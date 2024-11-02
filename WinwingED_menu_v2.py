import hid
from pynput.keyboard import Controller, Key
from time import sleep
from ufc import UFCSimAppProHelper
import socket
import json
import datetime

# Initialize variables to store the vendor and product ID
vendor_id = None
product_id = None

for device in hid.enumerate():
    if device['product_string'] == 'WINWING UFC1':
        vendor_id = f"0x{device['vendor_id']:04x}"
        product_id = f"0x{device['product_id']:04x}"
        break

# Check if the device was found
if vendor_id is None or product_id is None:
    print("WINWING UFC not found. Exiting")
    exit()

gamepad = hid.device()
gamepad.open(int(vendor_id, 16), int(product_id, 16))
gamepad.set_nonblocking(True)
keyboard = Controller()

#Initialise button states
button_names = ['IP','1', '2', '3', '4','5','6',
                '7', '8', '9', 'Clr', '0', 'Ent',
                'Opt1', 'Opt2', 'Opt3', 'Opt4', 'Opt5', 'EmCon',
                'AP','IFF','TCN','ILS','DL','BCN','ON_OFF'
                ]
buttons = {}
for list_id, button_name in enumerate(button_names):
    buttons[button_name] = {"ID":list_id + 1, "prev_State": 0, "cur_State" : 0}

    print(buttons[button_name])

menu_items = ['AP','IFF','TCN','ILS','DL','ON_OFF']
menu_state = 1

def send_json_udp_message(json_data, host='localhost', port=16536):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(json.dumps(json_data).encode('utf-8'), (host, port))

simapp_pro_start_messages = [
    {"func": "net", "msg": "ready"},
    {"func": "mission", "msg": "ready"},
    {"func": "mission", "msg": "start"},
    {"func": "mod", "msg": "FA-18C_hornet"}
]

# Connect to SimApp Pro and prepare to start receiving data
for payload in simapp_pro_start_messages:
    send_json_udp_message(payload)

# Create a UFC payload
ufc_payload = {
    "option1": "-", 
    "option2": "-",
    "option3": "-",
    "option4": "-",
    "option5": "-",
    "com1": "1",
    "com2": "1",
    "scratchPadNumbers": "",
    "scratchPadString1": "",
    "scratchPadString2": "",
    "selectedWindows": ["1"]
}
ufcHelper = UFCSimAppProHelper(ufc_payload)

# Create the SimApp Pro messaged it needs to update the UFC
simapp_pro_ufc_payload = {
    "args": {
        "FA-18C_hornet": ufcHelper.get_ufc_payload_string(),
    },
    "func": "addCommon",
    "timestamp": 0.00
}

simapp_pro_set_brightness = {
    "args": {
        "0": {
            "109": "0.95"
        }
    },
    "func": "addOutput",
    "timestamp": 0
}

# Send message to SimApp Pro
send_json_udp_message(simapp_pro_ufc_payload)
send_json_udp_message(simapp_pro_set_brightness)


def button_bit_checker(data):
    data_bit_representation = ' '.join(format(byte, '08b') for byte in data)
    #Run through each button, read the button_id and use the usb data to see if it is being pressed
    #print(data_bit_representation)
    
    for x, button_info in buttons.items():
        button_id = button_info["ID"] - 1
        byte = button_id // 8
        bit = button_id % 8

        button_byte = data[byte+1]
        button_bit = (button_byte >> bit) & 1
        button_info["cur_State"] = button_bit

    return()

def set_menu_state(menu_pressed):
    global menu_state
    
    if menu_pressed == "AP":
        menu_state = 1
        ufc_list = ["","","RETN","FOLL","POSI","1","1","1","F","I","1"]

    elif menu_pressed == "IFF":
        menu_state = 2
        ufc_list = ["NXTG","PRTG","NXHO","PRHO","HIGH","1","1","","T","G","1"]

    elif menu_pressed == "TCN":
        menu_state = 3
        ufc_list = ["FREE","DEF","TGT","HOLD","","1","1","2","F","I","1"]

    elif menu_pressed == "ILS":
        menu_state = 4
        ufc_list = ["GXY","SYS","NEXT","CRUI","JUMP","1","1","","N","V","1"]
            
    elif menu_pressed == "DL":
        menu_state = 5
        ufc_list = ["WG-1","WG-2","WG-3","WGNV","WG-T","1","1","","W","G","1"]

    elif menu_pressed == "ON_OFF":
        menu_state = 7
        ufc_list = ["CARG","NVG","LAND","","MODE","1","1","","O","N","1"]

    
        
    ufc_payload = {
        "option1": ufc_list[0], 
        "option2": ufc_list[1],
        "option3": ufc_list[2],
        "option4": ufc_list[3],
        "option5": ufc_list[4],
        "com1": ufc_list[5],
        "com2": ufc_list[6],
        "scratchPadNumbers": ufc_list[7],
        "scratchPadString1": ufc_list[8],
        "scratchPadString2": ufc_list[9],
        "selectedWindows": [ufc_list[10]]
    }

    simapp_pro_set_brightness = {
    "args": {
        "0": {
            "109": "0.95"
        }
    },
    "func": "addOutput",
    "timestamp": 0
    }
    
    ufcHelper = UFCSimAppProHelper(ufc_payload)
    simapp_pro_ufc_payload = {
        "args": {
            "FA-18C_hornet": ufcHelper.get_ufc_payload_string(),
        },
        "func": "addCommon",
        "timestamp": 0.00
    }

    send_json_udp_message(simapp_pro_ufc_payload)
    send_json_udp_message(simapp_pro_set_brightness)


def check_button_presses():
    usb_data = gamepad.read(64)

    if usb_data:
        button_bit_checker(usb_data)

        for button_name, button_info in buttons.items():
            # Check for a new press (transition from 0 to 1)
            if button_info["cur_State"] == 1 and button_info["prev_State"] == 0:
                print(button_name)
                if button_name in menu_items:
                    pass
                    set_menu_state(button_name)

            # Update previous state to current state after checking
            button_info["prev_State"] = button_info["cur_State"]  
        
        
while True:
    check_button_presses()
    sleep(0.2)    

    









