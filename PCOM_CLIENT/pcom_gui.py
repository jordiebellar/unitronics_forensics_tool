import FreeSimpleGUI as sg
from pcom_client import PCOM_CLIENT, auto_detect_plc, upload_auth, read_memory, read_and_save_project_zip



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

def main_gui():

    sg.theme("DarkGrey14")

    status_row = [sg.Text("Status: Scanning...", key = "-STATUS-", size = (50, 1))]

    button_row1 = [
        sg.Button("PLC Name", size = (14, 2)),
        sg.Button("Firmware", size = (14, 2)),
        sg.Button("Unit ID", size = (14, 2)),
        sg.Button("Signature Table", size = (14, 2)),

        ]

    button_row2 = [
        sg.Button("Read Project ZIP", size = (14, 2)),
        sg.Button("Memory Dump", size = (14, 2)),
        sg.Button("Check Password", size = (14, 2)),
        sg.Button("STOP PLC", size = (14, 2), button_color = ("white", "red")),
        
        ]

    log_row = [ sg.Multiline( size = (70, 20), key = "-LOG-", disabled = True, autoscroll = True, font = ("Courier New", 10), )]

    debug_row = [sg.Checkbox("Debug mode", key = "-DEBUG-", default = False)]
            

    layout = [
        status_row,
        button_row1,
        button_row2,
        log_row,
        debug_row,
    ]

    window = sg.Window("PCOM Terminal", layout, finalize = True, resizable = True)

    window.refresh()

    result = auto_detect_plc(log_fn = lambda msg: log(window, msg))

    if result is None: 
        window["-STATUS-"].update("No PLC Found")
        for btn in ["PLC Name","Firmware","Unit ID","Signature Table", "Read Project ZIP","Memory Dump","Check Password","STOP PLC"]:
            window[btn].update(disabled = True)
    else:
        ser, pcom = result 
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
                print_signature_table(ser, pcom, log_fn = lambda msg: log(window, msg))
                log(window, "[-] Signature table complete.")
            except Exception as e:
                log(window, f"[X] Error reading signature table: {e}")
                
        elif event == "Read Project ZIP":
            log(window, "[-] Reading project ZIP from PLC...")
            try:
                filename = read_and_save_project_zip(ser, pcom)
                log(window, f"[-] Saved project ZIP to: {filename}")
            except Exception as e:
                log(window, f"[X] Failed to read project ZIP: {e}")

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
                        log(window, f"[-] Dumping {hex(start)}..{hex(end)} flag = {flag}...")
                        filename = read_memory(ser, pcom, loc_type = flag, start = start, end = end)
                        log(window, f"[-] Saved a dump to: {filename}")
                except ValueError:
                    log(window, "[X] Invalid address")
                except Exception as e:
                    log(window, f"[X] Memory dump failed: {e}")

        elif event == "Check Password":
            pwd = ask_password()
            if pwd:
                try:
                    ok = upload_auth(ser, pcom, password = pwd)
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