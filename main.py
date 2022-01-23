from machine import Pin
from time import sleep, sleep_ms
from i2c_responder import I2CResponder
from machine import UART

def start_uart():
    uart = UART(0, 115200)
    print(uart)
    return uart

def uart_send(serial, uartdata):
  uartdata = str(uartdata)
  serial.write(uartdata.encode('utf-8'))
  return 0

def flash(led, count):
    j = 0
    while j < count:
        led.on()
        sleep_ms(200)
        led.off()
        sleep_ms(200)
        j += 1

uart = start_uart()

I2C_FREQUENCY = 100000

RESPONDER_I2C_DEVICE_ID = 0
RESPONDER_ADDRESS = 0x41
GPIO_RESPONDER_SDA = 16
GPIO_RESPONDER_SCL = 17

led = Pin(25, Pin.OUT)

led.off()

buffer_in = []
buffer_out = []

# -----------------
# Initialize Responder
# -----------------
i2c_port = I2CResponder(RESPONDER_I2C_DEVICE_ID, sda_gpio=GPIO_RESPONDER_SDA, scl_gpio=GPIO_RESPONDER_SCL, responder_address=RESPONDER_ADDRESS)

i = 0

while True:
    if i2c_port.write_data_is_available():
        flash(led, 2)
        sleep_ms(500)
        buffer_in = i2c_port.get_write_data(max_size=2)
        print("Responder: Received I2C WRITE data: {}".format(buffer_in))
        uart_send(uart, "Responder: Received I2C WRITE data: ")
        uart_send(uart, buffer_in)
        
        for value in buffer_in:
            buffer_out.append(value + 1)
        print(buffer_out)
        uart_send(uart, "Created buffer out ")
        uart_send(uart, buffer_out)
    
    if len(buffer_out) > 0:
        if i2c_port.read_is_pending:
            print("Sending data {}".format(buffer_out))
            uart_send(uart, "Sending data ")
            uart_send(uart, buffer_out)
            uart_send(uart, "\n")
            flash(led, 3)
            sleep_ms(500)
            
            for value in buffer_out:
                i2c_port.put_read_data(value)
            
            print("Sent data {}".format(buffer_out))
            uart_send(uart, "Sent data ")
            uart_send(uart, buffer_out)
            uart_send(uart, "\n")

            buffer_out = []

    sleep(1)
    flash(led, 1)

    i += 1

    serialdata = uart.read()
    print(serialdata)
    if serialdata == b'q':
        print("quitting")
        break
    
    uart_send(uart, "Looping\n")
    print("looping")