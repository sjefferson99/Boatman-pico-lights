# Boatman-pico-lights

## Overview
The Boatman pico lights module forms part of a wider Boatman ecosystem documented in the [Boatman project repository](https://github.com/sjefferson99/Boatman-project)

The hardware detailed below is built around the relatively new Raspberry Pi Pico microprocessor and runs micropython.

The module leverages all of the 16 onboard PWM drivers which should be fed into LED driver circuitry to address the current requirements of LED strips.
Control of the module is performed by a custom protocol on the I2C bus, using a community library to have the pico present as an I2C slave on the bus.
A pico hub module performs the role of I2C master and depending on the hub will have a variety of ways to drive th lights module config.

### Hub modules
- [Pico wired serial UART hub](https://github.com/sjefferson99/Boatman-pico-uart-hub)
- [Pico wireless hub](https://github.com/sjefferson99/Boatman-pico-wireless-hub)

## I2C command reference
(TBC)

## Hardware
- Raspberry Pi Pico: [Pi hut pico](https://thepihut.com/products/raspberry-pi-pico)
- MOSFET PWM Drivers: [Amazon Mosfet with connectors on PCB](https://www.amazon.co.uk/gp/product/B07QVZK39F/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1)
