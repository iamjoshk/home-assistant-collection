## Project to flash ESPHome on a Sinilink XY-WFUSB.

Resources:
+ https://devices.esphome.io/devices/Sinilink-XY-WFUSB-USB-Switch-Relay
+ https://rudd-o.com/linux-and-free-software/switching-an-usb-load-on-or-off-using-the-sinilink-xy-wfusb-and-esphome
+ https://templates.blakadder.com/sinilink_XY-WFUSB.html

Connect to serial adapter:
  - FTDI 232RL adapter to pads on XY-WFUSB. I used sewing pins inserted through the holes (very tight fit) and then dupont connectors to the ends of the sewing pins.
  - For initial flash used web.esphome.io. On Linux, needed to add user to `tty` and `dialout` groups located in `/etc/group`.
  - Wifi could not be provisioned on the intial flash, so next step was to connect directly to HA ESPHome dashboard to flash. After wifi was set up on the device, OTA flashing was successful.
  
