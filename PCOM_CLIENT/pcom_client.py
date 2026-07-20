import serial
import time
import zlib
import socket
import re
import binascii
import struct
import sys
import datetime
import time
import random
import csv
from io import BytesIO
from serial.tools import list_ports

WARNING = "\033[93m"  # Yellow color
ENDC = "\033[0m"      # Reset color
RESOURCE_ID_PROJECT_ZIP = 6
PASSWORD_DEFAULT = "*"*8

# SYSTEM OPERAND MAPS

# SYSTEM BIT MAP

SB_MAP = {
    0: 'Always 0',
    1: 'Always 1',
    2: 'Power-up bit',
    3: '1 second pulse ( a squarewave of 1 second duration, with a 50% duty cycle)',
    4: 'Divide by zero',
    5: 'Short circuits in loads linked to transistor Outputs on snap-in/expansion I/O modules',
    6: 'Keyboard is active',
    7: '100 mS pulse',
    8: 'Battery low (1=low)',
    9: 'Ram Failure',
    10: 'Result of Float operation is illegal (Reset by user)',
    13: 'ON at Rising Edge of SB3 (1sec pulse)',
    14: 'Request to calculate current PLC temperature (not supported by V120, V130, V350)',
    15: 'ON at Rising Edge of SB7 (100 mS pulse)',
    16: 'Touchscreen is Active (has been touched] (Touch models only)',
    17: 'Enable/Disable Touch-screen indication (Message Board function)',
    22: 'Enable Virtual Keyboard (Relevant only to Standard Vision + Touchscreen, not Enhanced)',
    23: 'Enable all HMI keys during Keypad Entry',
    24: 'Initialize and Reset PLC (Set to cause PLC Reset and to Initialize all operands to 0)',
    25: 'Use operand value as Index of HMI variable',
    26: 'Exiting OS Draw Mode ( ON for 1 cycle after OS draw)',
    27: 'Disable all keypad automation (V280 only)',
    28: 'LCD: controlled by OS (OS Drawing)',
    29: 'Current keypad entry sets SB 30 (HMI keypad entries complete)',
    30: 'Keypad Vars Locked(Standard: OS turns ON after entries complete (V130: User turns ON/OFF)',
    31: 'Refresh current LCD screen display variables',
    32: 'HMI keypad entry in progress (Standard Vision)',
    33: 'Load Disply + linked Call Sub-ON 1 scan 1st time the Sub runs (Standard Vision)',
    34: 'UnLoad Disply w/linked Call Sub-ON 1 scan last time Sub runs (Standard Vision)',
    35: 'OnLine Test Point',
    36: 'INFO mode',
    37: 'Exclude Last Viewed Display from FIFO',
    38: 'Invert Touchscreen element pixels (Text, images) (V280/290-BW)',
    39: 'FLASH on LCD, Display not Refreshed (V570, 290-C)',
    40: 'Key: # 0',
    41: 'Key: # 1 (also Up arrow for V120)',
    42: 'Key: # 2',
    43: 'Key: # 3',
    44: 'Key: # 4',
    45: 'Key: # 5',
    46: 'Key: # 6  (also Down arrow for V120)',
    47: 'Key: # 7',
    48: 'Key: # 8',
    49: 'Key: # 9',
    50: 'Plus/Minus',
    51: 'Left Arrow',
    52: 'Right Arrow',
    53: 'ENTER',
    54: 'Key <i>',
    55: 'Up',
    56: 'Down',
    57: 'ESC',
    58: 'F1',
    59: 'F2',
    60: 'F3',
    61: 'F4',
    62: 'F5',
    63: 'F6',
    64: 'F7',
    65: 'F8',
    66: 'F9',
    67: 'F10',
    68: 'F11',
    69: 'F12',
    70: 'F13',
    71: 'F14',
    72: 'F15',
    73: 'Disable HMI cursor blinking (Standard) Calibrate Touchscreen (touchscreen models)',
    75: 'Download Complete, PLC and HMI application',
    76: 'Keypad Entry: Focus (V130/350/570)',
    77: 'Modem Busy (Enhanced Vision: COM 1) (Standard Vision: the COM linked to modem)',
    78: 'Modem Busy, COM Port 2 (V570, 290-C)',
    79: 'Modem Busy, COM Port 3 (V570, 290-C)',
    80: 'Modem Init :COM 1',
    81: 'Modem Init: Fail  1',
    82: 'Modem Init: COM 2',
    83: 'Modem Init Fail: COM 2',
    84: 'Modem Init: COM 3',
    85: 'Modem Init Fail: COM 3',
    86: 'Modem Connected: Com Port 1',
    87: 'Modem Connected: COM 2',
    88: 'Modem Connected: COM3',
    89: 'CLIP - Caller Number is here',
    91: 'I/O Exp. Module--Command buffer is full',
    92: 'Keypad Entry in Progress (ON during entry) (Enhanced Vision)',
    93: 'Keypad Entry Var Activates (ON for 1 scan) (Enhanced Vision)',
    94: 'Keypad Entry Var Complete (ON for 1 scan) (Enhanced Vision)',
    100: 'GPRS modem connected (TC 65)',
    102: 'MODBUS Read Long: Transpose',
    104: 'Enable MODBUS over GPRS: COM1. Set before MODBUS Configuration.',
    105: 'Enable MODBUS over GPRS: COM2. Set before MODBUS Configuration.',
    106: 'Enable MODBUS over GPRS: COM3. Set before MODBUS Configuration.',
    108: 'Press "Enter" 1x (V130) When SB 108 + 76 ON, KP entry requires Enter pressed once',
    109: 'V130 only. Arrow keys tab between keypad entry fields: 0 = Left/Right, 1= Up/Down',
    110: 'Draw: Out of Range',
    111: 'Disable Virtual Keypad. ON=Virtual Keypad is disabled but Keypad enabled (Vision560)',
    112: 'On-Board USB port found',
    113: 'USB cable - connected to PC (set to "1" when connected. Relevant models only)',
    115: 'V130 only: Keypad keys, letters/number order.  0=abc2, def3, etc(default) 1=2abc, 3def, etc',
    116: 'SD Trends to SD: Set to Overwrite .utr',
    117: 'SD Trends: Jump to next segment',
    118: 'SD Trends: Jump to previous segment',
    119: 'SD Trends: System busy - Draw Trend is gathering data',
    120: 'DTR COM Port 1 (signal output from PLC)',
    121: 'DSR COM Port 1 (signal input to PLC)',
    122: 'DTR COM Port 2 (signal output from PLC)',
    123: 'DSR COM Port 2 (signal input to PLC)',
    124: 'DTR COM Port 3 (signal output from PLC)',
    125: 'DSR COM Port 3 (signal input to PLC)',
    132: 'COM Port 1, Data Transmission',
    133: 'COM Port 2, Data Transmission',
    134: 'COM Port 3, Data Transmission',
    135: 'COM Port 1, Data Receive',
    136: 'COM Port 2, Data Receive',
    137: 'COM Port 3, Data Receive',
    140: 'Remote access - read only',
    141: 'Ethernet: Card Exists',
    142: 'Ethernet: Card Initialized',
    143: 'Ethernet: Socket 0 Initialized (not relevant for V700)',
    144: 'Ethernet: Socket 1 Initialized (not relevant for V700)',
    145: 'Ethernet: Socket 2 Initialized (not relevant for V700)',
    146: 'Ethernet: Socket 3 Initialized (not relevant for V700)',
    147: 'Ethernet: Socket 0 Connected (not relevant for V700)',
    148: 'Ethernet: Socket 1 Connected (not relevant for V700)',
    149: 'Ethernet: Socket 2 Connected (not relevant for V700)',
    150: 'Ethernet: Socket 3 Connected (not relevant for V700)',
    151: 'Ethernet Status: Link',
    152: 'Ethernet Status: Rate, 10 mbps',
    153: 'Ethernet Status: Rate, 100 mbps',
    154: 'Ethernet Status: Collision',
    155: 'Ethernet Socket 0: Send in Progress (not relevant for V700)',
    156: 'Ethernet Socket 1: Send in Progress (not relevant for V700)',
    157: 'Ethernet Socket 2: Send in Progress (not relevant for V700)',
    158: 'Ethernet Socket 3: Send in Progress (not relevant for V700)',
    159: 'Enable UDP Unicast in Socket 0',
    162: 'Link failed after card was properly initialized',
    167: 'Error detected on ETHERNET',
    168: 'To activate "Link lost, auto-recover": Set SB 168 (Power-up Value =1)',
    177: 'Snap I/O Module Installed | 1=Snap Installed| 0=Snap is Not Installed',
    178: 'Profibus Card found',
    180: 'COM1 Received Message Invalid, STX/ETX/Checksum (V570, 290-C,130)',
    181: 'COM2 Received Message Invalid, STX/ETX/Checksum (V570, 290-C,130)',
    182: 'COM3 Received Message Invalid, STX/ETX/Checksum (V570, 290-C,130)',
    184: 'SMS: TX Success (Standard: any COM linked to Modem) (Enhanced: Modem on COM1)',
    185: 'SMS: TX Failed, (Standard: any COM linked to Modem) (Enhanced: Modem on COM1)',
    186: 'SMS: TX Success, COM2 (ACK) (Enhanced only)',
    187: 'SMS: TX Failed, COM2 (NACK) (Enhanced only)',
    188: 'SMS: TX Succeeded COM3 (ACK) (Enhanced only)',
    189: 'SMS: TX Failed, COM3 (NACK) (Enhanced only)',
    198: 'SMS Arrived, Record the Received SMS Message Length in SI 198',
    199: 'Save SMS to Memory Vector',
    200: 'CANbus Network operand',
    201: 'CANbus Network operand',
    202: 'CANbus Network operand',
    203: 'CANbus Network operand',
    204: 'CANbus Network operand',
    205: 'CANbus Network operand',
    206: 'CANbus Network operand',
    207: 'CANbus Network operand',
    208: 'CANbus Network operand',
    209: 'Customer ID',
    210: 'CANbus Network operand',
    211: 'CANbus Network operand',
    212: 'CANbus Network operand',
    213: 'CANbus Network operand',
    214: 'CANbus Network operand',
    215: 'CANbus Network operand',
    217: 'SD Card Present',
    218: 'SD Card is Write-Enabled',
    219: 'SD: No Pending Tasks (SD Card may be Ejected)',
    226: 'CANopen COB-ID mask (Enhanced Vision only)',
    236: 'CANbus Network communication error',
    237: 'CANbus ISC Network disable',
    240: 'CANopen: Configuration downloaded',
    241: 'CANopen: Configured',
    242: 'CANopen: SDO in Progress',
    243: 'CANopen: SDO transfer failed',
    249: 'Black Background, when Sys screen (Alarm,Info) does not stretch across screen.Enhanced',
    250: 'HMI keypad entry within limits (Standard Vision)',
    251: 'Keypad entry exceeds limits  (Standard Vision)',
    252: 'EX-RC1, Control Bus COMM LED| Use SB in program to control the LED to signal EX-RC1 - OPLC communication failure.',
    253: 'EX-RC1 - I/Os COM Error| ON at communication failure between EX-RC1 - I/Os',
    254: 'EX-RC1: Reset all outputs| Turn SB ON to reset all outputs. Controlled by user.',
    255: 'Init Expansion I/O failed.',
    279: 'Send SMS message in ASCII format (ON sends ASCII)',
    280: 'Force Message Display on Cell Phone',
    281: 'GPRS Server is on-line (COM1)',
    282: 'GPRS Server is on-line (COM2)',
    283: 'GPRS Server is on-line (COM3)',
    284: 'Send PDO1 (ON when SI 212 =8)',
    285: 'Send PDO2 (ON when SI 213 =8)',
    286: 'Send PDO3 (ON when SI 214 =8)',
    287: 'Send PDO4 (ON when SI 215 =8)',
    288: 'RTR PDO1 (ON when SI 216 =12)',
    289: 'RTR PDO2 (ON when SI 217 =12)',
    290: 'RTR PDO3 (ON when SI 218 =12)',
    291: 'RTR PDO4 (ON when SI 219 =12)',
    292: 'Send NMT MC (ON when SI 221 =8)',
    293: 'Send RTR NMT (ON when SI 222 =12)',
    300: 'Reset PLC',
    301: 'PLC exits Stop and returns to Run Mode; turns ON for 1 scan',
    302: 'Stop Mode ON, turns ON when entering Stop Mode, OFF when exists to Run Mode',
    303: 'Backup Security in Memory',
    305: 'Restrict MODBUS Master Access to MB & SI arrays specified via SIs 165-168, Vision Enhanced + Samba',
    310: 'Buzzer (290/570/350/530)',
    311: 'Buzzer - Screen Touch (Touchscreen models only)',
    314: 'Block PC access to PLC. OFF by default. When ON: access via VisiLogic, RA, etc. blocked',
    324: 'SD: Open File (Read to SD) Status: SI 67',
    325: 'SD File: Read Chunk in Progress (Chunk= 512 bytes)',
    326: 'SD Read File :EOF, entire file has been read',
    327: 'SD: Open File (Write to SD) Status : SI 67',
    328: 'SD File: Write Chunk in Progress (Chunk= 512 bytes)',
    329: 'SD Write File: EOF, entire file has been read',
    330: 'Break from External Device, COM1',
    331: 'Break from External Device, COM2',
    332: 'Break from External Device, COM3',
    334: 'GPRS Active, COM Port 1',
    335: 'GPRS Active, COM Port 2',
    336: 'GPRS Active, COM Port 3',
    337: 'Modem Break: COM Port 1(V570, 290-C)',
    338: 'Modem Break: COM Port 2 (V570, 290-C)',
    339: 'Modem Break: COM Port 3 (V570, 290-C)',
    340: 'Log to SD in Progress',
    341: 'Copy Data Table from PLC to SD Card in Progress',
    342: 'Copy Data Table from SD Card to PLC in Progress',
    343: 'SD: File Report in Progress',
    344: 'SD: Write .csv delimited line to SD in Progress',
    345: 'Email Send in Progress',
    346: 'SD Data Block 0 Busy',
    347: 'SD Data Block 1 Busy',
    348: 'SD Data Block 2 Busy',
    349: 'SD Data Block 3 Busy',
    350: 'Show Alarms on LCD (ON=Show, OFF=Hide)',
    351: 'Exit Alarm - Jump to Display',
    352: 'SD: Write Alarm History to SD (OFF by default)',
    358: 'SD: Delete File in Progress',
    359: 'Folder Report Function in Progress',
    366: 'Clone in Progress. Note that the process can take from several seconds to several minutes',
    372: 'Burn DLUs to Flash |OFF by Default| Turn ON to burn DLUs to Flash| Reset by PLC after burn.',
    399: 'Ladder Utility Failure. When ON, the number of the failed utility is in SI 26.',
    500: 'User RAM overlap warning',
    501: 'Retain Inputs Forced Value after power failure',
}

# SYSTEM INTEGER MAP

SI_MAP = {
    0: 'Scan Time, Resolution: Units of 1 mSec',
    6: 'Current key pressed (V120/130/230/260/280)',
    7: 'LCD Contrast Control: (V120/280/290 only) 0=Min. Contrast, 50=Med. Contrast, 100=Max. Contrast',
    8: 'Unit ID',
    9: 'LCD Backlight intensity',
    14: 'Current PLC temperature, including decimal point (not supported by V120, V130, V350)',
    26: 'Ladder Utility Failure Indication. (SB399 ON & utility fails, SI 26 indicates utility #)',
    30: 'Current second - according to RTC (SS)',
    31: 'Current time - according to RTC (HHMM)',
    32: 'Current date - according to RTC (DDMM)',
    33: 'Current year - according to RTC (YYYY)',
    34: 'Current day - according to RTC (1-7)',
    35: 'RTC Current Hour 0-23',
    36: 'RTC Current Minute, 0-59',
    37: 'RTC Day in Month (30 = 30th day in month)',
    38: 'RTC Current Month',
    40: 'Touchscreen is being touched - X coordinates',
    41: 'Touchscreen is being touched - Y coordinates',
    42: 'Active Keypad Entry variable, contains number of active var. Write to activate another var.',
    45: 'Numeric Key Entry Out of Limit - Counter of Attempts (Enhanced)',
    46: 'Refresh HMI (units 10 msec), Buttons, Frame, Text (V570, V290-C)',
    49: 'Select Touch Keyboard Type (enhanced only)',
    50: 'INFO delay time (default 4 seconds)',
    51: 'Info Mode, Serial COM Monitor: # of messages not displayed, V570 only',
    58: 'Email file attachment size, where 1=1024 bytes (power-up default is 1) Maximum = 10 (10 MB)',
    59: 'Send e-mail: Increase Timeout (resolution=10 ms)',
    63: 'Maximum number of Trend files that can be saved (read-only)',
    64: 'Maximum number of DT files that can be saved (read-only)',
    66: 'SD Card Status Messages',
    67: 'SD Card, Read Files: Status (0=no error)',
    68: 'SD Card, Write Files: Status (0=no error)',
    69: 'SD Card: File Open Time (may signal file fragmentation)',
    73: 'String Library Error',
    74: 'Alarms Utility, General Status',
    75: 'Operand assignment error (V570, 290-C)',
    76: 'Number of Alarms currently in History Buffer',
    80: 'Modem Status: COM 1',
    81: 'Error Code: COM 1',
    82: 'Modem Status: COM 2',
    83: 'Error Code: COM 2',
    84: 'Modem Status: COM 3',
    85: 'Error Code: COM 3',
    100: 'Maximum Time Delay between characters (units 2.5ms) MODBUS + Modem',
    101: 'TCP/IP Retries base time out',
    102: 'TCP/IP Retries count',
    103: 'Socket 0 TCP/IP Keep Alive (units of 100 msec)',
    104: 'Socket 1 TCP/IP Keep Alive (units of 100 msec)',
    105: 'Socket 2 TCP/IP Keep Alive (units of 100 msec)',
    106: 'Socket 3 TCP/IP Keep Alive (units of 100 msec)',
    107: 'TCP/IP Keep Client (Master) Connection (Socket 0)',
    108: 'TCP/IP Keep Client (Master) Connection (Socket 1)',
    109: 'TCP/IP Keep Client (Master) Connection (Socket 2)',
    110: 'TCP/IP Keep Client (Master) Connection (Socket 3)',
    115: 'Current Protocol COM1: 0=PCOM, 1=MODBUS, 2=FB Protocol, 3=SMS',
    117: 'Current Protocol COM3: 0=PCOM, 1=MODBUS, 2=FB Protocol, 3=SMS',
    118: 'CANbus: Record CAN messages to Data Table. Enhanced Vision only.',
    119: 'CANbus: CAN message currently being written to Data Table. (read-only)',
    136: 'PCOM_LAST_MESSAGE_KEY',
    140: 'Ethernet send fail, bitmap',
    141: 'Eth Socket 0: 0=PCOM, 1=Modbus, 2=RIO, 3=FB Protocol',
    142: 'Eth Socket 1: 0=PCOM, 1=Modbus, 2=RIO, 3=FB Protocol',
    143: 'Eth Socket 2: 0=PCOM, 1=Modbus, 2=RIO, 3=FB Protocol',
    144: 'Eth Socket 3: 0=PCOM, 1=Modbus, 2=RIO, 3=FB Protocol',
    145: 'Ethernet Socket 0: State (not relevant for V700)',
    146: 'Ethernet Socket 1: State (not relevant for V700)',
    147: 'Ethernet Socket 2: State (not relevant for V700)',
    148: 'Ethernet Socket 3: State (not relevant for V700)',
    165: 'Restrict MODBUS Access to MB Array: Start Address (use with SB 305)',
    166: 'Restrict MODBUS Access to MB Array: End Address (use with SB 305)',
    167: 'Restrict MODBUS Access to MI Array: Start Address (use with SB 305)',
    168: 'Restrict MODBUS Access to MI Array: End Address (use with SB 305)',
    185: 'GSM Signal Quality (Standard: all ports)(Enhanced: COM1)',
    188: 'GSM Signal Quality COM2 (V570, 290-C)',
    191: 'GSM Signal Quality COM3 (V570, 290-C)',
    198: 'Received SMS Message Length (in bytes)',
    199: 'SMS to Memory Vector - start of vector',
    200: 'CANbus Network operand',
    201: 'CANbus Network operand',
    207: 'UMI Command Number - use this to send a command to the UMI module',
    209: 'Customer ID',
    212: 'CANopen: Number of PDO1 waiting to be sent (buffer maximum=8)',
    213: 'CANopen: Number of PDO2 waiting to be sent (buffer maximum=8)',
    214: 'CANopen: Number of PDO3 waiting to be sent (buffer maximum=8)',
    215: 'CANopen: Number of PDO4 waiting to be sent (buffer maximum=8)',
    216: 'CANopen: Number of Send RTR PDO1 waiting to be sent (buffer maximum=8)',
    217: 'CANopen: Number of Send RTR PDO2 waiting to be sent (buffer maximum=8)',
    218: 'CANopen: Number of Send RTR PDO3 waiting to be sent (buffer maximum=8)',
    219: 'CANopen: Number of Send RTR PDO4 waiting to be sent (buffer maximum=8)',
    220: 'CANopen: Number of SDO waiting to be sent (buffer maximum=8)',
    221: 'CANopen: Number of Send NMT waiting to be sent (buffer maximum=8)',
    222: 'CANopen: Number of Send RTR NMT waiting to be sent (buffer maximum=12)',
    223: 'CANopen: Send Buffer full (per type. Check Help for bitmap)',
    224: 'CANopen: Number of received SDO messages',
    225: 'CANopen: SDO status (Codes in Help file)',
    236: 'CANbus Network communication error code',
    237: 'CANbus Network: failed unit ID',
    240: 'CANbus error bitmap, indicates PLC ID number',
    241: 'CANbus error bitmap, indicates PLC ID number',
    242: 'CANbus error bitmap, indicates PLC ID number',
    243: 'CANbus error bitmap, indicates PLC ID number',
    244: 'V1040, X Coordinates, Num Keypad/Alarm screen',
    245: 'V1040, Y Coordinates, Num Keypad/Alarm screen',
    246: '(V1210/V1040 only) Improve Display of Complex HMI elements (1-30)',
    249: 'Last Active Keypad Entry Var (Standard Vision)',
    250: 'Currently active keypad entry (read/write) (Standard Vision)',
    251: 'Previous HMI Display Number (Standard Vision only)',
    252: 'Current HMI Display Number (Standard Vision only)',
    253: 'Password: Info Mode',
    274: 'COM1, Received Message Counter, Serial',
    275: 'COM2, Received Message Counter, Serial',
    276: 'COM3, Received Message Counter, Serial',
    280: 'Number of minutes - counts constantly unless initialised by user. When register is full, OS inits',
    281: '2.5mS Subroutine - actual duration of subroutine (resolution 10microS)',
    282: '2.5mS Subroutine + related tasks = total execution time for Subroutine (resolution 10microS)',
    286: 'Servo 1 CANopen send retry counter',
    287: 'Servo 2 CANopen send retry counter',
    288: 'Servo 3 CANopen send retry counter',
    330: 'SD: Copy DT from PLC to SD - Total Amount of Data to be Copied (blocks of 512 bytes)',
    331: 'SD: Copy DT from PLC to SD - Blocks that have been copied',
    333: 'SD: Copy DT from SD to PLC - Remaining Amount (blocks not yet copied)',
    440: 'Float errors (check Help for error codes)',
    491: 'Switch current Text Library',
    492: 'Jump from Alarm x to HMI Display',
    497: 'Firmware Build Number (V120, V230, V260, V280, V290 BW)',
    498: 'Firmware Version Number (V120, V230, V260, V280, V290 BW)',
}

# HELPER FUNCTIONS

def tx(d: bytes) -> str:
    """
    Convert raw bytes into a printable lowercase hex string.
    
    :param d: raw bytes
    :type d: bytes
    :return: hex-encoded string
    :rtype: str
    """
    return binascii.hexlify(d).decode()

def up_I(r: BytesIO) -> int:
    """
    Read a 4-byte integer from a bit stream.
    
    :param r: a file-like object
    :type r: BytesIO
    :return: unsigned integer parsed from the 4 bytes
    :rtype: int
    """
    return struct.unpack("<I", r.read(4))[0]

def dex(d: str) -> bytes:
    """
    Convert a hex string into raw bytes.
    
    :param d: hex string
    :type d: str
    :return: decoded bytes
    :rtype: bytes
    """
    return binascii.unhexlify(d)

def print_body_info(key: str, info, out = print) -> None:
    """
    Print a labeled field.
    
    :param key: label to print
    :type key: str
    :param info: field value to print
    """
    if info:
        info_data = info
        try:
            if type(info_data) == bytes:
                info_data = info_data.decode("windows-1252")
        except Exception as e:
            info_data = info
        out(f"\t\t\t[-] {key}: {info_data}")
    else:
        out(f"\t\t\t[-] {key}")

# Port Scanner Functions:

def get_canidate_ports():
    """
    Returns a list of all available serial port device names.

    :return: list of port name strings, empty list if none are found
    :rtype: list[str]
    """
    return [p.device for p in list_ports.comports()]

def probe_port(port, baud, timeout = 0.25):
    """
    Attempts to open a serial port and verify if the PLC is connected.

    :param port: serial port device name
    :type port: str
    :param baud: baud rate to use when opening the port
    :type baud: int
    :param timeout: secondes to wait for a response before giving up
    :type timeout: float
    :return: tuple of (ser, pcom) if a PLC is found, None otherwise
    :rtype: tuple[serial.Serial, PCOM_CLIENT] | None
    """
    try:
        ser = serial.Serial(port, baud, timeout = timeout)
        pcom = PCOM_CLIENT(isTcp = False)

        request = pcom.create_read_plc_name()
        ser.write(request)

        data = ser.read(256)
        name = pcom.parse_read_plc_name(data)

        if name:
            return (ser, pcom)
        ser.close()
        return None
    except:
        return None

# Baud rates to test
BAUDS = [115200, 57600, 38400, 19200, 9600]

def auto_detect_plc(log_fn = None):
    """
    Scans all available serial ports and baud rates to find a connected PLC.

    :return: tuple of (ser, pcom) for the detected PLC, None if not found
    :rtype: tuple[serial.Serial, PCOM_CLIENT] | None
    """
    out = log_fn if log_fn else print

    ports = get_canidate_ports()

    if not ports:
        out("No serial ports found.")
        return None
    for port in ports:
        for baud in BAUDS:
            out(f"Trying {port} at {baud}")
            result = probe_port(port, baud)

            if result:
                out(f"Found PLC on {port} at {baud}")
                return result
    out("No PLC found")
    return None



# PCOM_CLIENT BUILDS AND PARSES PCOM MESSAGES

class PCOM_CLIENT:

    MODELS = { 'PRBT': 'FACTORY BOOT', '13PRBT': 'V130 FACTORY BOOT', '35PRBT': 'V350 FACTORY BOOT', '43PRBT': 'V430 FACTORY BOOT', '10PRBT': 'V1040/V1210 FACTORY BOOT', 'PC15': 'EXF-RC15 FACTORY BOOT', 'SM35PB': 'SM35-J FACTORY BOOT', 'SM43PB': 'SM43-J FACTORY BOOT', 'SM70PB': 'SM70-J FACTORY BOOT', 'SM7OPB': 'SM70-OEM FACTORY BOOT', '70PR': 'V700-T20BJ FACTORY BOOT', 'ADF1': 'ADP-PB1 FACTORY BOOT', 'BOOT': 'BOOT', 'CLBT': 'CLR BOOT', '13BOOT': 'V130 BOOT', '35BOOT': 'V350 BOOT', 'SM35BT': 'SM35-J BOOT', 'SM43BT': 'SM43-J BOOT', 'SM70BT': 'SM70-J BOOT', 'SM7OBT': 'SM70-OEM BOOT', 'SMBT': 'SM35 BOOT', '10BOOT': 'V1040 BOOT', '12BOOT': 'V1210 BOOT', '43BOOT': 'V430 BOOT', '70BOOT': 'V700-T20BJ BOOT', 'ADB1': 'ADP-PB1 BOOT', 'BM90': 'BOOT', 'BNX1': 'BOOT', 'BNR1': 'BOOT', 'BRC1': 'EX-RC1 BOOT', 'BC15': 'EXF-RC15 BOOT', 'B1': 'M90-19-B1', 'B1A': 'M90-19-B1A', 'R1': 'M90-R1', 'R1C': 'M90-R1-CAN', 'R2C': 'M90-R2-CAN', 'T': 'M90-T', 'T1': 'M90-T1', 'T1C': 'M90-T1-CAN', 'TA2C': 'M90-TA2-CAN', 'TA3C': 'M90-TA3-CAN', '1TC2': 'M91-19-TC2', '1UN2': 'M91-19-UN2', '1R1': 'M91-19-R1', '1R2': 'M91-19-R2', '1R2C': 'M91-19-R2C', '1T1': 'M91-19-T1', '1UA2': 'M91-19-UA2', '1T2C': 'M91-19-T2C', '7B1': 'M90-2-B1', '7B1A': 'M90-2-B1A', '7R1': 'M90-2-R1', '7R1C': 'M90-2-R1-CAN', '7R2C': 'M90-2-R2-CAN', '7T': 'M90-2-T', '7T1': 'M90-2-T1', '7T1C': 'M90-2-T1-CAN', '7TA2': 'M90-2-TA2-CAN', '7TA3': 'M90-2-TA3-CAN', '8TC2': 'M91-2-TC2', '8UN2': 'M91-2-UN2', '8R1': 'M91-2-R1', '8R2': 'M91-2-R2', '8R2C': 'M91-2-R2C', '8T1': 'M91-2-T1', '8UA2': 'M91-2-UA2', '8T38': 'M91-2-T38', '8T2C': 'M91-2-T2C', '8R6C': 'M91-2-R6C', '8R34': 'M91-2-R34', '8A19': 'M91-2-RA19', '8A22': 'M91-2-RA22', '1T38': 'M91-19-T38', 'JR14': 'BOSCH', 'JR17': 'JZ10-11-R17', 'JR10': 'JZ10-11-R10', 'JR16': 'JZ10-11-R16', 'JT10': 'JZ10-11-T10', 'JT17': 'JZ10-11-T17', 'JEW1': 'JZB2-11-EW1', 'JE10': 'JZB1-11-SE10', 'JR31': 'JZ10-11-R31', 'JT40': 'JZ10-11-T40', 'JP15': 'JZ10-11-PT15', 'JE13': 'JZ10-11-UE13', 'JA24': 'JZ10-11-UA24', 'JN20': 'JZ10-11-UN20', '8RZ': 'M91-2-R1-AZ1', '2320': 'V230-13-B20', '2620': 'V260-16-B20', '2820': 'V280-18-B20', '2920': 'V290-19-B20', 'VUN2': 'V120-12-UN2', 'VR1': 'V120-12-R1', 'VR2C': 'V120-12-R2C', 'VUA2': 'V120-12-UA2', 'VT1': 'V120-12-T1', 'VT40': 'V120-12-T40', 'VT2C': 'V120-12-T2C', 'VT38': 'V120-12-T38', 'WUN2': 'V120-22-UN2', 'WR1': 'V120-22-R1', 'WR2C': 'V120-22-R2C', 'WUA2': 'V120-22-UA2', 'WT1': 'V120-22-T1', 'WT40': 'V120-22-T40', 'WT2C': 'V120-22-T2C', 'WT38': 'V120-22-T38', 'WR6C': 'V120-22-R6C', 'WR34': 'V120-22-R34', 'WA19': 'V120-22-RA19', 'WA22': 'V120-22-RA22', 'ERC1': 'EX-RC1', '5320': 'V530-53-B20B', '49C3': 'V570-57-C30 / V290-19-C30', '57C3': 'V570-57-C30 / V290-19-C30', '49T3': 'V570-57-T34 / V290-19-T34', '57T3': 'V570-57-T34 / V290-19-T34', '49T2': 'V570-57-T20 / V290-19-T20', '57T2': 'V570-57-T20 / V290-19-T20', '49T4': 'V570-57-T40 / V290-19-T40', '57T4': 'V570-57-T40 / V290-19-T40', '56C3': 'V560-56-C30', '56T4': 'V560-56-T40', '56T3': 'V560-56-T34', '56T2': 'V560-56-T25B', '13TR22': 'V130-33-TRA22', '13XXXX': 'V130-33-XXXX', '13R2': 'V130-33-R2', '13R34': 'V130-33-R34', '13T2': 'V130-33-T2', '13T38': 'V130-33-T38', '13RA22': 'V130-33-RA22', '13TA24': 'V130-33-TA24', '13B1': 'V130-33-B1', '13T40': 'V130-33-T40', '13R6': 'V130-33-R6', '13TR34': 'V130-33-TR34', '13TR20': 'V130-33-TR20', '13TR6': 'V130-33-TR6', '13TU24': 'V130-33-TU24', '35R2': 'V350-35-R2', '35R34': 'V350-35-R34', '35T2': 'V350-35-T2', '35T38': 'V350-35-T38', '35RA22': 'V350-35-RA22', '35TA24': 'V350-35-TA24', '35B1': 'V350-35-B1', '35T40': 'V350-35-T40', '35R6': 'V350-35-R6', '35TR34': 'V350-35-TR34', '35TR22': 'V350-35-TRA22', '35TR20': 'V350-35-TR20', '35TR6': 'V350-35-TR6', '35TU24': 'V350-35-TU24', '35XXXX': 'V350-35-XXXX', 'S3T20': 'SM35-J-T20', 'S3TA2': 'SM35-J-R20', 'S3R20': 'SM35-J-R20', 'S4T20': 'SM43-J-T20', 'S4TA2': 'SM43-J-R20', 'S4R20': 'SM43-J-R20', '70T2': 'V700-T20BJ', 'EC15': 'EXF-RC15', '10T2': 'V1040', '12T2': 'V1210', 'ADP1': 'ADP-PB1'}
    FW_TYPE_TO_NAME = {'B':'O/S', 'P':'BOOT', 'F':'FactoryBoot', 'FT': 'BinLib'}
    binary_header_magic = b"/_OPLC" # start of packet marker for binary PCOM
    ascii_header_magic = b"/" # start of packet marker for ASCII PCOM
    binary_suffix = b"\\" # end character for binary PCOM
    ascii_suffix = b"\x0d" # end character for ASCII PCOM
    PCOM_TCP_HEADER_SIZE = 6 # header size when using TCP
    PCOM_HEADER_SIZE = 24 # PCOM binary header size
    PCOM_BINARY_FOOTER_SIZE = 3 # PCOM binary footer size
    current_tcp_id = 30412

# CONSTRUCTOR
    
    def __init__(self, isTcp: bool = False, debugMode: bool = False, out = print) -> None:
        """
        Create a PCOM client capable of building and parsing PCOM packets.
        
        :param isTcp: if True, wrap and unwrap packets using TCP header
        :type isTcp: bool
        :param debugMode: if True, print high-level descriptions of packets
        :type debugMode: bool
        """
        self.isTcp = isTcp
        self.debugMode = debugMode
        self.out = out
    
# PCOM_CLIENT HELPER FUNCTIONS

    def print_pcom_binary(self, data: bytes) -> None:
        """
        Pretty-print a summary of a binary PCOM packet.

        Determines packet direction by checking the opcodes MSB.
        
        :param data: full binary PCOM frame
        :type data: bytes
        """
        opcode_table = {
            b"\x01": "Read Memory Reqeust",
            b"\x81": "Read Memory Response",
            b"\x02": "Check Password",
            b"\x82": "Password OK",
            b"\x0c": "Get PLC Name Request",
            b"\x8C": "Get PLC Name Response",
            b"\x10": "Where Resource Reqeust",
            b"\x90": "Where Resource Response",
            b"\x16": "Translate Index to Address Request",
            b"\x96": "Translate Index to Address Response",
            b"\x1A": "Flash Memory Buffer Request",
            b"\x9A": "Flash Memory Buffer Response",
            b"\x41": "Write Memory Reqeust",
            b"\xC1": "Write Memory Response",
            b"\x4D": "Read Operand Request",
            b"\xCD": "Read Operand Response",
            b"\xFF": "Error",
        }
        opcode = data[12:13]
        opcode_message = opcode_table.get(opcode, "")
        if int.from_bytes(opcode, 'little') & 0b10000000:
            direction = "Client <--- Server"
        else:
            direction = "Client ---> Server"
        self.out(f"{direction}: Binary PCOM Command {opcode_message} ({hex(int.from_bytes(opcode, 'little'))})")
        self.out(data)
  
    def print_pcom_ascii(self, data: bytes) -> None:
        """
        Pretty print a summary of an ASCII PCOM packet.

        Checks for 'A' to know direction.
        
        :param data: full ASCII PCOM frame
        :type data: bytes
        """
        opcode_table = {
            b"ID": "Get PLC Version ",
            b"UG": "Get UnitID Command ",
            b"GF": "Read Integers ",
            b"GS": "Read Bits ",
            b"SF": "Write Integers ",
            b"SS": "Write Bits",
            b"CCS": "Stop PLC "
        }
        if data[0:2] == b"/A":
            direction = "Client (EWS) <--- Server (PLC)"
            type_of_msg = "Response"
            opcode = data[4:6]
        else:
            direction = "Client (EWS) ---> Server (PLC)"
            type_of_message = "Request"
            opcode = data[3:5]
        
        opcode_message = opcode_table.get(opcode, "")
        self.out(f"{direction}: ASCII PCOM Command {opcode_message} ({opcode.decode()})")
        self.out(data)

    def extract_pcom_data(self, data: bytes) -> bytes:
        """
        Extract the payload from a binary PCOM response frame.
        
        :param data: raw bytes received from the PLC
        :type data: bytes
        :return: the payload bytes between header and footer
        :rtype: bytes
        """

        # Move after the PCOM/TCP header

        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        if self.debugMode:
            self.print_pcom_binary(data)
        return data[self.PCOM_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]

    def make_tcp(self,data: bytes, isAscii: bool = False) -> bytes:
        """
        Wrap a raw PCOM frame inside the Unitronics PCOM/TCP header.
        
        :param data: raw PCOM frame
        :type data: bytes
        :param isAscii: whether this is an ASCII PCOM frame
        :type isAscii: bool
        :return: TCP-wrapped frame
        :rtype: bytes
        """
        tcp = struct.pack("<H", self.current_tcp_id) # Transaction ID (2 bytes)
        self.current_tcp_id += 1
        tcp += struct.pack("B", 101) if isAscii else struct.pack("B", 102) # 101 for Ascii mode or 102 for Binary mode
        tcp += b"\x00" # Reserved
        tcp += struct.pack("<H", len(data)) # PCOM length
        tcp += data
        return tcp 
    
# CRC CALCULATORS

    def calc_binary_header_crc(self, data: bytes) -> bytes:
        """
        Compute the 16-bit checksum for the binary PCOM header.
        The CRC is computed over the first 22 bytes of the header.

        ALGORITHM:
              sum all bytes
              constrain to 16 bits
              compute 2's complement
              return as little endian uint16
        
        :param data: the partially built header bytes
        :type data: bytes
        :return: 2 byte CRC
        :rtype: bytes
        """
        # Packet[0:22]
        return struct.pack("<H", (( ~ (sum(data[0:22]) % 0x10_000) + 1 ) % 0xffff + 1))
   
    def calc_binary_footer_crc(self, data: bytes) -> bytes:
        """
        Compute the 16-bit checksum for the binary PCOM payload section.

        The footer CRC is calculated over the payload bytes only.

        ALGORITHM:
              sum all bytes
              constrain to 16 bits
              compute 2's complement
              return as little endian uint16

        :param data: full binary PCOM frame before footer CRC
        :type data: bytes
        :return: 2 byte CRC
        :rtype: bytes
        """
        # Packet[24:-3]
        return struct.pack("<H", (( ~ (sum(data[self.PCOM_HEADER_SIZE:]) % 0x10_000) + 1 ) % 0xffff + 1))

    def calc_ascii_crc(self, data: bytes) -> bytes:
        """
        Compute the ASCII PCOM checksum.

        Calculated as:
              sum(data[1:]) % 256

              then formatted as 2 uppercase ASCII hex characters.
        
        :param data: the ASCII PCOM frames before CRC
        :type data: bytes
        :return: 2 ASCII bytes
        :rtype: bytes
        """
        # Packet[1:-3]
        return hex(sum((data)[1:]) % 256).upper()[2:].rjust(2,"0").encode()
    
# BINARY PCOM REQUEST FACTORY

    def create_binary_request(
            self,
            command_opcode: int,
            command_details: bytes = b'\x00\x00\x00\x00\x00\x00',
            command_data: bytes = b"", 
            res1: bytes = b"\xfe", 
            res2: bytes = b"\x01", 
            res3: bytes = b"\x01\x00\x00", 
            res4: bytes = b"\x00"
            ) -> bytes:
        """
        Constructs a complete binary PCOM request frame.

        ASSEMBLES:
              HEADER|PAYLOAD DATA|FOOTER CRC|BINARY SUFFIX
              
        :param command_opcode: the PCOM operation code
        :type command_opcode: int
        :param command_details: six-byte opcode-specific field
        :type command_details: bytes
        :param command_data: optional payload data
        :type command_data: bytes
        :param res1: reserved field used by the PCOM protocol
        :type res1: bytes
        :param res2: reserved field used by the PCOM protocol
        :type res2: bytes
        :param res3: reserved field used by the PCOM protocol
        :type res3: bytes
        :param res4: reserved field used by the PCOM protocol
        :type res4: bytes
        :return: A complete binary PCOM frame ready to be sent to the PLC
        :rtype: bytes
        """

        # BUILDING HEADER
        header = self.binary_header_magic # Magic b"/_OPLC"
        header += b'\x00' # ID
        header += res1 # default: b'\xfe' # Reserved
        header += res2 # default: b'\x01' # Reserved
        header += res3 # default: b'\x01\x00\x00' # Reserved
        header += struct.pack("b", command_opcode) # Command Opcode
        header += res4 # default: b'\x00' # Reserved
        header += command_details[0:6] # Command details (6 bytes)
        header += struct.pack("<H", len(command_data)) # Command length
        header += self.calc_binary_header_crc(header) # CRC
        packet = header

        # ADD PAYLOAD
        packet += command_data # Data
       
        # CALCULATE CRC IF NEEDED
        if not command_data:
            footer_crc = b'\x00\x00'
        else:
            footer_crc = self.calc_binary_footer_crc(packet) # CRC
       
        # ADD FOOTER
        packet += footer_crc
        packet += self.binary_suffix # Suffix b"\\"

        if self.debugMode:
            self.print_pcom_binary(packet)
        
        if self.isTcp:
            return self.make_tcp(packet)
        
        return packet
    
# ASCII PCOM REQUEST FACTORY (JORDIE)

    def _build_ascii_request(self, opcode: bytes, payload: bytes = b"") -> bytes:
        """
        Build a complete ASCII PCOM request frame.

        :param opcode: ASCII opcode
        :type opcode: bytes
        :param payload: opcode-specific bytes
        :type payload: bytes
        :return: complete ASCII PCOM request frame
        :rtype: bytes
        """

        request = self.ascii_header_magic # /
        request += b"00"                  # Unit ID
        request += opcode
        request += payload
        request += self.calc_ascii_crc(request)
        request += self.ascii_suffix

        if self.debugMode:
            self.print_pcom_ascii(request)
        if self.isTcp:
            return self.make_tcp(request, isAscii = True)
        return request
    
# 32 Bit ASCII PARSER (JORDIE)

    def _parse_ascii_32bit(self, data: bytes, mode: str = "signed") -> list | None:
        """
        Parse an ASCII PCOM response containing 32-bit values.

        :param data: raw bytes received from the PLC
        :type data: bytes
        :param mode: signed, unsigned, or float
        :type mode: str
        :return: list of values or None if response is invalid
        :rtype: list | None
        """
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        if self.debugMode:
            self.print_pcom_ascii(data)
        try:
            text = data.decode("ascii", errors = "replace")
        except Exception:
            return None
        payload = text[self.PCOM_TCP_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]
        if not payload or len(payload) % 8 != 0:
            return None
        results = []
        for i in range(0, len(payload), 8):
            chunk = payload[i:i+8]
            try:
                if mode == "float":
                    # swap the 16-bit word pairs then unpack big-endian float
                    swapped = chunk[4:] + chunk[:4]
                    raw_bytes = bytes.fromhex(swapped)
                    val, = struct.unpack(">f", raw_bytes)
                else:
                    raw = int(chunk, 16)
                    if mode == "signed" and raw >= 0x80000000:
                        raw -= 0x100000000
                    val = raw
            except (ValueError, struct.error):
                return None
            results.append(val)
        return results

# READ PLC NAME

    # Binary Request

    def create_read_plc_name(self) -> bytes:
        """
        Build a binary PCOM request that asks the PLC for its configured name.
        
        :return: the PCOM request as bytes
        :rtype: bytes
        """
        opcode = 0x0c
        return self.create_binary_request(opcode)

    # Binary Response

    def parse_read_plc_name(self, data: bytes) -> bytes | int:
        """
        Parse a binary PCOM "Get PLC Name" response and return PLC name bytes.
        
        :param data: raw bytes recieved from the PLC
        :type data: bytes
        :return: the PLC name as raw bytes | 0 if too short
        :rtype: bytes | int
        """

        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]

        if self.debugMode:
            self.print_pcom_binary(data)
        
        # The header length should be 27 bytes long (including footer + suffix)
        if len(data) < 27:
            return 0
        
        # Extracts payload length
        name_len = struct.unpack("<H", data[20:22])[0]
        
        if not name_len:
            return 0
        
        # Check packet is long enough to contain name
        if len(data) < 27 + name_len:
            return 0
        
        # Extract name bytes from the payload region
        name = data[self.PCOM_HEADER_SIZE:self.PCOM_HEADER_SIZE + name_len]
        
        return name
    
# READ PLC VERSION

    # ASCII Request

    def create_read_plc_versions(self) -> bytes:
        """
        Build an ASCII PCOM request that asks the PLC for model/firmware versions.
        
        :return: the complete ASCII PCOM request frame
        :rtype: bytes
        """

        request = self.ascii_header_magic # Magic "/"
        request += b"00" # Unit ID (00 const)
        request += b"ID" # Opcode
        request += self.calc_ascii_crc(request) # CRC
        request += self.ascii_suffix # Suffix b"\x0d" = "\r"
        
        if self.debugMode:
            self.print_pcom_ascii(request)
        
        if self.isTcp:
            return self.make_tcp(request, isAscii=True)
        
        return request

    # ASCII Response

    def parse_version(self, data):
        """
        Parse an ASCII PCOM 'ID' response containing PLC model and firmware versions.
        
        :param data: raw bytes received from the PLC
        :returns: A dictionary with keys:
                     model
                     model_desc
                     hw_rev
                     fw_rev
                     leftover
        """
        
        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        
        if self.debugMode:
            self.print_pcom_ascii(data)

        # 49T4 C 
        # 004 010 36 B --> 4.10.36 B (OS)
        # 002 002 53 P --> 2.2.53 P (BOOT)
        # 000 000 43 F --> 0.0.43 F (BinLib / Force)
        # 11100001     --> ?????

        data = data.decode()
        data = data[self.PCOM_TCP_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]
        REGEX_FW_SINGLE = "(([0-9x]{3})([0-9x]{3})([0-9x]{2})([A-Z]+))"
        res = {}
        model_len = 6
        
        while self.MODELS.get(data[:model_len]) is None:
            model_len -= 1
            if model_len == 2:
                return data
        
        res["model"] = data[:model_len]
        res["model_desc"] = self.MODELS.get(data[:model_len])
        res["hw_rev"] = data[model_len:model_len+1]
        res["fw_ver"] = []
        sub_fw = re.findall(REGEX_FW_SINGLE, data)

        if not sub_fw:
            # no firmware version strings found
            res["fw_ver"] = []
            res["leftover"] = data
            return res
        
        for match in sub_fw:
            full_match, ver, ver_major, ver_minor, ver_type = match
            if ver_type == "FT":
        
                # 03100020 --> 0-3.10 (20)
                # 11100001 --> 1-1.10 (10)
                version = f"{full_match[0:1]}-{full_match[1:2]}.{full_match[2:4]} ({full_match[4:8]})"
        
            else:
                ver = int(ver) if ver.isdigit() else ver
                ver_major = int(ver_major) if ver_major.isdigit() else ver_major
                ver_minor = int(ver_minor) if ver_minor.isdigit() else ver_minor
                version = f"{ver}.{str(ver_major).zfill(3)} ({str(ver_minor).zfill(2)})" # 2.011 (02)
        
            res["fw_ver"].append({"version": version, "type": ver_type})
        
        last_full_match = sub_fw[-1][0]
        leftovers = data.split(last_full_match)[-1]
        res["leftover"] = leftovers
        return res

# READ SYSTEM INTEGERS (JORDIE)

    # ASCII Request 

    def create_read_system_integers(self, start: int = 0, count: int = 64) -> bytes:
        """
        Build an ASCII PCOM request to read system integers from the PLC.
        
        :param start: starting address of read
        :type start: int
        :param count: how many addresses to read
        :type count: int
        :return: the complete ASCII PCOM request frame as bytes
        :rtype: bytes
        """
        payload = f"{start:04X}{count:02X}".encode()        
        return self._build_ascii_request(b"GF", payload)
    
    # ASCII RESPONSE

    def parse_read_system_integers(self, data: bytes) -> list[int] | None:
        """
        Parse an ASCII PCOM response and return a list of values containing system integers.

        :param data:
        :type data:
        :return: A list of system integers | None
        :rtype: List | None
        """
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]

        if self.debugMode:
            self.print_pcom_ascii(data)
        
        try:
            text = data.decode("ascii", errors = "replace")
        except Exception:
            return None
        
        payload = text[self.PCOM_TCP_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]

        if not payload or len(payload) % 4 != 0:
            return None
        
        results = []
        for i in range(0, len(payload), 4):
            chunk = payload[i:i+4]
            try:
                raw = int(chunk, 16)
            except ValueError:
                return None
            if raw >= 0x8000:
                raw -= 0x10000
            results.append(raw)
        return results
    
# READ SYSTEM BITS (JORDIE)

    # ASCII Request

    def create_read_system_bits(self, start: int = 0, count: int = 64) -> bytes:
        """
        Build an ASCII PCOM request to read system bits from the PLC.
        
        :param start: the address to begin the read
        :type start: int
        :param count: how many addresses to read
        :type count: int
        :return: the complete ASCII PCOM request frame as bytes
        :rtype: bytes
        """
        payload = f"{start:04X}{count:02X}".encode()
        return self._build_ascii_request(b"GS", payload)
    
    # ASCII Response

    def parse_read_system_bits(self, data: bytes) -> list[bool] | None:
        """
        Parse an ASCII PCOM response and return a list of values containing system bits.

        :param data:
        :type data:
        :return: A list of system bits | None
        :rtype: List | None
        """
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]

        if self.debugMode:
            self.print_pcom_ascii(data)
        
        try:
            text = data.decode("ascii", errors = "replace")
        except Exception:
            return None
        
        payload = text[self.PCOM_TCP_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]

        if not payload:
            return None
        
        results = []
        for ch in payload:
            if ch not in ('0', '1'):
                return None
            results.append(ch == '1')
        return results
    
# READ MEMORY BITS (JORDIE)

    # ASCII Request

    def create_read_memory_bits(self, start: int = 0, count: int = 255) -> bytes:
        """
        Build an ASCII PCOM read memory bits request.

        :param start: address where read starts
        :type start: int
        :param count: number of addresses to read
        :type count: int
        :return: complete ASCII PCOM request frame
        :rtype: bytes
        """
        payload = f"{start:04X}{count:02X}".encode()
        return self._build_ascii_request(b"RB", payload)

    # ASCII Response

    def parse_read_memory_bits(self, data: bytes) -> list[bool] | None:
        """
        Parse an ASCII PCOM read memory bits response into a list.

        :param data: raw bytes recieved from PLC
        :type data: bytes
        :return: list of bool values or None
        :rtype: list[bool] | None
        """

        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        if self.debugMode:
            self.print_pcom_ascii(data)
        try:
            text = data.decode("ascii", errors = "replace")
        except Exception:
            return None
        payload = text[self.PCOM_TCP_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]
        if not payload:
            return None
        results = []
        for ch in payload:
            if ch not in ('0', '1'):
                return None
            results.append(ch == '1')
        return results

# READ MEMORY INTEGERS (JORDIE)

    # ASCII Request

    def create_read_memory_integers(self, start: int = 0, count: int = 64) -> bytes:
        """
        Build an ASCII PCOM read memory integers request.

        :param start: starting address to read
        :type start: int
        :param count: number of addresses to read
        :type count: int
        :return: a complete ASCII PCOM request frame
        :rtype: bytes
        """
        payload = f"{start:04X}{count:02X}".encode()
        return self._build_ascii_request(b"RW", payload)

    # ASCII Response

    def parse_read_memory_integers(self, data: bytes) -> list[int] | None:
        """
        Parse an ASCII PCOM read memory integers request into a list.

        :param data: the raw bytes received from the PLC
        :type data: bytes
        :return: a list of int or None
        :rtype: list[int] | None
        """
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        if self.debugMode:
            self.print_pcom_ascii(data)
        try:
            text = data.decode("ascii", errors = "replace")
        except Exception:
            return None
        payload = text[self.PCOM_TCP_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]
        if not payload or len(payload) % 4 != 0:
            return None
        results = []
        for i in range(0, len(payload), 4):
            try:
                raw = int(payload[i: i+4], 15)
            except ValueError:
                return None
            if raw >= 0x8000:
                raw -= 0x10000
            results.append(raw)
        return results

# READ MEMORY LONGS (JORDIE)

    # ASCII Request

    def create_read_memory_longs(self, start: int = 0, count: int = 32) -> bytes:
        """
        """
        return self._build_ascii_request(b"RNL", f"{start:04X}{count:02X}".encode())

    # ASCII Response

    def parse_read_memory_longs(self, data: bytes) -> list[int] | None:
        """
        """
        return self._parse_ascii_32bit(data, mode = "signed")

# READ MEMORY DOUBLE WORDS (JORDIE)

    # ASCII Request

    def create_read_memory_double_words(self, start: int = 0, count: int = 32) -> bytes:
        """
        """
        return self._build_ascii_request(b"RND", f"{start:04X}{count:02X}".encode())

    # ASCII Response

    def parse_read_memory_double_words(self, data: bytes) -> list[int] | None:
        """
        """
        return self._parse_ascii_32bit(data, mode = "unsigned")

# READ MEMORY FLOATS (JORDIE)

    # ASCII Request

    def create_read_memory_floats(self, start: int = 0, count: int = 32) -> bytes:
        """
        """
        return self._build_ascii_request(b"RNF", f"{start:04X}{count:02X}".encode())

    # ASCII Response

    def parse_read_memory_floats(self, data: bytes) -> list[float] | None:
        """
        """
        return self._parse_ascii_32bit(data, mode = "float")

# READ SYSTEM LONGS (JORDIE)

    # ASCII Request

    def create_read_system_longs(self, start: int = 0, count: int = 32) -> bytes:
        """
        """
        return self._build_ascii_request(b"RNH", f"{start:04X}{count:02X}".encode())

    # ASCII Response

    def parse_read_system_longs(self, data: bytes) -> list[int] | None:
        """
        """
        return self._parse_ascii_32bit(data, mode = "signed")

# READ SYSTEM DOUBLE WORDS (JORDIE)

    # ASCII Request

    def create_read_system_double_words(self, start: int = 0, count: int = 32) -> bytes:
        """
        """
        return self._build_ascii_request(b"RNJ", f"{start:04X}{count:02X}".encode())

    # ASCII Response

    def parse_read_system_double_words(self, data: bytes) -> list[int] | None:
        """
        """
        return self._parse_ascii_32bit(data, mode = "unsigned")

# WRITE SYSTEM INTEGERS (JORDIE)

    # ASCII Request

    def create_write_system_integer(self, address: int, value: int) -> bytes:
        """
        Build an ASCII PCOM request to write to the system integers.

        :param address: the address to write to
        :type address: int
        :param value: the value to write to the address
        :type value: int
        :return: the complete ASCII PCOM request
        :rtype: bytes
        """
        payload = f"{address:04X}01{value & 0xFFFF:04X}".encode()
        return self._build_ascii_request(b"SF", payload)
    
# WRITE SYSTEM BITS (JORDIE)

    def create_write_system_bit(self, address: int, value: bool) -> bytes:
        """
        Build an ASCII PCOM request to write to the system bits.

        :param address: the address to write to
        :type address: int
        :param value: the value to write to the address
        :type value: int
        :return: the complete ASCII PCOM request
        :rtype: bytes
        """
        payload = f"{address:04X}01".encode() + (b"1" if value else b"0")
        return self._build_ascii_request(b"SS", payload)

# READ OPERAND *** IGNORE RESPONSE LATER? *** *** PARSE IS NOT IMPLEMENTED ***

    # Binary Request

    def create_read_operand(self) -> bytes:
        """
        Build a binary PCOM request to read PLC operands.
        
        :return: a complete binary PCOM request frame
        :rtype: bytes
        """
        command_opcode = 0x4d
        command_details = b"\x00\x00\x00\x00\x02\x00" # Const for read operand
        command_data = (
            b"\x01\x00\x02\xff\x8d\x00\x03\x00\x11\xff\x00\x00\x09\x00\x03\x00"
         ) # Const for read Operand
        return self.create_binary_request(command_opcode = command_opcode,
                                          command_details = command_details,
                                          command_data = command_data
        )

    # Binary Response

    def parse_read_operand(self, data: bytes) -> None:
        """
        Parse a binary PCOM "Read Operand" response.

        *** CURRENTLY DOES NOTHING ***
        
        :param data: raw bytes received from PLC
        :type data: bytes
        """
        
        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        
        if self.debugMode:
            self.print_pcom_binary(data)

        # Not interesting data for us here
        pass

# STOP COMMAND

    # ASCII Request

    def create_stop_command(self) -> bytes:
        """
        Build an ASCII PCOM request that instructs the PLC to stop execution.

        "CCS" -> Control Command Stop

        :return: the complete ASCII PCOM stop command frame
        :rtype: bytes
        """
        request = self.ascii_header_magic # Magic (/)
        request += b"00" # Unit ID (00 const)
        request += b"CCS" # Opcode
        request += self.calc_ascii_crc(request)
        request += self.ascii_suffix
        
        if self.debugMode:
            self.print_pcom_ascii(request)

        if self.isTcp:
            return self.make_tcp(request, isAscii=True)
        
        return request
    
# READ UNIT ID

    # ASCII Request

    def create_read_unitID(self) -> bytes:
        """
        Build an ASCII PCOM request to read the PLC's Unit ID.
        
        :return: the complete ASCII PCOM request frame
        :rtype: bytes
        """
        request = self.ascii_header_magic # Magic "/"
        request += b"00" # Unit ID (00 const)
        request += b"UG" # Opcode
        request += self.calc_ascii_crc(request)
        request += self.ascii_suffix
        
        if self.debugMode:
            self.print_pcom_ascii(request)

        if self.isTcp:
            return self.make_tcp(request, isAscii=True)
        
        return request

    # ASCII Response

    def parse_read_unitID(self, data: bytes) -> bytes:
        """
        Parse an ASCII PCOM 'Get Unit ID' response.
        
        :param data: raw bytes recieved from the PLC
        :type data: bytes
        :return: the Unit ID as raw ASCII bytes
        :rtype: bytes
        """

        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        
        if self.debugMode:
            self.print_pcom_ascii(data)

        return data[self.PCOM_TCP_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]
    
# WHERE RESOURCE
  
    # Binary Request

    def create_where_resource(self, resource_id: int) -> bytes:
        """
        Build a binary PCOM request that asks the PLC for the location of a resource.

        Resource examples:
              project zip
              resource table
              signature table
        
        :param resource_id: integer identifier of the resource to locate
        :type resource_id: int
        :return: a complete binary PCOM request frame
        :rtype: bytes
        """
        opcode = 0x10
        res1 = b"\xfe"
        res2 = b"\x01"
        res3 = b"\x00\x00\x00" # different than default
        res4 = struct.pack("B", resource_id) # where the resource is selected
        command_details = b"\x00"*6
        return self.create_binary_request(
              command_opcode = opcode, 
              res1 = res1, 
              res2 = res2, 
              res3 = res3, 
              res4 = res4, 
              command_details = command_details
       )
 
    # Binary Response

    def parse_where_resource(self, data: bytes) -> tuple[int, int, int]:
        """
        Parse a binary PCOM 'Where Resource' response.
        
        :param data: raw bytes received from the PLC
        :type data: bytes
        :return: a tuple of (address, size, resource_id)
        :rtype: tuple[int, int, int]
        """
        
        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]

        if self.debugMode:
            self.print_pcom_binary(data)

        addr, size, res_id = struct.unpack(
            "<III", 
            data[self.PCOM_HEADER_SIZE:-self.PCOM_BINARY_FOOTER_SIZE]
            )
        
        return addr, size, res_id

# READ RESOURCE TABLE

    # Gets the address of the resource table
    # Binary Request
    def create_read_resource_table_address(self) -> bytes:
        """
        Build a binary PCOM request to obtain the address/size of the resource table.
        
        :return: a complete binary PCOM request frame
        :rtype: bytes
        """
        return self.create_translate_resource_index_to_address(0x0d)

    # This function parses the resource table struct from memory read from the PLC (using read_memory)
    # Binary Response
    def parse_read_resource_table(self, data: bytes) -> int:
        """
        Parse a PLC resource table structure from a binary PCOM memory-read response.

        The PLC's resource table is an array of 32-but integers located after the header.

        This function extracts the 10th resource entry, this is the signature table's
        resource index.

        :param data: raw bytes received from the PLC containing the resource table
        :type data: bytes
        :return: the signature table's resource index as an integer | 0 if too short
        :rtype: int
        """
        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]

        # check length 24 (header) + 9 * 4 (9th entry) = 64        
        if len(data) < 64:
            return 0
        
        if self.debugMode:
            self.print_pcom_binary(data)

        # OPLC_HEADER (size 24)
        # Resource table struct (each size 4)
        # We need the 10th resource (signature table) --> 24 + 9*4 
        index =  struct.unpack(
            "<I", 
            data[self.PCOM_HEADER_SIZE + 9*4: self.PCOM_HEADER_SIZE + 10*4]
            )[0]
        
        return index
    
# WRITE MEMORY

    # Binary Request
    def create_write_memory(
              self, 
              address: bytes, 
              size: int, data: bytes, 
              flag: int = 1
              ) -> bytes:
        """
        Build a binary PCOM request to write raw memory to the PLC.

        The command encodes the destination address and size in the 6-byte
        'command_details' field:
              4 bytes address
              2 bytes size

        The payload is the actual bytes to write.
        
        :param address: 4 byte packed address
        :type address: bytes
        :param size: number of bytes to write
        :type size: int
        :param data: raw bytes to write into memory
        :type data: bytes
        :param flag: memory/region selector used by the PLC
        :type flag: int
        :return: a complete binary PCOM write-memory request frame
        :rtype: bytes
        """
        
        opcode = 0x41
        res1 = b"\xfe"
        res2 = b"\x01"
        res3 = b"\x00\x00\x00" # different than default
        res4 = struct.pack("b", flag) # carries selector flag
        command_details = address
        command_details += struct.pack("<H", size)

        return self.create_binary_request(
            command_opcode = opcode, 
            res1 = res1, 
            res2 = res2, 
            res3 = res3, 
            res4 = res4, 
            command_details = command_details, 
            command_data = data
            )

    # NO BINARY RESPONSE?
    
# TRANSLATE RESOURCE INDEX TO ADDRESS

    # This function creates a request translating a resource index to its address. For example, the resource table has index 0x0d
    # Binary Request
    def create_translate_resource_index_to_address(self, index: int) -> bytes:
        """
        Build a binary PCOM request to translate a resource index into an address/size.
        
        :param index: resource index to translate
        :type index: int
        :return: a complete binary PCOM request frame
        :rtype: bytes
        """
        command_opcode = 0x16
        command_data = b"\x64\x00" # Const
        command_data += struct.pack("<H", index) # Resource Index
        res3 = b"\x00\x00\x00" # different than default
        return self.create_binary_request(
            command_opcode = command_opcode, 
            command_data = command_data, 
            res3 = res3
            )

    # Binary Response
    def parse_translate_index(self, data: bytes) -> tuple[bytes, int] | int:
        """
        Parse a binary PCOM 'Translate Index to Address' response.

        Response includes:
              4 byte address
              2 byte size
        
        :param data: raw bytes received from the PLC
        :type data: bytes
        :return: a tuple (address_bytes, size) | 0 if too short
        :rtype: tuple[bytes, int] | int
        """
        
        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        
        if self.debugMode:
            self.print_pcom_binary(data)

        if len(data) < 37:
            return 0
        
        # Message Struct:
        #   OPLC_HEADER (size 24)
        #   PCOM_DATA (should be <= size 10)
        #   OPLC_FOOTER (size 3)

        # PCOM_DATA Struct:
        #   ???? (size 4)
        #   Index Address (Size 4)
        #   Content Length (Size 2)

        # ***** THIS IS A LITTLE SUS *****
        # ???? is supposed to be 4 bytes but is represented here as 2
        # Something is wrong

        address = data[self.PCOM_HEADER_SIZE + 2: self.PCOM_HEADER_SIZE + 6]
        size = struct.unpack(
            "<H",
            data[self.PCOM_HEADER_SIZE + 6: self.PCOM_HEADER_SIZE + 8]
            )[0]
        
        return (address, size)

# OPCODE 1a (UNKNOWN OPCODE)
# OPCODE TABLE: FLASH MEMORY BUFFER

    # Unknown opcode
    # Binary Request
    def create_opcode_1a_request(self) -> bytes:
        """
        Build a binary PCOM request for opcode 0x1A.

        Appears to be a memory/flash buffering step.
        
        :return: a complete binary PCOM request frame
        :rtype: bytes
        """
        command_opcode = 0x1a
        res3 = b"\x00\x00\x00" # different than default

        return self.create_binary_request(
            command_opcode = command_opcode, 
            res3 = res3
            )

    # Binary Response    
    def parse_opcode_1a(self, data) -> None:
        """
        Parse a binary PCOM response to opcode 0x1A.

        DOES NOT DO ANYTHING
        
        :param data: raw bytes received from the PLC
        """
        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        
        if self.debugMode:
            self.print_pcom_binary(data)

# SIGNATURE TABLE SCHENANIGANS

    # Parse a single signature record
    def parse_signature(self, data: bytes, out = print) -> None:
        """
        Parse a PLC signature table containing one or more signature records.
        
        :param data: raw bytes received from the PLC
        :type data: bytes
        """
        reader = BytesIO(data) # Stream reader
        magic = up_I(reader) # Reads 4 bytes
        out(f"\t[-] Magic: {hex(magic)}") # Prints Magic
        total_len = up_I(reader) # Reads 4 bytes
        out(f"\t[-] Total Len: {hex(total_len)} ({total_len == len(data)})") # Prints length and checks to see if it matches buffer

        while reader.tell() < len(data): # Loops through records
            out(f"\t[-] Signature Topic")

            unk1 = reader.read(4)
            out(f"\t\t[-] Unk1: {tx(unk1)}") # Prints unknown field
            
            unk2 = reader.read(4)
            out(f"\t\t[-] Unk2: {tx(unk2)}") # Prints unknown field

            block_size = up_I(reader)
            out(f"\t\t[-] Size: {hex(block_size)}") # Size of signature block

            name_bytes = reader.read(18)

            try:
                name = name_bytes.decode("utf-16-le").rstrip("\x00")
            except UnicodeDecodeError:
                out(f"\t\t{WARNING}[x] Warning: failed to decode name as UTF-16, raw = {tx(name_bytes)}{ENDC}")
                name = name_bytes.decode("latin-1", errors = "replace")

            out(f"\t\t[-] Name: {name}") # Project name

              # We expect 200-1000 bytes
              # Subtraction:
              #      -4 unk1
              #      -4 unk2
              #      -4 block_size
              #      -18 name
              #      -4 footer

            if 1000 > block_size > 200:
                body = reader.read(block_size-4-4-4-18-4)
            else:
                block_size = 1000 # default
                body = reader.read(block_size-4-4-4-18-4)
            
            # Checks where footer is
            if not (reader.tell() < len(data)):
                footer = int.from_bytes(body[-4:],"little")
                body = body[:-4]
            else:
                footer = up_I(reader)
            
            # Decompresses zip, ignores zlib framing
            try:
                decompressed_body = zlib.decompress(body[11:],-15)
                out(f"\t\t[-] Decompressed Body: {len(decompressed_body)} bytes")
                self.parse_decompressed(decompressed_body, out = out)
                out(f"\t\t[-] Footer: {hex(footer)}")
            except Exception as e:
                pass
    
    def parse_decompressed(self, data: bytes, out = print) -> None:
        """
        Parse and print fields from a decompressed signature metadata blob.
        
        :param data: decompresses bytes from a signature record
        :type data: bytes
        """
        
        try:
            
            # data[0x4:0xc] - PC Date
            pc_date_double, = struct.unpack('<d', data[0x4:0xc])
            pc_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(pc_date_double)
            print_body_info("PC Date", pc_date, out = out)

            # data[0xc:0x1c] - GUID
            guid_tuple = struct.unpack('<IHH2s6s', data[0xc:0x1c])
            guid_first_part = '-'.join([hex(item).strip('0x').upper() for item in guid_tuple[:-2]])
            guid_second_part = f"{binascii.hexlify(guid_tuple[-2]).decode().upper()}-{binascii.hexlify(guid_tuple[-1]).decode().upper()}"
            guid = f"{{{guid_first_part}-{guid_second_part}}}"
            print_body_info('GUID', guid, out = out)

            # data[0x1c:0x2c] - Username
            print_body_info('User', data[0x1c:0x2c], out = out)

            # data[0x2c:0x40] - Description
            print_body_info('Description', data[0x2c:0x40], out = out)

            # data[0x40:0x68] - Path
            print_body_info('Path', data[0x40:0x68], out = out)

            # data[0x68:0x6a] - DB
            db, = struct.unpack('<H', data[0x68:0x6a])
            print_body_info('DB', db, out = out)

            # data[0x6a:0x6c] - Version Created
            created, = struct.unpack('<H', data[0x6a:0x6c])
            
            try:
                created_str = str(created)
                created_str = f"{created_str[0]}.{created_str[1]}.{created_str[2:]}"
            
            except Exception as e:
                created_str = str(created)
            
            print_body_info('Created Version', created_str, out = out)
            
            # data[0x6c:0x6e] - Modified Version
            modified, = struct.unpack('<H', data[0x6c:0x6e])
            
            try:
                modified_str = str(modified)
                modified_str = f"{modified_str[0]}.{modified_str[1]}.{modified_str[2:]}"
            
            except Exception as e:
                modified_str = str(modified)
            
            print_body_info('Modified Version', modified_str, out = out)

            # data[0x6e:0x70] - Booleans bitmask
            features_bitmask, = struct.unpack('<H', data[0x6e:0x70])
            features_bitmask_str = bin(features_bitmask)[2:].zfill(16)[::-1]

            info_table_bit, ladder_bit, ladder_data_bit, page_bit, misc_data_bit, eDT_Reserved1_bit, page_idx_bit, eDT_Reserved2_bit, variables_bit, eDT_Reserved3_bit, counters_bit, functionBlocks_bit, func_blocks_inst_bit, timers_bit, data_tables_bit, hw_config_bit = [bool(int(x)) for x in features_bitmask_str]

            # data[0x70:0x78] - Unk1/2
            unk1, unk2 = struct.unpack('<II', data[0x70:0x78])
            print_body_info('Unk1 (0)', unk1, out = out)
            print_body_info('Unk2 (0)', unk2, out = out)

            # data[0x78:0xb8] - All other integers

            info_table, ladder, ladder_data, page, misc_data, eDT_Reserved1, page_idx, eDT_Reserved2, variables, eDT_Reserved3, counters, functionBlocks, func_blocks_inst, timers, data_tables, hw_config, eDT_Reserved4 = struct.unpack('<'+'I'*17, data[0x78:0x78 + 4*17])
            
            print_body_info(f'Info Tables Downloaded: {info_table_bit} (CRC={info_table})', None, out = out)
            
            print_body_info(f'Ladder Downloaded: {ladder_bit} (CRC={ladder})', None, out = out)
            
            print_body_info(f'Ladder Data Downloaded: {ladder_data_bit} (CRC={ladder_data})', None, out = out)
            
            print_body_info(f'Page Downloaded: {page_bit} (CRC={page})', None, out = out)
            
            print_body_info(f'Misc.Data Downloaded: {misc_data_bit} (CRC={misc_data})', None, out = out)
            
            print_body_info(f'eDT_Reserved1 Downloaded: {eDT_Reserved1_bit} (CRC={eDT_Reserved1})', None, out = out)
            
            print_body_info(f'Pages->Idx Downloaded: {page_idx_bit} (CRC={page_idx})', None, out = out)
            
            print_body_info(f'eDT_Reserved2 Downloaded: {eDT_Reserved2_bit} (CRC={eDT_Reserved2})', None, out = out)
            
            print_body_info(f'Variables Downloaded: {variables_bit} (CRC={variables})', None, out = out)
            
            print_body_info(f'eDT_Reserved3 Downloaded: {eDT_Reserved3_bit} (CRC={eDT_Reserved3})', None, out = out)
            
            print_body_info(f'Counters Downloaded: {counters_bit} (CRC={counters})', None, out = out)
            
            print_body_info(f'FunctionBlocks Downloaded: {functionBlocks_bit} (CRC={functionBlocks})', None, out = out)
            
            print_body_info(f'Function Blocks Instance Downloaded: {func_blocks_inst_bit} (CRC={func_blocks_inst})', None, out = out)
            
            print_body_info(f'Timers Downloaded: {timers_bit} (CRC={timers})', None, out = out)
            
            print_body_info(f'Data Tables Downloaded: {data_tables_bit} (CRC={data_tables})', None, out = out)
            
            print_body_info(f'HW Configuration Downloaded: {hw_config_bit} (CRC={hw_config})', None, out = out)
            
            # data[0xbc:0xcc] - Connection info
            conn_info = data[0xbc:0xcc]
            conn_info_type = conn_info[0]
            
            if conn_info_type == 0:
                conn_info_general = "Serial"
                conn_info_details = conn_info[1:]
            
            elif conn_info_type == 3:
                conn_info_general = "TCP/IP"
                conn_info_ip = socket.inet_ntoa(conn_info[1:5])
                conn_info_port, = struct.unpack("<H", conn_info[7:9])
                conn_info_details = f"{conn_info_ip} TCP {conn_info_port}"
            else:
                conn_info_general = f"Unknown (type {conn_info_type})"
                conn_info_details = conn_info[1:].hex()
            
            print_body_info('Connection Info General', conn_info_general, out = out)
            
            print_body_info('Connection Info Details', conn_info_details, out = out)

            # data[0xcd:0xce] - PLC Reset Event
            plc_reset_event, = struct.unpack("<B", data[0xcd:0xce])
            PLC_RESET_DICT = {
                0: "None",
                1: "Flash",
                2: "Password",
                3: "Hardware Config",
                4: "Function Block",
                5: "Memory",
                6: "ISC",
                7: "Compiled STL Size",
                8: "Build All",
                9: "User",
            }
            plc_reset_event_desc = PLC_RESET_DICT.get(plc_reset_event, f"Unknown") + f" (type {hex(plc_reset_event)})"
            print_body_info('PLC Reset', plc_reset_event_desc, out = out)

            # data[0xd4:0xd8] - UnitID
            unitid, = struct.unpack("<I", data[0xd4:0xd8])
            print_body_info('Unit ID', unitid, out = out)

            #data[0xe4:0xe8] - User OS
            pc_os_type, = struct.unpack("<f", data[0xe4:0xe8])
            pc_os_desc = "Unknown"
            
            if pc_os_type == 5.0:
                pc_os_desc = "Windows XP"
            
            elif pc_os_type == 6.0:
                pc_os_desc = "Windows 7 or later"
            
            else:
                pc_os_desc = "Windows Unknown"

            pc_os_desc = f"{pc_os_desc} (type {pc_os_type})"
            print_body_info('PC OS', pc_os_desc, out = out)

            # data[0xe8:0x128] - User Computer Langauge
            language = data[0xe8:0x128]
            print_body_info('Language', language, out = out)

            # data[0x128:0x138] - PLC Model
            plc_model = data[0x128:0x138]
            print_body_info('PLC Model', plc_model, out = out)
            
            # data[0x138:0x148] - PLC Boot Version
            boot = data[0x138:0x148]
            print_body_info('Boot', boot, out = out)

            # data[0x148:0x158] - PLC Bin Lib Version
            bin_lib = data[0x148:0x158]
            print_body_info('BinLib', bin_lib, out = out)

            # data[0x158:0x168] - PLC Factory Boot Version
            factory_boot = data[0x158:0x168]
            print_body_info('Factory Boot', factory_boot, out = out)

            # data[0x168:0x16c] - User Connection Timeout
            timeout_ms, = struct.unpack("<I", data[0x168:0x16c])
            print_body_info('Timeout (ms)', timeout_ms, out = out)

            # data[0x16c:0x170] - User Connection Retry Count
            retry_count, = struct.unpack("<I", data[0x16c:0x170])
            print_body_info('Retry Count', retry_count, out = out)

            # data[0x170:] - Download Type
            download_type = data[0x170:]
            print_body_info('Download Type', download_type, out = out)

        except struct.error as e:
            out(f"\t\t{WARNING}[x] Warning: Struct failed to unpack a field.{ENDC}")
            return

        except Exception as e:
            out(f"Error: {e}")
    
# PASSWORD REQUEST

    # Binary request
    def create_check_password_request(self, password) -> bytes:
        """
        Build a binary PCOM request to check the PLC upload/write password
        
        :param password: password string to test
        :return: a complete binary PCOM request frame containing the packed password
        :rtype: bytes
        """
        opcode = 0x02
        res3 = b"\x00\x00\x00" # different than default
        password = password[:8].ljust(8," ").encode()

        return self.create_binary_request(
            command_opcode = opcode, 
            command_data = password, 
            res3 = res3
            )

    # Binary Response
    def parse_check_password(self, data: bytes) -> bool:
        """
        Parse a binary PCOM password-check response and indicate whether it succeeded.
        
        :param data: raw bytes received from the PLC
        :type data: bytes
        :return: True if password is correct, False otherwise
        :rtype: bool
        """        
        # Move after the PCOM/TCP header
        if self.isTcp:
            data = data[self.PCOM_TCP_HEADER_SIZE:]
        
        if self.debugMode:
            self.print_pcom_binary(data)

        opcode = data[12]
        reserved = data[13]
        
        if opcode == 0x82 and reserved == 0x64:
            return True
        
        return False
    
# READ MEMORY
    
    # Binary Request
    def create_read_memory(self, address: bytes, size: int, flag: int = 1) -> bytes:
        """
        Build a binary PCOM request to read raw PLC memory/
        
        :param address: 4-byte little-endian packed memory address
        :type address: bytes
        :param size: number of bytes to read
        :type size: int
        :param flag: memory/region selector
        :type flag: int
        :return: a complete binary PCOM read-memory request frame
        :rtype: bytes
        """
        #This function sends the read command head components to the create_binary_request function
        opcode = 0x01
        res1 = b"\xfe"
        res2 = b"\x01"
        res3 = b"\x00\x00\x00" # different than default
        res4 = struct.pack("B", flag) # carries flag
        command_details = address
        command_details += struct.pack("<H", size)

        return self.create_binary_request(
            command_opcode = opcode, 
            res1 = res1, 
            res2 = res2, 
            res3 = res3, 
            res4 = res4, 
            command_details = command_details
            )

# OUTSIDE OF PCOM_CLIENT CLASS

def do_read(ser, pcom_client, addr: int, length: int, flag: int, read_size:int = 976, out = print) -> bytes:
    """
    Read a section of PLC memory in chunks and return the concatenated bytes.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance 
    :param addr: starting memory address
    :type addr: int
    :param length: total number of bytes to read
    :type length: int
    :param flag: PLC memory/region selector
    :type flag: int
    :param read_size: maximum number of bytes to request per read
    :type read_size: int
    :return: the requested memory region as a single bytes object
    :rtype: bytes
    """
    pcom = pcom_client
    read_bytes = 0
    res = b""

    while read_bytes < length:
        out(f"[-] Reading from address: {hex(addr)} ({(read_bytes/length)*100:.2f}%)")
        size = min(read_size, length - read_bytes) #checks to see if the size of the memory to be read will be the read size of 976 or the remaining memory to be read
        read_mem = pcom.create_read_memory(struct.pack("<I", addr), size, flag = flag) #Creates the command
        ser.write(read_mem) #Sends command
        read_bytes += size
        addr += size
        resp = ser.read(1024*5)
        res += pcom.extract_pcom_data(resp)
    
    out(f"[-] Read is completed (100%)")
    
    return res

def do_write(ser, pcom_client, addr: int, data: bytes, flag: int, out = print) -> None:
    """
    Write a contiguous bytes buffer into PLC memory in chunks.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance 
    :param addr: starting memory address
    :type addr: int
    :param data: bytes to write into memory
    :type data: bytes
    :param flag: PLC memory/region selector
    :type flag: int
    """
    pcom = pcom_client
    write_size = 976
    write_bytes = 0
    length = len(data)
    
    while write_bytes < length:
        out(f"[-] Writing to address: {hex(addr)} ({(write_bytes/length)*100:.2f}%)")
        size = min(write_size, length-write_bytes)
        current_data_chunk = data[write_bytes:write_bytes+size]
        write_mem = pcom.create_write_memory(struct.pack("<I", addr), size, current_data_chunk, flag=flag)
        ser.write(write_mem)
        write_bytes += size
        addr += size
        resp = ser.read(1024*5)
        pcom.extract_pcom_data(resp)
    
    out(f"[-] Write is completed (100%)")

def print_firmware_version(data, out = print) -> None:
    """
    Pretty-print PLC model and firmware version information.
    
    :param data: parsed firmware dictionary | raw model/version string
    """
    
    if type(data) in [bytes, str]:
        out(f"\t[-] Unknown Model (model: {data})")
    
    else:
        out("\t[-] Model: " + data.get("model_desc"))
        out("\t[-] HW Rev: " + data.get("hw_rev"))
        is_ft_exists = False
    
        for fw_ver in data["fw_ver"]:
            fw_ver_type = fw_ver.get("type")
            if fw_ver_type == "FT":
                is_ft_exists = True
            fw_ver_version = fw_ver.get("version")
            out(f"\t[-] {PCOM_CLIENT.FW_TYPE_TO_NAME.get(fw_ver_type,fw_ver_type)}: {fw_ver_version}")
    
        if not is_ft_exists and len(data.get("leftover","")) == 8:
            binlib_ver_full = data.get("leftover")
            binlib_ver = f"{binlib_ver_full[0:1]}-{binlib_ver_full[1:2]}.{binlib_ver_full[2:4]} ({binlib_ver_full[4:8]})"
            out("\t[-] BinLib: " + binlib_ver)    

def print_plc_name(ser, pcom_client, out = print) -> None:
    """
    Query and print the PLC's configured name.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    """
    s = ser
    pcom = pcom_client
    # --> (B) Get Name Req (0c)
    get_name_req = pcom.create_read_plc_name()
    s.write(get_name_req)
    # <-- (B) Get Name Res (8c)
    resp = s.read(1024*5)
    plc_name = pcom.parse_read_plc_name(resp)
    out(f"\t[-] PLC Name: {plc_name.decode('windows-1252', errors = 'replace')}")

def print_plc_firmware(ser, pcom_client, out = print) -> None:
    """
    Query and print the PLC's model and firmware versions.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    """
    s = ser
    pcom = pcom_client
    # --> (A) Get Versions Req (ID)
    get_versions_req = pcom.create_read_plc_versions()
    s.write(get_versions_req)
    # <-- (A) Get Versions Res (ID)
    resp = s.read(1024*5)
    firmware_version_raw = pcom.parse_version(resp)
    print_firmware_version(firmware_version_raw, out = out)

def print_plc_unitid(ser, pcom_client, out = print) -> None:
    """
    Query and print the PLC Unit ID.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    """
    s = ser
    pcom = pcom_client
    # --> (A) Get UnitID (UG) Req  (UG)
    get_unitid_req = pcom.create_read_unitID()
    s.write(get_unitid_req)
    # <-- (A) Get UnitID (UG) Res  (UG)
    resp = s.read(1024*5)
    unitId = pcom.parse_read_unitID(resp)
    out(f"\t[-] UnitID: {unitId.decode()}")

def print_signature_table(ser, pcom_client, log_fn = None) -> None:
    """
    Discover, read, and parse the PLC signature table.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    """
    # Directions:
    # Client (EWS) <--> Server (PLC)
    # Type of Connection:
    # (B)inary (A)scii
    # --> (B) Get Name Req (0c)                     
    # <-- (B) Get Name Res (8c)                     
    # --> (A) Get Versions Req (ID)                 
    # <-- (A) Get Versions Res (ID)                 
    # --> (B) Read Operands Req (4D)                
    # <-- (B) Read Operands Res (CD)                
    # --> (A) Get UnitID (UG) Req  (UG)             
    # <-- (A) Get UnitID (UG) Res  (UG)             
    # --> (B) Get Resource Table Address Req (16)   
    # <-- (B) Get Resource Table Address Res (96)   
    # --> (B) Opcode 0x1a Req  (1A)                 
    # <-- (B) Opcode 0x1a Res  (9A)                 
    # --> (B) Read Resource Table Memory Req  (01)  
    # <-- (B) Read Resource Table Memory Res  (81)  
    # --> (B) Get Signature Address Req (16)        
    # <-- (B) Get Signature Address Res (96)        
    # --> (B) Opcode 0x1a Req  (1A)                 
    # <-- (B) Opcode 0x1a Res  (9A)                 
    # --> (B) Read Signature Table Memory Req  (01) 
    # <-- (B) Read Signature Table Memory Res  (81) 

    out = log_fn if log_fn else print
    s = ser
    pcom = pcom_client

    # --> (B) Read Operands Req (4D) 
    read_operand_req = pcom.create_read_operand()
    s.write(read_operand_req)

    # <-- (B) Read Operands Res (CD)
    resp = s.read(1024*5)

    # --> (B) Get Resource Table Address Req (16)
    get_resource_table_address_req = pcom.create_read_resource_table_address()
    s.write(get_resource_table_address_req)

    # <-- (B) Get Resource Table Address Res (96)
    resp = s.read(1024*5)
    rTable_addr, rTable_size = pcom.parse_translate_index(resp)
    rTable_addr_hex = hex(struct.unpack("<I", rTable_addr)[0])
    out(f"\t[-] Resource Table Address: {rTable_addr_hex} Size: {hex(rTable_size)}")

    # --> (B) Opcode 0x1a Req  (1A)
    flush_req = pcom.create_opcode_1a_request()
    s.write(flush_req)

    # <-- (B) Opcode 0x1a Res  (9A)
    resp = s.read(1024*5)
    pcom.parse_opcode_1a(resp)

    # --> (B) Read Resource Table Memory Req  (01)
    read_rTable_memory = pcom.create_read_memory(rTable_addr, rTable_size, flag=4)
    s.write(read_rTable_memory)

    # <-- (B) Read Resource Table Memory Res  (81)
    resp = s.read(1024*5)
    sigTable_index = pcom.parse_read_resource_table(resp)
    out(f"\t[-] Signature Table Index: {sigTable_index}")

    # --> (B) Get Signature Address Req (16)
    get_signature_table_address_req = pcom.create_translate_resource_index_to_address(sigTable_index)
    s.write(get_signature_table_address_req)

    # <-- (B) Get Signature Address Res (96)
    resp = s.read(1024*5)
    sigTable_address, sigTable_size = pcom.parse_translate_index(resp)
    sigTable_address_hex = hex(struct.unpack("<I", sigTable_address)[0])
    out(f"\t[-] Signature Table Address: {sigTable_address_hex} Size: {hex(sigTable_size)}")

    # --> (B) Opcode 0x1a Req  (1A)
    flush_req = pcom.create_opcode_1a_request()
    s.write(flush_req)

    # <-- (B) Opcode 0x1a Res  (9A)
    resp = s.read(1024*5)
    pcom.parse_opcode_1a(resp)

    # --> (B) Read Signature Table Memory Req  (01)
    # <-- (B) Read Signature Table Memory Res  (81) - Check
    addr = struct.unpack("<I", sigTable_address)[0]
    sig_table_data = do_read(ser=s, pcom_client=pcom,addr=addr, length=sigTable_size, flag=4, out = out)
    sigTable = pcom.parse_signature(sig_table_data, out = out)

def read_project_zip(ser, pcom_client, out = print) -> bytes:
    """
    Locate and read the PLC project ZIP resource from PLC memory.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    :return: raw bytes of the project ZIP resource as read from the PLC
    :rtype: bytes
    """
    s = ser
    pcom = pcom_client
    where_resource_id_req = pcom.create_where_resource(resource_id = RESOURCE_ID_PROJECT_ZIP)
    s.write(where_resource_id_req)
    resp = s.read(1024*5)
    addr, size, res_id = pcom.parse_where_resource(resp)
    out(f"[-] Project ZIP: addr={hex(addr)} size={hex(size)} flag={res_id}")
    project_zip_data = do_read(ser=s, pcom_client=pcom, addr=addr, length=size, flag=res_id, out = out) # flag should be 1
    return project_zip_data

def read_and_save_project_zip(ser, pcom_client, filename: str | None = None, out = print) -> str:
    """
    Read the PLC project ZIP resource and save it to a local .zip file.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    :return: The filename of the saved ZIP
    :rtype: str
    """
    pcom = pcom_client
    s = ser
    name = filename or f"project_{int(time.time())}.zip"
    project_zip = read_project_zip(s, pcom, out = out)
    project_zip = project_zip[0x2a:]
    with open(name, "wb") as f:
        f.write(project_zip)
    out(f"[-] Saved project ZIP to: {name}")
    return name

def read_memory(
        ser, 
        pcom_client, 
        loc_type: int = 1, 
        start: int = 0, 
        end: int = 0x100000, 
        filename: str | None = None,
        out = print
        ) -> str:
    """
    Dump a region of PLC memory to a binary file.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    :param loc_type: PLC memory/region selector
    :type loc_type: int
    :param start: starting memory address
    :type start: int
    :param end: ending memory address
    :type end: int
    :return: filename of saved dump
    :rtype: str
    """
    if end <= start:
        out(f"[X] end ({hex(end)}) must be greater than start ({hex(start)})")
        return ""

    length = end - start
    out(f"[-] Dumping memory from {hex(start)} to {hex(end)} ({hex(length)} bytes, flag={loc_type})")

    pcom = pcom_client
    filename = filename or f"ram_{hex(start)}_{hex(end)}_flag_{loc_type}_{int(time.time())}.bin"

    # Reduce timeout for the dump to avoid 250ms dead-wait after each response
    old_timeout = ser.timeout
    ser.timeout = 0.125

    try:
        data = do_read(ser, pcom, addr=start, length=length, flag=loc_type, out=out)
    finally:
        ser.timeout = old_timeout  # Always restore, even if do_read throws

    with open(filename, "wb") as f:
        f.write(data)

    out(f"[-] Saved dump to: {filename}")
    return filename

def write_memory(ser, pcom_client, addr: int, data: bytes, loc_type: int = 1, out = print) -> None:
    """
    Write a bytes buffer into PLC memory.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    :param addr: starting memory address
    :type addr: int
    :param data: bytes to write into PLC memory
    :type data: bytes
    :param loc_type: PLC memory/region selector
    :type loc_type: int
    """
    out(f"[-] Writing memory from from address {hex(addr)} with size {hex(len(data))} (flag={loc_type})")
    do_write(ser, pcom_client, addr, data, loc_type, out = out)

def upload_auth(ser, pcom_client, password: str = PASSWORD_DEFAULT, out = print) -> bool:
    """
    Check whether a password grants upload/write authorization on the PLC.
    
    :param ser: an open serial object
    :param pcom_client: PCOM_CLIENT instance
    :param password: password string to test
    :type password: str
    :return: True if password is accepted otherwise False
    :rtype: bool
    """
    s = ser
    pcom = pcom_client
    out(f"[-] Trying to check upload_auth with password: '{password}'")
    # --> (B) Opcode 0x02 Req
    req_pass = pcom.create_check_password_request(password)
    s.write(req_pass)
    # <-- (B) Opcode 0x82 Res
    resp = s.read(1024*5)
    is_ok = pcom.parse_check_password(resp)
    if is_ok:
        out(f"\t[-] Password: OK")
        return True
    else:
        out(f"\t[-] Password: Bad")
        return False
    
def read_system_integers(ser, pcom_client, start: int = 0, count: int = 64, out = print) -> list[int] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_system_integers(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_system_integers(resp)

    if values is None:
        out("[X] Failed to read system integers - no valid response.")
        return None
    
    out(f"[-] System Integers SI{start} to SI{start + len(values) - 1}:")
    for i, val in enumerate(values):
        label = SI_MAP.get(start + i, "")
        out(f"      SI {start + i} = {val} (0x{val & 0xFFFF:04X})  | {label}")

    return values

def read_system_bits(ser, pcom_client, start: int = 0, count: int = 32, out = print) -> list[bool] | None:
    """
    Read and display System Bits.

    :param ser:
    :param pcom_client:
    :param start:
    :type start:
    :param count:
    :type count:
    :param out:
    :type out:
    :return:
    :rtype:
    """

    pcom = pcom_client
    ser.write(pcom.create_read_system_bits(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_system_bits(resp)

    if values is None:
        out("[X] Failed to read system bits - no valid response.")
        return None

    out(f"[-] System Bits SB{start} to SB{start + len(values) -1}:")
    for i, val in enumerate(values):
        label = SB_MAP.get(start + i, "")
        state = "1" if val else "0"
        out(f"      SB{start + i} = {state}  | {label}")
    
    return values

def read_memory_bits(ser, pcom_client, start: int = 0, count: int = 255, out = print) -> list[bool] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_memory_bits(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_memory_bits(resp)
    if values is None:
        out("[X] Failed to read memory bits.")
        return None
    out(f"[-] Memory Bits MB{start} to MB{start + len(values) -1}:")
    for i, val in enumerate(values):
        out(f"MB {start + i} = {'1' if val else '0'}")
    return values

def read_memory_integers(ser, pcom_client, start: int = 0, count: int = 64, out = print) -> list[int] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_memory_integers(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_memory_integers(resp)
    if values is None:
        out("[X] Failed to read memory integers.")
        return None
    out(f"[-] Memory Integers MI{start} to MI{start + len(values) - 1}:")
    for i, val in enumerate(values):
        out(f"MI{start + i} = {val}")
    return values

def read_memory_longs(ser, pcom_client, start: int = 0, count: int = 32, out = print) -> list[int] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_memory_longs(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_memory_longs(resp)
    if values is None:
        out("[X] Failed to read memory longs.")
        return None
    out(f"[-] Memory Longs ML{start} to ML{start + len(values) - 1}:")
    for i, val in enumerate(values):
        out(f"ML{start + i} = {val}")
    return values

def read_memory_double_words(ser, pcom_client, start: int = 0, count: int = 32, out = print) -> list[int] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_memory_double_words(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_memory_double_words(resp)
    if values is None:
        out("[X] Failed to read memory double words.")
        return None
    out(f"[-] Memory Double Words MDW{start} to MDW{start + len(values) - 1}:")
    for i, val in enumerate(values):
        out(f"MDW{start + i} = {val}")
    return values

def read_memory_floats(ser, pcom_client, start: int = 0, count: int = 32, out = print) -> list[float] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_memory_floats(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_memory_integers(resp)
    if values is None:
        out("[X] Failed to read memory floats.")
        return None
    out(f"[-] Memory Floats MF{start} to MF{start + len(values) - 1}:")
    for i, val in enumerate(values):
        out(f"MF{start + i} = {val}")
    return values

def read_system_longs(ser, pcom_client, start: int = 0, count: int = 32, out = print) -> list[int] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_system_longs(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_system_longs(resp)
    if values is None:
        out("[X] Failed to read system longs.")
        return None
    out(f"[-] System Longs SL{start} to SL{start + len(values) - 1}:")
    for i, val in enumerate(values):
        out(f"SL{start + i} = {val}")
    return values

def read_system_double_words(ser, pcom_client, start: int = 0, count: int = 32, out = print) -> list[int] | None:
    """
    """
    pcom = pcom_client
    ser.write(pcom.create_read_system_double_words(start = start, count = count))
    resp = ser.read(1024 * 5)
    values = pcom.parse_read_system_double_words(resp)
    if values is None:
        out("[X] Failed to read system double words.")
        return None
    out(f"[-] System Double Words SDW{start} to SDW{start + len(values) - 1}:")
    for i, val in enumerate(values):
        out(f"SDW{start + i} = {val}")
    return values

SB_DESTRUCTIVE = {24, 300, 314} # Can do bad things
SB_OBSERVABLE = {301, 302, 310, 311} # Does IRL stuff

def write_system_bit(ser, pcom_client, address: int, value: bool, out = print, force: bool = False) -> bool:
    """
    """

    label = SB_MAP.get(address, "Unknown")
    if address in SB_DESTRUCTIVE and not force:
        out(f"[X] SB{address} ({label}) is DESTRUCTIVE - pass force = True to write.")
        return False
    ser.write(pcom_client.create_write_system_bit(address, value))
    ser.read(1024 * 5)
    out(f"[-] SB{address} ({label}) set to {'1' if value else '0'}")
    
    return True

def write_system_integer(ser, pcom_client, address: int, value: int, out = print) -> bool:
    """
    """

    label = SI_MAP.get(address, "Unknown")
    ser.write(pcom_client.create_write_system_integer(address, value))
    ser.read(1024 * 5)
    out(f"[-] SI{address} ({label}) set to {value} (0x{value & 0xFFFF})")
    return True

# CLI FUNCTIONS

def prompt_int(prompt: str, default: int | None = None) -> int:
    """
    Prompt user for an int, accepts decimal or hex.
    
    :param prompt: text shown to the user
    :type prompt: str
    :param default: value returned when the user enters nothing
    :type default: int | None
    :return: parsed integer value
    :rtype: int
    """
    while True:
        suffix = f" [default: {hex(default) if isinstance(default, int) else default}]" if default is not None else ""
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return int(raw, 0)
        except ValueError:
            print(f"{WARNING}[X] Please enter a valid integer.{ENDC}")

def prompt_str(prompt: str, default: str | None = None) -> str:
    """
    Prompt the user for a string value.
    
    :param prompt: text shown to the user
    :type prompt: str
    :param default: value returned when the user enters nothing
    :type default: str | None
    :return: the user's input string
    :rtype: str
    """
    suffix = f" [default: {default}]" if default is not None else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    return raw if raw else (default or "")

def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """
    Prompt the user for a yes/no decision.
    
    :param prompt: question shown to the user
    :type prompt: str
    :param default: value returned when the user enters nothing
    :type default: bool
    :return: True for yes, False for no
    :rtype: bool
    """
    d = "Y/n" if default else "y/N"
    raw = input(f"{prompt} [{d}]: ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes")

def dump_one_file(ser, pcom):
    """
    Dump a PLC memory range to a single file
    
    :param ser: open serial connection object
    :param pcom: PCOM_CLIENT instance
    """
    start = prompt_int("Start address", 0x0)
    end = prompt_int("End address (non-inclusive)", 0x40000)
    flag = prompt_int("Memory flag", 1)
    filename = prompt_str("Output filename", "")

    if end <= start:
        print(f"{WARNING}[X] End must be greater than start.{ENDC}")
        return

    read_memory(ser, pcom, loc_type = flag, start = start, end = end, filename = filename or None)

    print(f"[-] Saved dump to: {filename}")

def project_zip_dump(ser, pcom):
    """
    Read the PLC project ZIP and optionally save it to disk.
    
    :param ser: open serial connection object
    :param pcom: PCOM_CLIENT instance
    """
    data = read_project_zip(ser, pcom)
    print(f"[-] Read raw project resource: {len(data)} bytes")
    if len(data) > 0x2A:
        stripped = data[0x2A:]
        print(f"[-] After stripping 0x2A header: {len(stripped)} bytes")
        print(f"[-] Magic after strip: {stripped[:4]!r} (ZIP often starts with b'PK\\x03\\x04')")
    else:
        print(f"{WARNING}[X] Data too short to strip 0x2A header.{ENDC}")

    if prompt_yes_no("Save as .zip file?", default = False):
        out = prompt_str("Output filename (leave blank for auto)", "")
        if not out:
            out = f"project_{int(time.time())}.zip"
        payload = data[0x2A:] if len(data) > 0x2A else data
        with open(out, "wb") as f:
            f.write(payload)
        print(f"[-] Saved: {out}")

# SYSTEM/MEMORY VALUE DUMPS

def dump_system_integers_csv(ser, pcom_client, filename: str | None = None, out = print) -> str | None:
    """
    """

    pcom = pcom_client
    filename = filename or f"si_dump_{int(time.time())}.csv"
    CHUNK = 64
    MAX_SI = 512

    out(f"[-] Sweeping SI0 to SI{MAX_SI - 1} in chunks of {CHUNK}")

    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value", "description"])

        for start in range(0, MAX_SI, CHUNK):
            count = min(CHUNK, MAX_SI - start)
            ser.write(pcom.create_read_system_integers(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_system_integers(resp)

            if values is None:
                out(f"[X] No response for SI{start}-SI{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                addr = start + i
                label = SI_MAP.get(addr, "")
                writer.writerow([addr, val, label])
    
    out(f"[-] Saved: {filename}")
    return filename

def dump_system_bits_csv(ser, pcom_client, filename: str | None = None, out = print) -> str | None:
    """
    """

    pcom = pcom_client
    filename = filename or f"sb_dump_{int(time.time())}.csv"
    CHUNK = 64
    MAX_SB = 512

    out(f"[-] Sweeping SB0 to SB{MAX_SB - 1} in chunks of {CHUNK}")

    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value", "description"])

        for start in range(0, MAX_SB, CHUNK):
            count = min(CHUNK, MAX_SB - start)
            ser.write(pcom.create_read_system_bits(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_system_bits(resp)

            if values is None:
                out(f"[X] No response for SB{start} - SB{start + count - 1}, skipping.")
                continue

            for i, val in enumerate(values):
                addr = start + i
                label = SB_MAP.get(addr, "")
                writer.writerow([addr, 1 if val else 0, label])

    out(f"[-] Saved: {filename}")
    return filename

def dump_memory_bits_csv(ser, pcom_client, filename = None, out = print) -> str | None:
    """
    """
    pcom = pcom_client
    filename = filename or f"mb_dump_{int(time.time())}.csv"
    CHUNK, MAX = 255, 8192
    out(f"[-] Sweeping MB0 to MB{MAX - 1}...")
    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for start in range(0, MAX, CHUNK):
            count = min(CHUNK, MAX - start)
            ser.write(pcom.create_read_memory_bits(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_memory_bits(resp)
            if values is None:
                out(f"[X] No response MB{start} -> MB{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                writer.writerow([start + i, 1 if val else 0])
    out(f"[-] Saved: {filename}")
    return filename

def dump_memory_integers_csv(ser, pcom_client, filename = None, out = print) -> str | None:
    """
    """
    pcom = pcom_client
    filename = filename or f"mi_dump_{int(time.time())}.csv"
    CHUNK, MAX = 64, 4096
    out(f"[-] Sweeping MI0 to MI{MAX - 1}...")
    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for start in range(0, MAX, CHUNK):
            count = min(CHUNK, MAX - start)
            ser.write(pcom.create_read_memory_integers(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_memory_integers(resp)
            if values is None:
                out(f"[X] No response MI{start} -> MI{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                writer.writerow([start + i, val])
    out(f"[-] Saved: {filename}")
    return filename

def dump_memory_longs_csv(ser, pcom_client, filename = None, out = print) -> str | None:
    """
    """
    pcom = pcom_client
    filename = filename or f"ml_dump_{int(time.time())}.csv"
    CHUNK, MAX = 32, 512
    out(f"[-] Sweeping ML0 to ML{MAX - 1}...")
    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for start in range(0, MAX, CHUNK):
            count = min(CHUNK, MAX - start)
            ser.write(pcom.create_read_memory_longs(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_memory_longs(resp)
            if values is None:
                out(f"[X] No response ML{start} -> ML{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                writer.writerow([start + i, val])
    out(f"[-] Saved: {filename}")
    return filename

def dump_memory_double_words_csv(ser, pcom_client, filename = None, out = print) -> str | None:
    """
    """
    pcom = pcom_client
    filename = filename or f"mdw_dump_{int(time.time())}.csv"
    CHUNK, MAX = 32, 256
    out(f"[-] Sweeping MDW0 to MDW{MAX - 1}...")
    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for start in range(0, MAX, CHUNK):
            count = min(CHUNK, MAX - start)
            ser.write(pcom.create_read_memory_double_words(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_memory_double_words(resp)
            if values is None:
                out(f"[X] No response MDW{start} -> MDW{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                writer.writerow([start + i, val])
    out(f"[-] Saved: {filename}")
    return filename

def dump_memory_floats_csv(ser, pcom_client, filename = None, out = print) -> str | None:
    """
    """
    pcom = pcom_client
    filename = filename or f"mf_dump_{int(time.time())}.csv"
    CHUNK, MAX = 32, 64
    out(f"[-] Sweeping MF0 to MF{MAX - 1}...")
    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for start in range(0, MAX, CHUNK):
            count = min(CHUNK, MAX - start)
            ser.write(pcom.create_read_memory_floats(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_memory_floats(resp)
            if values is None:
                out(f"[X] No response MF{start} -> MF{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                writer.writerow([start + i, f"{val:.6f}"])
    out(f"[-] Saved: {filename}")
    return filename

def dump_system_longs_csv(ser, pcom_client, filename = None, out = print) -> str | None:
    """
    """
    pcom = pcom_client
    filename = filename or f"sl_dump_{int(time.time())}.csv"
    CHUNK, MAX = 32, 56
    out(f"[-] Sweeping SL0 to SL{MAX - 1}...")
    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for start in range(0, MAX, CHUNK):
            count = min(CHUNK, MAX - start)
            ser.write(pcom.create_read_system_longs(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_system_longs(resp)
            if values is None:
                out(f"[X] No response SL{start} -> SL{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                writer.writerow([start + i, val])
    out(f"[-] Saved: {filename}")
    return filename

def dump_system_double_words_csv(ser, pcom_client, filename = None, out = print) -> str | None:
    """
    """
    pcom = pcom_client
    filename = filename or f"sdw_dump_{int(time.time())}.csv"
    CHUNK, MAX = 32, 64
    out(f"[-] Sweeping SDW0 to SDW{MAX - 1}...")
    with open(filename, "w", newline = "") as f:
        writer = csv.writer(f)
        writer.writerow(["address", "value"])
        for start in range(0, MAX, CHUNK):
            count = min(CHUNK, MAX - start)
            ser.write(pcom.create_read_system_double_words(start = start, count = count))
            resp = ser.read(1024 * 5)
            values = pcom.parse_read_system_double_words(resp)
            if values is None:
                out(f"[X] No response SDW{start} -> SDW{start + count - 1}, skipping.")
                continue
            for i, val in enumerate(values):
                writer.writerow([start + i, val])
    out(f"[-] Saved: {filename}")
    return filename

def dump_all_csv(ser, pcom_client, folder: str | None = None, out = print) -> str:
    """
    Dump all operand types to CSV files in a single timestamped folder.

    :param ser: open serial connection object
    :param pcom_client: PCOM_CLIENT instance
    :param folder: output folder path, auto-generated if None
    :type folder: str | None
    :param out: callable for output, defaults to print
    :type out: callable
    :return: path to folder
    :rtype: str
    """
    import os
    folder = folder or f"dump_{int(time.time())}"
    os.makedirs(folder, exist_ok = True)
    out(f"[-] Saving all operand CSVs to: {folder}/")

    dumps = [
        ("MB", dump_memory_bits_csv, "mb_dump.csv"),
        ("MI", dump_memory_integers_csv, "mi_dump.csv"),
        ("ML", dump_memory_longs_csv, "ml_dump.csv"),
        ("MDW", dump_memory_double_words_csv, "mdw_dump.csv"),
        ("MF", dump_memory_floats_csv, "mf_dump.csv"),
        ("SB", dump_system_bits_csv, "sb_dump.csv"),
        ("SI", dump_system_integers_csv, "si_dump.csv"),
        ("SL", dump_system_longs_csv, "sl_dump.csv"),
        ("SDW", dump_system_double_words_csv, "sdw_dump.csv"),
    ]

    for label, fn, fname in dumps:
        out(f"[-] Dumping {label}...")
        try:
            fn(ser, pcom_client, filename = os.path.join(folder, fname), out = out)
        except Exception as e:
            out(f"[X] {label} dump failed: {e}")

    out(f"[-] All dumps complete. Folder: {folder}/")
    return folder

def auth(ser, pcom):
    """
    Test the PLC upload/write password.
    
    :param ser: open serial connection object
    :param pcom: PCOM_CLIENT instance
    """
    pwd = prompt_str("Password (8 chars, will be padded/truncated)", "*" * 8)
    ok = upload_auth(ser, pcom, password=pwd)
    print("[-] Auth result:", "OK" if ok else "BAD")

def stop_plc(ser, pcom):
    """
    Send the ASCII stop command to the PLC.
    
    :param ser: open serial connection object
    :param pcom: PCOM_CLIENT instance
    """
    print(f"{WARNING}[X] This sends CCS (STOP) to the PLC. It can halt logic execution.{ENDC}")
    if not prompt_yes_no("Are you sure you want to STOP the PLC?", default = False):
        print("[-] Stop cancelled.")
        return
    req = pcom.create_stop_command()
    ser.write(req)
    resp = ser.read(1024 * 5)
    if pcom.debugMode:
        pcom.print_pcom_ascii(resp)
    print("[-] Stop command sent.")

def sweep_resource_ids(ser, pcom_client, out=print) -> None:
    """
    Sweep all 255 resource IDs and log the address, size, and resource ID
    returned by the PLC for each one.
    """
    import csv

    pcom = pcom_client
    filename = f"resource_sweep_{int(time.time())}.csv"

    out(f"[-] Sweeping all 255 resource IDs...")

    results = []

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["resource_id", "address", "size", "res_id_returned", "notes"])

        for rid in range(256):
            try:
                ser.write(pcom.create_where_resource(rid))
                resp = ser.read(1024 * 5)

                if len(resp) < 24 + 12 + 3:
                    out(f"  ID {rid:3d}: response too short")
                    writer.writerow([rid, "", "", "", "too short"])
                    continue

                addr, size, res_id_returned = pcom.parse_where_resource(resp)

                notes = []
                if addr == 0 and size == 0:
                    notes.append("null")
                if rid == RESOURCE_ID_PROJECT_ZIP:
                    notes.append("PROJECT_ZIP")
                if rid == 0x0d:
                    notes.append("RESOURCE_TABLE")
                if size > 0:
                    notes.append(f"addr={hex(addr)}")

                note_str = " ".join(notes)
                out(f"  ID {rid:3d}: addr={hex(addr):<12} size={hex(size):<10} returned_id={res_id_returned:<5} {note_str}")
                writer.writerow([rid, hex(addr), hex(size), res_id_returned, note_str])
                results.append((rid, addr, size, res_id_returned))

            except Exception as e:
                out(f"  ID {rid:3d}: ERROR - {e}")
                writer.writerow([rid, "", "", "", f"error: {e}"])

    # Summary - only non-null entries
    out(f"\n[-] Non-null results:")
    for rid, addr, size, ret in results:
        if addr != 0 or size != 0:
            out(f"  ID {rid:3d}: addr={hex(addr)}  size={hex(size)}  returned_id={ret}")

    out(f"[-] Saved to {filename}")

def main() -> None:
    """
    Entry point
    """
    # Session startup

    result = auto_detect_plc()
    if result is None:
        print("Could not connect to PLC.")
        return
    ser, pcom = result

    upload_auth(ser, pcom, "12345678")

    try:
        while True:
            print("\nPCOM Terminal Menu")
            print(" 1) Print PLC Name")
            print(" 2) Print PLC Firmware / Versions")
            print(" 3) Print PLC Unit ID")
            print(" 4) Print Signature Table")
            print(" 5) Read Project ZIP")
            print(" 6) Dump Memory Range to file")
            print(" 7) Check Upload/Auth Password")
            print(" 8) STOP PLC")
            print(" 9) Toggle debugMode (currently: {})".format("ON" if pcom.debugMode else "OFF"))
            print(" 10) Read System Integer")
            print(" 11) Read Information Mode Password")
            print(" 12) Dump ALL operands to CSV folder")
            print(" 0) Exit")

            choice = input("Select an option: ").strip()

            if choice == "1":
                print_plc_name(ser, pcom)
            elif choice == "2":
                print_plc_firmware(ser, pcom)
            elif choice == "3":
                print_plc_unitid(ser, pcom)
            elif choice == "4":
                print_signature_table(ser, pcom)
            elif choice == "5":
                project_zip_dump(ser, pcom)
            elif choice == "6":
                dump_one_file(ser, pcom)
            elif choice == "7":
                auth(ser, pcom)
            elif choice == "8":
                stop_plc(ser, pcom)
            elif choice == "9":
                pcom.debugMode = not pcom.debugMode
                print(f"[-] debugMode is now {'ON' if pcom.debugMode else 'OFF'}")
            elif choice == "0":
                print("[-] Goodbye.")
                break
            elif choice == "10":
                si_addr = prompt_int("SI address", 254)
                si_count = prompt_int("Count", 1)
                read_system_integers(ser, pcom, start = si_addr, count = si_count)
            elif choice == "11":
                password = read_system_integers(ser, pcom, start = 253, count = 1)
                print(f"[-] Information Mode Password: {password}")
            elif choice == "12":
                folder = dump_all_csv(ser, pcom)
            else:
                print("  [!] Invalid choice. Pick a number from the menu.")

    finally:
        try:
            ser.close()
        except Exception:
            pass
 
if __name__ == "__main__":
    main()
