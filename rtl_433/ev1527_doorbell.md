## Generic RF doorbell using an EV1527

I ordered a [cheap 433MHz doorbell](https://www.amazon.com/gp/product/B09JVS7ZNL). Unfortunately, the transmission was not a decoded by `rtl_433` automatically so I needed to set up a flex decoder.
I disassembled the button and found the transmitter chip on the PCB. It's a cheap EV1527.

![share_1548447214581607946](https://github.com/iamjoshk/home-assistant-collection/assets/28068117/97b7ed14-95fd-46f0-935e-a8f8f490abf0)

Good news: The EV1527 is very common and there are several confs in the [`rtl_433` repo](https://github.com/merbanan/rtl_433/tree/master/conf).

Bad news: The timings are different for every device which is pretty annoying and this is why it requires a flex decoder instead of a pre-configured protocol.

The right way to get the best flex decoder settings is to use rtl_433 to analyze the signal for your specific device and then set your flex decoder appropriately.

I'm using rtl_433 with a Home Assistant add-on, so the easiest thing for me to do was to add `analyze_pulses true` in the `rtl_c433.conf` file, restart the add-on and then reviewing the log after pressing the doorbell button.

I've got a bunch of 433MHz devices and the console log doesn't provide a lot of space, so there is a little bit of timing your presses and log refreshes. Pretty sure you can output the results of analyze_pulses to a log file, but I am lazy when it comes to this kind of thing. Path of least resistance and all.

Anyway, this was the result in the console log:
```
Detected OOK package	2024-02-16T14:25:06.750262-0500
Analyzing pulses...
Total count: 1200,  width: 1140.84 ms		(1140842 S)
Pulse width distribution:
 [ 0] count:  528,  width:  163 us [148;195]	( 163 S)
 [ 1] count:  672,  width:  544 us [483;618]	( 544 S)
Gap width distribution:
 [ 0] count:   48,  width: 5663 us [5635;5683]	(5663 S)
 [ 1] count:  480,  width:  574 us [555;587]	( 574 S)
 [ 2] count:  671,  width:  210 us [193;224]	( 210 S)
Pulse period distribution:
 [ 0] count:   48,  width: 5826 us [5797;5840]	(5826 S)
 [ 1] count: 1151,  width:  747 us [677;817]	( 747 S)
Pulse timing distribution:
 [ 0] count:  617,  width:  168 us [148;204]	( 168 S)
 [ 1] count: 1152,  width:  557 us [483;618]	( 557 S)
 [ 2] count:   48,  width: 5663 us [5635;5683]	(5663 S)
 [ 3] count:  583,  width:  211 us [204;224]	( 211 S)
Level estimates [high, low]:  15782,    806
RSSI: -0.2 dB SNR: 12.9 dB Noise: -13.1 dB
Frequency offsets [F1, F2]:     887,      0	(+13.5 kHz, +0.0 kHz)
Guessing modulation: Pulse Width Modulation with multiple packets
view at https://triq.org/pdv/#AAB00B040100A8022D161F00D38255+AAB023042700A8022D161F00D38193939393938193819381939381938193819381818193938255+AAB023040100A8022D161F00D38193939393938193819381939081938193819381818193938255+AAB023040100A8022D161F00D38190939393938193819081909081938193819081818193908255+AAB023040100A8022D161F00D38193909393938190819381939081938193819381818193908255+AAB023040100A8022D161F00D38190909090908190819081909081908190819081818190908255+AAB023040100A8022D161F00D38190909390908190819081909081908190819081818190908255+AAB023040300A8022D161F00D38190909090908190819081909081908190819081818190908255+AAB022040100A8022D161F00D381909090909081908190819090819081908190818181909055
Attempting demodulation... short_width: 163, long_width: 544, reset_limit: 5684, sync_width: 0
Use a flex decoder with -X 'n=name,m=OOK_PWM,s=163,l=544,r=5684,g=588,t=152,y=0'
[pulse_slicer_pwm] Analyzer Device
codes     : {1}8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {25}82a55c8, {24}82a55c
```

Based on this, I added the following to my `rtl_433` config file.

```
decoder {n=doorbell_ev1527,m=OOK_PWM,s=164,l=552,r=5680,g=584,t=152,y=0,repeats>=5,rows>=25,bits=25,countonly,unique,get=@0:{24}:id,get=@0:{25}:channel}
```

>Breaking down the flex decoder that is suggested in the results:
>```
>n = name
>m = modulation
>s = short pulse width
>l = Long pulse width
>r = Reset limit
>g = Gap limit
>t = Tolerance
>y = Sync width
>```
>
>I added these additional parameters based on testing and tweaking:
>```
>repeats = match based on number of times a row repeats
>rows = match based on the number of rows
>bits = match based on number of bits in a row
>countonly = supresses the row details
>unique = supresses duplicate rows
>get=@0:{24}:id = the id of the device
>get=@0:{25}:channel = get the channel, which is helpful if there is more than one button on the device (there isn't on this, but I like data so I kept it).
>```


This got me the following results in the output logs (not the console logs because I forgot to copy those results):
```
{"time" : "2024-02-16T14:21:28.906540-0500", "model" : "doorbell_ev1527", "count" : 14, "num_rows" : 50, "len" : 25, "data" : "0489bc8", "id" : 297404, "channel" : 594809, "mod" : "ASK", "freq" : 433.959, "rssi" : -5.941, "snr" : 3.940, "noise" : -9.881}
```
and
```
{"time" : "2024-02-16T14:20:48.766486-0500", "model" : "doorbell_ev1527", "count" : 6, "num_rows" : 50, "len" : 25, "data" : "82a55c8", "id" : 8562012, "channel" : 17124025, "mod" : "ASK", "freq" : 433.981, "rssi" : -10.555, "snr" : 2.933, "noise" : -13.487}
```

Using this, I set up these [MQTT sensors](https://www.home-assistant.io/integrations/sensor.mqtt/). The state topic and attributes topic is defined in the `rtl_433.conf` file. The `prev_time` attribute shows the previous time the doorbell was rung.
```
#############
#DOORBELLS       
  - name: "Doorbell"
    state_topic: "homeassistant/events/doorbell_ev1527/297404"
    unique_id: front_doorbell_ev1527
    qos: 0
    value_template: |
      {{ value_json.time | as_timestamp | timestamp_custom('%X %D') }}
    json_attributes_topic: "homeassistant/events/doorbell_ev1527/297404"
    json_attributes_template: >
      { 
      "model": {{ value_json.model | to_json }},
      "id": {{ value_json.id | to_json | string }},
      "time": {{ value_json.time | as_timestamp | timestamp_custom('%X %D') | to_json }},
      "prev_time": "{{ state_attr('sensor.front_door_doorbell','time') }}",
      "channel": {{ value_json.channel | to_json }} 
      }
      
    device: {
        model: "doorbell",
        identifiers: ["297404"],
        name: "Front Door",
        suggested_area: "Exterior"
        }
        
        
  - name: "Doorbell"
    state_topic: "homeassistant/events/doorbell_ev1527/8562012"
    unique_id: red_door_doorbell_ev1527
    qos: 0
    value_template: |
      {{ value_json.time | as_timestamp | timestamp_custom('%X %D') }}
    json_attributes_topic: "homeassistant/events/doorbell_ev1527/8562012"
    json_attributes_template: >
      { 
      "model": {{ value_json.model | to_json }},
      "id": {{ value_json.id | to_json | string }},
      "time": {{ value_json.time | as_timestamp | timestamp_custom('%X %D') | to_json }},
      "prev_time": "{{ state_attr('sensor.front_door_doorbell','time') }}",
      "channel": {{ value_json.channel | to_json }}
      }      
    device: {
        model: "doorbell",
        identifiers: ["8562012"],
        name: "Red Door",
        suggested_area: "Exterior"
        }
```

And finally an automation to send a notification when the doorbell is rung. The conditions prevent me from being alerted if I am not home, if the state changes from unavailable or unknown, and if the doorbell has no previous ring time attribute which is mostly important during testing.

```
alias: Doorbell
description: ""
trigger:
  - platform: state
    entity_id:
      - sensor.front_door_doorbell
condition:
  - condition: and
    conditions:
      - condition: state
        entity_id: person.me
        state: home
      - condition: template
        value_template: "{{ states('sensor.front_door_doorbell') != 'unknown' }}"
      - condition: template
        value_template: "{{ states('sensor.front_door_doorbell') != 'unavailable' }}"
      - condition: template
        value_template: "{{ state_attr('sensor.front_door_doorbell','prev_time') != 'None' }}"
action:
  - service: notify.mobile_app_me
    metadata: {}
    data:
      message: Someone is at the front door!
      title: Ding Dong!
      data:
        tag: doorbell
mode: single
```
