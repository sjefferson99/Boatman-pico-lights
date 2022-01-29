from machine import Pin
from i2c_responder import I2CResponder
from time import sleep, sleep_ms
from machine import UART
from machine import PWM

global debugEnable
#debugEnable = False
debugEnable = True

#100% on duty value
global max_duty
max_duty = 65025

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
    serial = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
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

#Configure duties for a group
def set_group_duties(group, duty=max_duty):
    for led in group:
        led_duty[led] = duty

#Set PWM config
def set_led_duties(leds, led_duty):
    for led in leds:
        leds[led].duty_u16(led_duty[led])
        
        if debugEnable:
            print ("\nSetting LED to value")
            print (led)
            print (led_duty[led])

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
debug("Init board LED")
led = Pin(25, Pin.OUT)
flash(led, 1)
led.off()

#LED-pwm config
print("init external LEDs")
ext_led1 = PWM(Pin(0))
ext_led1.freq(1000)
ext_led2 = PWM(Pin(1))
ext_led3 = PWM(Pin(2))
ext_led3.freq(1000)
ext_led4 = PWM(Pin(3))
ext_led5 = PWM(Pin(6))
ext_led5.freq(1000)
ext_led6 = PWM(Pin(7))
ext_led7 = PWM(Pin(8))
ext_led7.freq(1000)
ext_led8 = PWM(Pin(9))
ext_led9 = PWM(Pin(10))
ext_led9.freq(1000)
ext_led10 = PWM(Pin(11))
ext_led11 = PWM(Pin(12))
ext_led11.freq(1000)
ext_led12 = PWM(Pin(13))
ext_led13 = PWM(Pin(14))
ext_led13.freq(1000)
ext_led14 = PWM(Pin(15))
ext_led15 = PWM(Pin(20))
ext_led15.freq(1000)
ext_led16 = PWM(Pin(21))

leds = {1: ext_led1, 2: ext_led2, 3: ext_led3, 4: ext_led4, 5: ext_led5, 6: ext_led6, 7: ext_led7, 8: ext_led8, 9: ext_led9, 10: ext_led10, 11: ext_led11, 12: ext_led12, 13: ext_led13, 14: ext_led4, 15: ext_led15, 16: ext_led16}

#Define LED groups
led_groups = {"all": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], "all_white": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "all_red": [11, 12], "saloon": [1, 2, 3, 4, 5]}

#Set default LED duties
#TODO maybe a constructor makes this from enabled LEDs and value = 0 or max for default group
led_duty = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0}

#TODO read default group and values from persistent storage/server
#Default selected group
current_group = "saloon"
#Set LEDs in default group on
set_group_duties(led_groups[current_group])

#Configure PWM outputs
set_led_duties(leds, led_duty)

#Main program loop
debug("Starting program loop")
while True:
    #check for I2C data
    i2c_data = read_i2c(i2c_port)
    if i2c_data:
        debug("I2C data read into buffer")
        if i2c_data == "x":
            print("x")
            #read bank and value and update config and PWM
        elif i2c_data == "y":
            print("y")
        else:
            print("Unrecognised command")

    #Check for quit command on UART
    serialdata = serial.read()

    if serialdata == b'quit':
        debug("quitting")
        break
    
    #debug("looping")
