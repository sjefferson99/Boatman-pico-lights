from machine import Pin
from i2c_responder import I2CResponder
from time import sleep, sleep_ms
from machine import UART

global debugEnable
debugEnable = False

#Deals with debug messages appropriately
def debug(message):
    #TODO Support UART output (unsure if toggle signalk/debug or put debug into signalk format)
    if debugEnable:
        print(message)

#Flashes configured LED pin passed
def flash(led, count, pause=1):
    j = 0
    while j < count:
        led.on()
        sleep_ms(pause)
        led.off()
        sleep_ms(pause)
        j += 1

def start_serial():
    serial = UART(0, 115200)
    print(serial)
    return serial

def send_serial(serial, serialdata):
  serial.write(serialdata.encode('utf-8'))
  return 0

#Read I2C if data available - return data or False if no data
def read_i2c(i2c_port):
    if i2c_port.write_data_is_available():
        flash(led, 2, 1)

        buffer_in = []
        buffer_in = i2c_port.get_write_data(max_size=9)
        debug("Responder: Received I2C WRITE data:" + buffer_in)
        
        return buffer_in
    
    else:
        return False

#Try and send data on I2C bus
def i2c_send(i2c_port, send_data):
    if i2c_port.read_is_pending:
        flash(led, 3, 1)

        debug("Sending data: " + send_data)
        
        for value in send_data:
            i2c_port.put_read_data(value)
        
        debug("Sent data: " + send_data)

        return 0
    
    else:
        return -1

#Init UART
debug("Init UART")
serial = start_serial()

#Config I2C
I2C_FREQUENCY = 100000

RESPONDER_I2C_DEVICE_ID = 0
RESPONDER_ADDRESS = 0x41
GPIO_RESPONDER_SDA = 16
GPIO_RESPONDER_SCL = 17

# Initialize I2C Responder
debug("Init I2C")
i2c_port = I2CResponder(RESPONDER_I2C_DEVICE_ID, sda_gpio=GPIO_RESPONDER_SDA, scl_gpio=GPIO_RESPONDER_SCL, responder_address=RESPONDER_ADDRESS)

#Init LED
debug("Init LED")
led = Pin(25, Pin.OUT)
flash(led, 1)
led.off()

#TODO default led-pwm config

#Main program loop
debug("Starting program loop")
while True:
    #check for I2C data
    i2c_data = read_i2c(i2c_port)
    if i2c_data:
        debug("I2C data read into buffer")
        #TODO some command parser - return data as needed

    #TODO Setup lights
    #TODO configure lights
    
    #Check for quit command on UART
    serialdata = serial.read()

    if serialdata == b'quit':
        debug("quitting")
        break
    
    debug("looping")