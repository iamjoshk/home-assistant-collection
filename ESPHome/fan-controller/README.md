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

+ Two example yaml configurations are included:
  + [fan-controller.yaml](https://github.com/iamjoshk/home-assistant-collection/blob/main/ESPHome/fan-controller/fan-controller.yaml): uses a lambda to decode the raw RF signals
    + Pro: doesn't require an external components
    + Con: triggers the light on any RF signal that roughly matches the DSC contact sensor's signal. With a noisy RF environment, this could mean false triggers.
      
  + [fan-controller-rtl433.yaml](https://github.com/iamjoshk/home-assistant-collection/blob/main/ESPHome/fan-controller/fan-controller-rtl433.yaml): uses the [rtl_433 decoder component](https://github.com/juanboro/esphome-rtl_433-decoder) to decode only the specific DSC contact sensor I am using for the light switch.
    + Pro: can exclude any RF signals that are not specifically the DSC contact sensor used in the light toggle. No false triggers.
    + Con: uses an external component that could break in future ESPHome releases or if it is archived.
    
+ I am currently (as of Aug 2026) using fan-controller-rtl433.yaml.  
  + I chose to load the external component and not the entire package so I could better control what parts of the component I utilized. Instead of a separate include file for the protocols, I just added the script to the `on_boot` configuration.
  + Since this works kind of like a virtual multi-way switch, I don't really need to capture the state of the contact sensor. I only care that the state changed.
    + For debugging the logic in the lambda for the decoded RF signal, I added a binary sensor to track the state of the contact sensor. This helped me realize that the hourly heartbeat for the sensor was triggering the light.
  + I capture the battery state as a sensor for visibility in HA.
  + I don't need MQTT messages or to generate API events.

+ Since I don't need the full capabilities of rtl_433 and really just need to be able to decode the DSC protocol, I may try using a local lightweight C++ header file for decoding the signal. Maybe in the future.
