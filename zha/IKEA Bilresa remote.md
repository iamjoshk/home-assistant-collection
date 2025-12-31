Here are the events:

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
