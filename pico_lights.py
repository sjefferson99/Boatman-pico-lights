###########################
# I2C Pico light controller
###########################

# Command protocol:
###################

# Commands and data should be sent as a byte array.

# The commands are constructed as a 1 byte command with supplementary data bytes as defined below where required. 
# The pico module will read 8 bytes into the read buffer, so pad remaining data bytes with 0 to ensure no unexpected results.

# 0b00xxxxxx: Reserved
# 0b01xxxxxx: Get/set light values
# 0b01GRIIII 0bDDDDDDDD - set light or light group duty cycle
# G: 1 = Group, 0 = Individual light
# R: 1 = Reset other lights to duty cyle of 0, 0 = update only this target
# IIII = 4 bit Light or Group ID
# DDDDDDDD = 0-255 Duty cycle value 0 = off, 255 = fully on

# 0b1xxxxxxx: Get/set config data
# 0b10000001: Get module ID - Pico lights should return 0b00000010
# 0b10000010: Get version
# 0b10000011: Get group assignments

# I2C command expected data return
##################################

# 0b01xxxxxx: Get/set light values - 1 byte
# 0: Success
# 1: Received reserved command
# 2: Group config out of sync (only on group set command, issue a group sync command)
# Unrecognised get/set config command
# 10: Group ID out of range (only on group set command)
# 20: Duty value out of range
# 30: Group ID not in local config
# 0b10000001: Get module ID - 1 byte - 0b00000010
# 0b10000010: Get version - 1 byte big endian defining payload length - immediate send of version string, decode as ansi string e.g. "0.2.0"
# 0b10000011: Get group assignments - 2 bytes big endian defining payload length - immediate send of JSON of that length that can be fed into python json.loads(). 
# This is a python dictionary for use in set light group command.

from i2c_responder import I2CResponder
from machine import Pin, PWM
from time import sleep_ms
from debug import debugger
from json import dumps, loads

class pico_light_controller:
    
    def __init__(self, debugger: debugger, I2CResponder: I2CResponder, address: int = 0x41) -> None:
        self.debug = debugger
        self.i2c1 = I2CResponder
        self.I2C_address = address
        self.version = str("0.3.0")
        self.moduleID = 0b00000010
        self.set_light_bits = 0b01000000
        self.group_bit = 0b00100000
        self.reset_bit = 0b00010000
        self.module_id_byte = 0b10000001
        self.version_byte = 0b10000010
        self.get_groups_byte = 0b10000011
        self.max_duty = 65025   #100% on duty value
        self.init_leds()
        self.led_groups = {0: {"label": "All", "members": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "duty": 0, "name": ""}, 1: {"label": "All white", "members": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "duty": 0, "name": ""}, 2: {"label": "All red", "members": [10, 11], "duty": 0, "name": ""}, 3: {"label": "saloon", "members": [0, 1, 2, 3, 4], "duty": 0, "name": ""}, "duty": 0, "name": ""}
        self.current_group = 3
        self.set_group_duties(self.led_groups[self.current_group], self.max_duty)
        self.groupConfigInSync = False

    def init_leds(self):
        # data structure
        # leds = [{"pin": pin1, "duty": int, "name": str, "duty": 0, "name": ""}, ...] 

        self.debug.print("init external LEDs")
        self.leds = [
        {"pin": PWM(Pin(0)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(1)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(2)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(3)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(6)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(7)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(8)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(9)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(10)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(11)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(12)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(13)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(14)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(25)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(20)), "duty": 0, "name": ""},
        {"pin": PWM(Pin(21)), "duty": 0, "name": ""},
        ]
             
        for led in self.leds:
            led["pin"].freq(1000)       

    def flash(self, led: Pin, count: int, duration: int = 1) -> None:
        """
        Pass a configured LED output pin to flash a count number of times with on time and pause between flashes of duration ms
        """
        # TODO Data transfer is currently small but if scaled this will bottleneck transfer speed, this should not happen. 
        # Could set a blinker on 2nd core or possibly state machine until data is finished reading
        i = 0
        while i < count:
            led.on()
            sleep_ms(duration)
            led.off()
            if count > 1:
                sleep_ms(duration)
            i += 1

    def read_i2c(self) -> list:
        """
        Checks I2C input buffer and returns a list of 8 bytes if data present, otherwise returns a list 0 length list.
        """
        buffer_in = []
        if self.i2c1.write_data_is_available():

            buffer_in = self.i2c1.get_write_data(max_size=8) #returns list of bytes
                    
        return buffer_in

    def send_i2c(self, send_data: list | bytearray) -> None:
        # TODO create interrupt timer to break out if no read requested in X
        self.debug.print("Entering I2C send")
        self.debug.print("Sending this data: ")
        self.debug.print(str(send_data))
        for value in send_data:
            self.debug.print("Entering I2C send loop")
            while not self.i2c1.read_is_pending():
                pass
            self.i2c1.put_read_data(value)
            self.debug.print("I2C value sent")
        
        # TODO timer based interrupt if read still high to break out of byte mismatch
        # While loop on read still active injects 0s that breaks stuff where no byte mismatch

    def send_i2c_multibyte(self, send_data: bytearray, sizebytes: int) -> None:
        """
        Measures data payload size and sends the data size as the first byte(s). sizebytes defines the number of bytes needed to convey the payload size.
        """
        self.debug.print("Entering multibyte I2C send")
        length = len(send_data)
        lengthData = bytearray((length).to_bytes(sizebytes,"big"))
        self.debug.print("length of data:")
        self.debug.print(str(lengthData))
        self.send_i2c(lengthData)
        self.send_i2c(send_data)
    
    def set_light_duty(self, led: int, duty: int) -> None:
        self.leds[led]["duty"] = duty

        self.set_led_duties()

    def set_group_duties(self, group: dict, duty: int) -> None:
        """
        Sets PWM duties for each light in a group, duty valid values: 0-65025
        """
        if duty > self.max_duty:
            duty = self.max_duty
        
        for led in group["members"]:
            self.leds[led]["duty"] = duty
        
        self.set_led_duties()

    def set_all_zero(self) -> None:
        """
        Sets all light duties to 0 (Turn everything off)
        """
        for led in self.leds:
            led["duty"] = 0

        self.set_led_duties()

    # Set PWM config
    def set_led_duties(self):
        for led in self.leds:
            led["pin"].duty_u16(led["duty"])
            
            if self.debug.enable:
                print ("\nSetting duty for")
                print (led)

    # Set lights or group of lights to duty value
    def set_lights(self, data: list) -> bytearray:
        """
        Set light or group of lights to specifed duty as defined in the lights command protocol
        Returns error code sent on I2C bus
        """
        returnByte = 0
        i2cSendData = []
        command = data[0]
        duty = data[1]
        id = command & 0b00001111
        self.debug.print(str(id))
        ledDuty = int(duty * self.max_duty / 255)
        self.debug.print(duty)
        self.debug.print(str(ledDuty))

        # Clear other duty cycles if reset bit set
        if data[0] & 0b00010000:
            self.debug.print("Clear other duty values")
            self.set_all_zero()
        
        # Group config mode
        if data[0] & 0b00100000:
            self.debug.print("Group config")
            if self.groupConfigInSync:
                self.set_group_duties(self.led_groups[id], ledDuty)
                self.debug.print("Setting group ID")
                self.debug.print(self.led_groups[id])

            # Group config not in sync
            else:
                self.debug.print("ERROR: Group config not in sync")
                returnByte = 3
            
        # Single light config mode
        else:
            self.debug.print("Single light config")
            self.set_light_duty(id, ledDuty)

        if returnByte == 0:
            self.debug.print("Set light command executed successfully")
        
        # Any error in setting light duties
        else:
            self.debug.print("Set command not applied due to error")
            self.debug.print(str(returnByte))

        #Return error code to master on "set" command execution
        i2cSendData=bytearray(returnByte)
        self.send_i2c(i2cSendData)

        return i2cSendData

    def get_set_config(self, data: list) -> bytearray:
        """
        Get or set config relating to the lights module
        Returns data sent on I2C bus
        """
        i2cSendData = []
        #Get module ID
        if data[0] == 0b10000001:
            self.debug.print("Command: Get module ID")
            self.debug.print(str(self.moduleID))
            i2cSendData.append(self.moduleID)
            self.send_i2c(i2cSendData)

        #Get version
        elif data[0] == 0b10000010:
            self.debug.print("Command: Get version")
            self.debug.print(str(self.version))
            i2cSendData = bytearray(self.version, 'utf-8')
            self.send_i2c_multibyte(i2cSendData, 1)
            
        #Get group configs
        elif data[0] == 0b10000011:
            self.debug.print("Command: Get group configs")
            jsonData = dumps(self.led_groups, sort_keys=True)
            self.debug.print(jsonData)
            i2cSendData = bytearray(jsonData, 'utf-8')
            self.send_i2c_multibyte(i2cSendData, 2)
            self.groupConfigInSync = True

        else:
            self.debug.print("Unrecognised get/set config command")
            self.debug.print(str(data))
            i2cSendData=bytearray(3)
            self.send_i2c(i2cSendData)
        
        return i2cSendData
        