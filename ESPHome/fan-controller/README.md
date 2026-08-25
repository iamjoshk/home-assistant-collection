# ESPHome Controller for RF Ceiling Fan

This is an ESP32 with C1101 controller for a dumb RF ceiling fan and light.
___

### Notes

+ Ceiling fan was a cheap low profile remote-only fan from Home Depot, under their brand Home Decorators. FCC info: https://fccid.io/Y7ZDL4112T
+ Remote uses frequency 303.94MHz to transmit codes.

+ Hardware used:
  + ESP32dev board
  + CC1101 / E07-M1101D V2 for rx/tx
 
+ Physical light control is handled with a paddle switch connected to a contact sensor.
  + https://github.com/iamjoshk/home-assistant-collection/blob/main/rtl_433/contact_sensor_light_switch_toggle.md

+ Everything runs on the ESP32 so if HA is down for some reason, the light and fan will still work.
  
+ Fan and light states persist across ESP32 and HA reboots.

+ Controls accessible via webserver if HA is down.

+ The ESP32-WROOM-32D board I am currently using crashes with the bluetooth proxy enabled, so I have it disabled in the config.
