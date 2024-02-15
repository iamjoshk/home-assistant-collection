## Contact Sensor Light Switch Toggle

The DSC Security contact sensor uses a magnet to close the connection. There are terminal connections onboard the PCB, so you can attach wires and run them to an alternative device to complete the circuit. If you connect the terminals to a light switch, you can create a remote control that can then be mounted in a wall like a regular light switch.

![light-switch-sm](https://github.com/iamjoshk/home-assistant-collection/assets/28068117/73a26165-c24b-43ff-9e49-b138689b5c03)

To utilize the switch, I created an MQTT binary sensor in Home Assistant.

Example payload:
```
{
  "time": "2024-02-14T21:03:05.038210-0500",
  "protocol": 23,
  "model": "DSC-Security",
  "id": 2700721,
  "closed": 1,
  "event": 1,
  "tamper": 1,
  "battery_ok": 1,
  "xactivity": 1,
  "xtamper1": 1,
  "xtamper2": 0,
  "exception": 0,
  "esn": "2935b1",
  "status": 162,
  "status_hex": "a2",
  "mic": "CRC",
  "mod": "ASK",
  "freq": 433.92253,
  "rssi": -4.14115,
  "snr": 21.01335,
  "noise": -25.1545
}
```

Example sensors based on payload:

```
  - name: "Toggle"
    state_topic: "homeassistant/events/DSC-Security/2700721"
    unique_id: living_room_fan_light_toggle
    qos: 0
    force_update: true
    payload_on: 1
    payload_off: 0
    value_template: |
      {{ value_json.closed }}
    device: {
        model: "DSC-Security",
        identifiers: ["2700721"],
        name: "Living Room Fan Light",
        suggested_area: "Living Room"
        }

  - name: "Battery"
    state_topic: "homeassistant/events/DSC-Security/2700721"
    unique_id: living_room_fan_light_switch_battery
    device_class: battery
    qos: 0
    force_update: true
    payload_on: 0
    payload_off: 1
    value_template: |
      {{ value_json.battery_ok }}
    device: {
        model: "DSC-Security",
        identifiers: ["2700721"],
        name: "Living Room Fan Light",
        suggested_area: "Living Room"
        }
```

Including the `device` parameters creates a device that groups the two entities together.

Then I created an automation that toggles a light on and off. Since I don't care about the actual state of this toggle compared to the state of the light, the triggers I set up are on state change from `on` to `off` and vice versa. I do not want the light to toggle on and off when the state changes to and from `unknown` and `unavailable`. 

Mounted the light box in the wall and it looks just like a regular light switch. Easy to take the face plate off to change the battery on the contact sensor, but I expect that it'll last at least a year or two before it needs to be changed.
