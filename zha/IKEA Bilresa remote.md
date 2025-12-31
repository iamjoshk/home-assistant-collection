### ZHA Quirk V2 for Bilresa 2 button remote
https://github.com/iamjoshk/home-assistant-collection/blob/main/zha/custom_zha_quirks/bilresa_v2.py

To use a custom quirk:
1. Add this to your `configuration.yaml` if you don't already have it:
```yaml
zha:
  custom_quirks_path: /config/custom_zha_quirks/ 
```
2. Create a folder in your config folder named `custom_zha_quirks` if you don't already have it
3. Download the quirk and add it to the `custom_zha_quirks` folder.
4. Restart HA

If you previously paired the Bilresa 2 button remote you should NOT need to pair it again. The device should pick up the custom quirk automatically. 

The quirk will add device automation triggers for `press on`, `hold on`, `hold on released`, `press off`, `hold off`, `hold off released`.

### to pair in ZHA
1. In ZHA, add new device
2. On remote, press the center pairing button 4 times
3. Wait for light to blink rapidly
4. Press pairing button 8 times

Here are the events the remote generates:

### press on:
```
event_type: zha_event
data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  device_id: e0c5b8bbd566112fe1966cxxxxxxxxxx
  unique_id: 10:35:97:00:xx:xx:xx:xx:1:0x0006
  endpoint_id: 1
  cluster_id: 6
  command: "on"
  args: []
  params: {}
origin: LOCAL
time_fired: "2025-12-31T02:09:30.701861+00:00"
context:
  id: 01KDS2NQJDHKMS9KVEHXKPSJ1N
  parent_id: null
  user_id: null
```

### hold on:
```
event_type: zha_event
data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  device_id: e0c5b8bbd566112fe1966cxxxxxxxxxx
  unique_id: 10:35:97:00:xx:xx:xx:xx:1:0x0008
  endpoint_id: 1
  cluster_id: 8
  command: move
  args:
    - 0
    - 83
  params:
    move_mode: 0
    rate: 83
    options_mask: null
    options_override: null
origin: LOCAL
time_fired: "2025-12-31T02:09:35.844487+00:00"
context:
  id: 01KDS2NWK41YV3CPN7XH2ZG5AD
  parent_id: null
  user_id: null
```
  #### then
```
event_type: zha_event
data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  device_id: e0c5b8bbd566112fe1966cxxxxxxxxxx
  unique_id: 10:35:97:00:xx:xx:xx:xx:1:0x0008
  endpoint_id: 1
  cluster_id: 8
  command: stop_with_on_off
  args: []
  params: {}
origin: LOCAL
time_fired: "2025-12-31T02:09:36.510604+00:00"
context:
  id: 01KDS2NX7Y1XH1NWPHZ9HCJ13G
  parent_id: null
  user_id: null
```

### press off:
```
event_type: zha_event
data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  device_id: e0c5b8bbd566112fe1966cxxxxxxxxxx
  unique_id: 10:35:97:00:xx:xx:xx:xx:1:0x0006
  endpoint_id: 1
  cluster_id: 6
  command: "off"
  args: []
  params: {}
origin: LOCAL
time_fired: "2025-12-31T02:09:39.243303+00:00"
context:
  id: 01KDS2NZXBQ7JBA8QMRJDHJGNZ
  parent_id: null
  user_id: null
```
### hold off:
```
event_type: zha_event
data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  device_id: e0c5b8bbd566112fe1966cxxxxxxxxxx
  unique_id: 10:35:97:00:xx:xx:xx:xx:1:0x0008
  endpoint_id: 1
  cluster_id: 8
  command: move
  args:
    - 1
    - 83
  params:
    move_mode: 1
    rate: 83
    options_mask: null
    options_override: null
origin: LOCAL
time_fired: "2025-12-31T02:09:41.088693+00:00"
context:
  id: 01KDS2P1Q0SB6CDVX4HMWRHREQ
  parent_id: null
  user_id: null
```
  #### then
```
event_type: zha_event
data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  device_id: e0c5b8bbd566112fe1966cxxxxxxxxxx
  unique_id: 10:35:97:00:xx:xx:xx:xx:1:0x0008
  endpoint_id: 1
  cluster_id: 8
  command: stop_with_on_off
  args: []
  params: {}
origin: LOCAL
time_fired: "2025-12-31T02:09:42.731495+00:00"
context:
  id: 01KDS2P3ABQPXW00432NMBK0GX
  parent_id: null
  user_id: null
```

### triggers
And for example, you could use the press on event like this as an automation trigger:
```
trigger: event
event_type: zha_event
event_data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  command: "on"
```
and hold on like this:
```
trigger: event
event_type: zha_event
event_data:
  device_ieee: 10:35:97:00:xx:xx:xx:xx
  command: move
  args:
    - 0
    - 83
  params:
    move_mode: 0
    rate: 83
```
Basically, you just need to give it enough information to make the event unique and identifiable as a trigger.


### device signature:
```
{
  "node_descriptor": {
    "logical_type": 2,
    "complex_descriptor_available": 0,
    "user_descriptor_available": 0,
    "reserved": 0,
    "aps_flags": 0,
    "frequency_band": 8,
    "mac_capability_flags": 128,
    "manufacturer_code": 4476,
    "maximum_buffer_size": 127,
    "maximum_incoming_transfer_size": 242,
    "server_mask": 11776,
    "maximum_outgoing_transfer_size": 242,
    "descriptor_capability_field": 0
  },
  "endpoints": {
    "1": {
      "profile_id": "0x0104",
      "device_type": "0x0006",
      "input_clusters": [
        "0x0000",
        "0x0001",
        "0x0003",
        "0x0020"
      ],
      "output_clusters": [
        "0x0003",
        "0x0004",
        "0x0005",
        "0x0006",
        "0x0008",
        "0x1000"
      ]
    }
  },
  "manufacturer": "IKEA of Sweden",
  "model": "09B9",
  "class": "zigpy.device.Device"
}
```
