Sonicare toothbrush BLE info via ESPHome BLE Client

Toothbrush must be active to read data. It will connect when powered on, when the brushing mode is changed, or for a short period of time when placed on the charger. 
When disconnected, states in Home Assistant with show `Unavailable` unless ESPHome components are set up to represent last known value or reset to a default initial value.

Battery:
```
service_uuid: 180F
characteristic_uuid: 2A19
```

Active time in seconds:
```
service_uuid: 477ea600-a260-11e4-ae37-0002a5d50002
characteristic_uuid: 477ea600-a260-11e4-ae37-0002a5d54090
```

Handle state:
```
service_uuid: 477ea600-a260-11e4-ae37-0002a5d50001
characteristic_uuid: 477ea600-a260-11e4-ae37-0002a5d54010
```
```
0x00 - off
0x01 - standby
0x02 - on
0x03 - charging
0x04 - shutdown
0x05 - validate
0x06 - ?
0x07 - lights out
```




