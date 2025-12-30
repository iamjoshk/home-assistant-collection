# OMG Ceiling Fan Control

## Update Dec 2025:
- Updated the format of my fan and fan light template entities because legacy template entities are being deprecated in 2026.6.

- Combined the fan and light templates into a single yaml example due to the new template entity format.
   
- Took the opportunity to add direction control, which had been on my list for nearly two years (apparently). The fan just toggles direction, so I created a input boolean helper to fake the direction setting for the template. Then in the `set_direction` part of the template, I added an action to toggle the helper after the commands for toggling the direction.

- The [C1101 component](https://esphome.io/components/cc1101/) was just added to ESPHome in 2025.12.0, so I may revisit using ESPHome for fan control again in the future. This existing set up works 95% of the time, but OpenMQTTGateway is a bit of a black box for me and this is my only OMG device. I would prefer to consolidate this to ESPHome. But that would be another future to-do.

---
## Notes
OpenMQTTGateway (https://docs.openmqttgateway.com/) project to add a ceiling fan with lights using RF remote to Home Assistant.

+ Remote uses frequency 303.94MHz to transmit codes.

+ Several attempts were made to use ESPHome for this solution, but ultimately, it was set up using OpenMQTTGateway.
+ Ceiling fan was a cheap low profile remote-only fan from Home Depot, under their brand Home Decorators. FCC info: https://fccid.io/Y7ZDL4112T

+ Hardware used:
  + ESP32dev board
  + CC1101 / E07-M1101D V2 for rx/tx

+ Software:
  + OpenMQTTGateway
    + Firmware: esp32dev-multi_receiver-pilight
    + RF active: 2
    + Frequency	303.9
   
Notes: This was a struggle to get set up. I really wanted this to work through ESPHome, but I just couldn't get the transmitter set up correctly. It may work for others, and I used the great work by dbuezas (https://github.com/dbuezas/esphome-cc1101) as a starting point. I made some changes to `cc11001.h` that I will share [here](https://github.com/iamjoshk/home-assistant-collection/tree/main/OpenMQTTGateway/archive). Unfortunately, I stupidly deleted my ESPHome yaml in a fit of frustration. I will share the pin configurations here, as well.

Update Dec 2025: There is now a C1101 component in ESPHOME: https://esphome.io/components/cc1101/



