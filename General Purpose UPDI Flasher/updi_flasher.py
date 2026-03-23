import subprocess, json
from guizero import *
import platform
from glob import glob

default_product_name = 'select product to flash'

with open("products.json") as json_data:
    products = json.load(json_data)
    json_data.close()

product_names = list(map(lambda x: x['name'], products))
product_names.insert(0, default_product_name)

selected_product_name = ''

def set_product(product_name):
    global selected_product_name
    selected_product_name = product_name
    button.enabled = (product_name != default_product_name)

def message(msg, detail, type="Error"):
    app.info(type, msg)

def status(text):
    status_field.value = text

def flash_button_pressed():
    find_port()
    if uart_dev:
        for product in products:
            if product['name'] == selected_product_name:
                flash_product(product)
                return
    
def flash_product(product):
    print(product)
    if set_fuses(product):
        flash_hex(product)

def set_fuses(product):
    status("Setting Fuses")
    uc = product['uc']
    fuses = product['fuses']
    bootloader_cmd = py_cmd + " prog.py -t uart -u " + uart_dev + " -b 230400 -d " + uc + " --fuses " + fuses +  " -aerase -v"
    print(bootloader_cmd)
    bootloader_cmd_list = bootloader_cmd.split(" ")
    result = subprocess.run(bootloader_cmd_list, capture_output=True, text=True)
    print("Error:", result.stderr)
    if len(result.stderr) > 1:
        lines = result.stderr.split('\n')
        last_line = lines[-2:-1] # last but 1 line
        message(f"Failure to set fuses.\n {last_line}", result.stderr)
        status("ERROR setting Fuses")
        return False
    status("Fuses set OK")
    return True

def flash_hex(product):
    status("Setting Fuses")
    uc = product['uc']
    flash_fuses = product['flash_fuses']
    hex = product['hex_file']
    flash_cmd = py_cmd + " prog.py -t uart -u " + uart_dev + " -b 230400 -d " + uc + " --fuses " + flash_fuses + " -f " + hex + " -a write -v"
    print(flash_cmd)
    flash_cmd_list = flash_cmd.split(" ")
    result = subprocess.run(flash_cmd_list, capture_output=True, text=True)
    print("Error:", result.stderr)
    if len(result.stderr) > 1:
        lines = result.stderr.split('\n')
        last_line = lines[-2:-1] # last but 1 line
        status("ERROR FLASHING")
        message(f"Failure to FLASH.\n {last_line}", result.stderr)
    #message("Success", "", type="Status")
    status("Flashing complete")

def find_port():
    global uart_dev, py_cmd
    print(platform.system())
    if platform.system() == 'Darwin':
        # Mac
        py_cmd = "/usr/bin/python3 -u"
        glob_pattern = '/dev/tty.usbserial*'
    else:
        # Pi
        py_cmd = "/usr/bin/python3 -u"
        glob_pattern = '/dev/ttyUSB*'

    port_candidates = glob(glob_pattern)
    if len(port_candidates) < 1:
        message('NO PROGRAMMER ATTACHED', "Check the leads")
        print(glob('/dev/cu.*'))
        uart_dev = None
    else:
        uart_dev = port_candidates[0]

app = App(title="Universal Flasher", layout="grid", width=1100, height=250)
Text(app, text="Product", grid=[0,0])
Combo(app, options=product_names, grid=[1,0], command=set_product)

button = PushButton(app, text="FLASH", grid=[0,2,2,1], width=40, height=3, command=flash_button_pressed)
status_field = Text(app, text="-", grid=[0,3,2,1])
button.enabled = False
button.text_color = "black"
button.tk.config(font="Verdana 30 bold") 
app.display()
