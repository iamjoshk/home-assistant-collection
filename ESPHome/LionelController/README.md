I used Copilot to make an integration for this, as an experiment: https://github.com/iamjoshk/ha_lionel_controller.
It supersedes the need for this ESPHome solution.

---
---

## Quick and Dirty ESPHome BLE Client to control Lionel LionChief locomotives

### Requirements
  + Home Assistant
  + ESPHome
  + ESP32 dev board (more RAM is better)
  + Service UUID for your Lionel locomotive (should be able to get this when setting up the BLE Client component
  + Bluetooth MAC address for your Lionel locomotive
  + To enable and simplify voice assistants, I created two helpers and an automation for limited voice commands.
    + `input_select` (dropdown) helper to select a train speed
    + `input_boolean` (toggle) helper to turn the train on and off
    + automation to press the respective buttons when the train speed was changed and/or the train toggle was turned on or off and keep the state in sync.

### Notes
  + I believe `service_uuid` is dependent upon the locomotive model
    + I have a Pennsylvania Flyer and the `service_uuid` is `e20a39f4-73f5-4bc4-a12f-17d1ad07a961`.
  + `characteristic_uuid` is `08590f7e-db05-467e-8757-72f6faeb13d4`
  + The notify characteristic is `08590f7e-db05-467e-8757-72f6faeb14d3` and this should provide statuses from the locomotive. I did not bother trying to implement this on the first iteration.
    + see: https://github.com/Property404/lionchief-controller/issues/2#issuecomment-1032179876
  + This is a very inelegant solution. There is a lot of refining and improvement that could be done. It is very much "good enough" for now.
  + All command values need `0x` preceding them in the `value` element in the ESPHome yaml.
    + For example, to stop the train, the command is `00 45 00` and this would be `[0x00, 0x45, 0x00]` in the yaml.
  + Updated yaml to use the `select` and `number` components to consolidate the commands for speed and announcements. It also enabled finer speed controls.
    + Unfortunately, in Home Assistant `number` entities are not compatible with Google Assistant (which I use for voice commands around the house). This meant that I had to make a new `input_select`          helper and update my automation to synchronize everything.
  + Updated yaml to include shutdown and reboot switches for the ESP32. 
  + No one else in the house uses it, but it makes me happy! 

### Resources
  + lots of work decoding Lionel's bluetooth signal done previously by [Property404](https://github.com/Property404) here: https://github.com/Property404/lionchief-controller
  + [ESPHome BLE Client component](https://esphome.io/components/ble_client.html)

### Simple Dashboard
 ![Simple train control dashboard](https://github.com/iamjoshk/home-assistant-collection/blob/2607c444ae01e66c7a251e0deb6d01f90a233494/ESPHome/LionelController/Screenshot_20241201-210908~2.png)
  
