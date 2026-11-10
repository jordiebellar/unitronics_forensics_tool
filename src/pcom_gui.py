import FreeSimpleGUI as sg
import time
from pcom_client import (
    PCOM_CLIENT,
    auto_detect_plc,
    dump_system_bits_csv,
    dump_system_integers_csv,
    read_memory,
    read_and_save_project_zip,
    upload_auth,
    dump_all_csv,
)



# LOG FUNCTION

def log(window, msg):
    """
    Prints output to log on GUI.

    :param window:
    :type window:
    :param msg:
    :type msg:
    """
    window["-LOG-"].print(msg)

# POP UP FUNCTIONS

def ask_password():
    """
    Popup a password input box.
    """
    pwd = sg.popup_get_text( "Enter upload password (8 chars):", title = "Password", password_char = "*", default_text = "********", )
    return pwd

def ask_memory_dump():
    """
    Popup an address and flag input box.
    """
    layout = [
        [sg.Text("Start address (hex): "), sg.Input("0x0", key = "-START-", size = (12, 1))],
        [sg.Text("End address (hex): "), sg.Input("0x100000", key = "-END-", size = (12, 1))],
        [sg.Text("Memory Flag: "), sg.Input("1", key = "-FLAG-", size = (12, 1))],
        [sg.Button("Start Dump"), sg.Button("Cancel")],
    ]

    win = sg.Window("Memory Dump", layout, modal = True)

    event, values = win.read()

    win.close()

    if event == "Start Dump":
        return values
    
    return None

def add_extension(path, extension):
    """
    Add a default extension when the selected save path has none.
    """
    if not path:
        return None
    if "." not in path.split("\\")[-1].split("/")[-1]:
        return f"{path}{extension}"
    return path

def ask_save_path(title, default_name, file_types, extension):
    """
    Popup an OS save-file dialog and normalize the selected filename.
    """
    filename = sg.popup_get_file(
        title,
        title = title,
        save_as = True,
        default_path = default_name,
        file_types = file_types,
        no_window = True,
    )
    return add_extension(filename, extension)

def main_gui():

    sg.theme("DarkGrey14")

    status_row = [
        sg.Text("Status: Scanning...", key = "-STATUS-", size = (58, 1)),
        sg.Checkbox("Debug mode", key = "-DEBUG-", default = False),
    ]

    info_frame = sg.Frame(
        "PLC Info",
        [[
            sg.Button("PLC Name", size = (15, 2)),
            sg.Button("Firmware", size = (15, 2)),
            sg.Button("Unit ID", size = (15, 2)),
            sg.Button("Signature Table", size = (15, 2)),
        ]],
    )

    download_frame = sg.Frame(
        "Downloads",
        [
            [
                sg.Button("Save Project ZIP", key = "Read Project ZIP", size = (18, 2)),
                sg.Button("Save Memory Dump", key = "Memory Dump", size = (18, 2)),
            ],
            [
                sg.Button("Save SI CSV", key = "System Integers CSV", size = (18, 2)),
                sg.Button("Save SB CSV", key = "System Bits CSV", size = (18, 2)),
                sg.Button("Dump All CSVs", key = "Dump All CSVs", size = (18, 2)),
            ],
        ],
    )

    control_frame = sg.Frame(
        "Controls",
        [[
            sg.Button("Check Password", size = (18, 2)),
            sg.Button("STOP PLC", size = (18, 2), button_color = ("white", "red")),
        ]],
    )

    log_row = [ sg.Multiline( size = (78, 22), key = "-LOG-", disabled = True, autoscroll = True, font = ("Courier New", 10), )]
            

    layout = [
        status_row,
        [info_frame],
        [download_frame],
        [control_frame],
        log_row,
    ]

    ser = None
    pcom = None
    window = sg.Window("PCOM Terminal", layout, finalize = True, resizable = True)
    
    def gui_out(msg):
        log(window, msg)
        window.refresh()

    window.refresh()

    result = auto_detect_plc(log_fn = gui_out)

    if result is None: 
        window["-STATUS-"].update("No PLC Found")
        for btn in ["PLC Name","Firmware","Unit ID","Signature Table", "Read Project ZIP","Memory Dump","System Integers CSV","System Bits CSV","Check Password","STOP PLC"]:
            window[btn].update(disabled = True)
    else:
        ser, pcom = result 
        pcom.out = gui_out
        window["-STATUS-"].update(f"Connected: {ser.port} AT {ser.baudrate} baud")

    # EVENT LOOP

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        if pcom:
            pcom.debugMode = values["-DEBUG-"]

        if event == "PLC Name":
            ser.write(pcom.create_read_plc_name())
            resp = ser.read(1024 * 5)
            name = pcom.parse_read_plc_name(resp)

            if name:
               log(window, f"[-] PLC Name: {name.decode('windows-1252', errors = 'replace')}")
            else:
                log(window, "[X] Could not read PLC name.")

        elif event == "Firmware":
            ser.write(pcom.create_read_plc_versions())
            resp = ser.read(1024 * 5)
            fw = pcom.parse_version(resp)

            if isinstance(fw, dict):
                log(window, f"[-] Model: {fw.get('model_desc', 'Unknown')}")
                log(window, f"[-] HW Rev: {fw.get('hw_rev', 'Unknown')}")

                for v in fw.get("fw_ver", []):
                    label = PCOM_CLIENT.FW_TYPE_TO_NAME.get(v.get("type"), v.get("type"))
                    log(window, f"[-] {label}: {v.get('version')}")
            else:
                log(window, f"[-] Unknown model: {fw}")

        elif event == "Unit ID":
            ser.write(pcom.create_read_unitID())
            resp = ser.read(1024 * 5)
            unit_id = pcom.parse_read_unitID(resp)
            log(window, f"[-] Unit ID: {unit_id.decode('windows-1252', errors = 'replace')}")

        elif event == "Signature Table":
            from pcom_client import print_signature_table
            log(window, "[-] Reading signature table...")
            try:
                print_signature_table(ser, pcom, log_fn = gui_out)
                log(window, "[-] Signature table complete.")
            except Exception as e:
                log(window, f"[X] Error reading signature table: {e}")
                
        elif event == "Read Project ZIP":
            default_name = f"project_{int(time.time())}.zip"
            filename = ask_save_path(
                "Save project ZIP",
                default_name,
                (("ZIP files", "*.zip"), ("All files", "*.*")),
                ".zip",
            )
            if filename:
                log(window, "[-] Reading project ZIP from PLC...")
                try:
                    saved = read_and_save_project_zip(ser, pcom, filename = filename, out = gui_out)
                    log(window, f"[-] Saved project ZIP to: {saved}")
                except Exception as e:
                    log(window, f"[X] Failed to read project ZIP: {e}")
            else:
                log(window, "[-] Project ZIP save cancelled.")

        elif event == "Memory Dump":
            params = ask_memory_dump()
            if params:
                try: 
                    start = int(params["-START-"], 0)
                    end = int(params["-END-"], 0)
                    flag = int(params["-FLAG-"], 0)
                    
                    if end <= start:
                        log(window, "[X] End address must be greater than start address.")
                    else:
                        default_name = f"ram_{hex(start)}_{hex(end)}_flag_{flag}_{int(time.time())}.bin"
                        filename = ask_save_path(
                            "Save memory dump",
                            default_name,
                            (("Binary files", "*.bin"), ("All files", "*.*")),
                            ".bin",
                        )
                        if filename:
                            log(window, f"[-] Dumping {hex(start)}..{hex(end)} flag = {flag}...")
                            saved = read_memory(ser, pcom, loc_type = flag, start = start, end = end, filename = filename, out = gui_out)
                            log(window, f"[-] Saved a dump to: {saved}")
                        else:
                            log(window, "[-] Memory dump save cancelled.")
                except ValueError:
                    log(window, "[X] Invalid address")
                except Exception as e:
                    log(window, f"[X] Memory dump failed: {e}")

        elif event == "System Integers CSV":
            default_name = f"si_dump_{int(time.time())}.csv"
            filename = ask_save_path(
                "Save System Integers CSV",
                default_name,
                (("CSV files", "*.csv"), ("All files", "*.*")),
                ".csv",
            )
            if filename:
                try:
                    saved = dump_system_integers_csv(ser, pcom, filename = filename, out = gui_out)
                    log(window, f"[-] Saved System Integers CSV to: {saved}")
                except Exception as e:
                    log(window, f"[X] Failed to save System Integers CSV: {e}")
            else:
                log(window, "[-] System Integers CSV save cancelled.")

        elif event == "System Bits CSV":
            default_name = f"sb_dump_{int(time.time())}.csv"
            filename = ask_save_path(
                "Save System Bits CSV",
                default_name,
                (("CSV files", "*.csv"), ("All files", "*.*")),
                ".csv",
            )
            if filename:
                try:
                    saved = dump_system_bits_csv(ser, pcom, filename = filename, out = gui_out)
                    log(window, f"[-] Saved System Bits CSV to: {saved}")
                except Exception as e:
                    log(window, f"[X] Failed to save System Bits CSV: {e}")
            else:
                log(window, "[-] System Bits CSV save cancelled.")

        elif event == "Dump All CSVs":
            folder = sg.popup_get_folder("Choose output folder for CSV dump", title = "Dump All CSVs")
            if folder:
                import os
                subfolder = os.path.join(folder, f"dump_{int(time.time())}")
                log(window, f"[-] Dumping all operands to {subfolder}...")
                try:
                    dump_all_csv(ser, pcom, folder = subfolder, out = gui_out)
                except Exception as e:
                    log(window, f"[X] Dump All CSVs failed: {e}")
            else:
                log(window, "[-] Dump All CSVs cancelled.")

        elif event == "Check Password":
            pwd = ask_password()
            if pwd:
                try:
                    ok = upload_auth(ser, pcom, password = pwd, out = gui_out)
                    if ok: 
                        log(window, "[-] Password: OK - upload authorized.")
                    else:
                        log(window, "[X] Password: BAD - upload not authorized.")
                except Exception as e:
                    log(window, f"[X] Password check failed: {e}")

        elif event == "STOP PLC":
            confirm = sg.popup_yes_no(
                "This will STOP the PLC.\nAre you sure?",
                title="Confirm STOP"
            )
            if confirm == "Yes":
                try:
                    req = pcom.create_stop_command()
                    ser.write(req)
                    resp = ser.read(1024 * 5)
                    log(window, "[!] STOP command sent to PLC.")
                except Exception as e:
                    log(window, f"[X] Stop command failed: {e}")
            else:
                log(window, "[-] Stop cancelled.")
    window.close()
    if ser:
        ser.close()

if __name__ == "__main__":
    main_gui()
