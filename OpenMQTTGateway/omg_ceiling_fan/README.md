# OMG Ceiling Fan Control

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

## To Do:
 + ~~add fan controla~~
 + coordinate states in HA
   + fan - uses the state value sent in the MQTT payload plus a contact sensor in the fan housing to determine if the fan is moving.
   + light - uses the state value sent in the MQTT payload to determine the state of the light. Added a contact sensor connected to a light switch toggle to provide a dedicated physical switch. Still possible for this to get out of sync.

