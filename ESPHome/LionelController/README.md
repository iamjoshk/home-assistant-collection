## Quick and Dirty ESPHome BLE Client to control Lionel LionChief locomotives

### Requirements:
  + ESPHome
  + ESP32 dev board (more RAM is better)
  + Service UUID for your Lionel locomotive (should be able to get this when setting up the BLE Client component
  + Bluetooth MAC address for your Lionel locomotive

### Resources
  + lots of work decoding Lionel's bluetooth signal done previously by [Property404](https://github.com/Property404) here: https://github.com/Property404/lionchief-controller
  + [ESPHome BLE Client component](https://esphome.io/components/ble_client.html)

### Simple Dashboard
 ![Simple train control dashboard](https://github.com/iamjoshk/home-assistant-collection/blob/2607c444ae01e66c7a251e0deb6d01f90a233494/ESPHome/LionelController/Screenshot_20241201-210908~2.png)
  
