## Overview
Describes how to set up rtl_433 and MQTT to utilize an SDR dongle to capture RF transmissions for various sensors

## Activities
+ Install rtl_433 add on
+ Install Mosquitto MQTT Broker add on
+ Install the MQTT integration
+ Set up sensors
+ Optional split configuration file set up

## INSTALL rtl_433 add on
In Home Assistant

1. Install rtl_433 add on
    - https://github.com/pbkhrv/rtl_433-hass-addons
        > Note: this repo is no longer active and has been forked by @catduckgnaf at https://github.com/catduckgnaf/rtl_433_ha. They are also working on a new auto discovery script.
        > Using this new repo means changing your `rtl_433.conf.template` file to use the `rtl_433.conf` format found in the new repo. 
    - run once to create `rtl_433.conf.template` in the `config/rtl_433` folder
    - modify the `rtl_433.conf.template` file to configure rtl_433 to output data
      - more info here on config options: https://github.com/merbanan/rtl_433/blob/master/conf/rtl_433.example.conf
      
      for example:
```
#identifies device, required if using more than one SDR dongle
device 0

#specifies output and included data
output mqtt://${host}:${port},user=${username},pass=${password},retain=${retain},devices=homeassistant/devices/[/model][/id],events=homeassistant/events[/model][/id],states=homeassistant/states[/model][/id]
report_meta time:iso:usec:tz
report_meta level
report_meta protocol

#converts units to desired format
convert customary

#outputs table of device results to the log
output kv

#specifies the frequency, can use more than one but then `hop_interval` in seconds is required
frequency 433.92M

#protocols to avoid scanning for, this is the default list of TPMS (tire pressure sensors) to exclude. Helps eliminate device noise from passing cars.
protocol -59
protocol -60
protocol -82
protocol -88
protocol -89
protocol -90
protocol -95
protocol -110
protocol -123
protocol -140
protocol -156
protocol -168
protocol -180
protocol -186
protocol -201
protocol -203      
```

   
## Install Mosquitto MQTT broker add on
2. Install Mosquitto Broker add on
    - create user for MQTT in HA user setup
    - start add on

## Install MQTT integration
3. Install MQTT integration

## Identify and set up your sensors
4. Run rtl_433 add on and review log
    - output should be similar to this:
```
s6-rc: info: service s6rc-oneshot-runner: starting
s6-rc: info: service s6rc-oneshot-runner successfully started
s6-rc: info: service fix-attrs: starting
s6-rc: info: service fix-attrs successfully started
s6-rc: info: service legacy-cont-init: starting
s6-rc: info: service legacy-cont-init successfully started
s6-rc: info: service legacy-services: starting
s6-rc: info: service legacy-services successfully started
Starting rtl_433 with rtl_433.conf...
[rtl_433] rtl_433 version 22.11 branch  at 202211191645 inputs file rtl_tcp RTL-SDR
[rtl_433] Use -h for usage help and see https://triq.org/ for documentation.
[rtl_433] Publishing MQTT data to core-mosquitto port 1883
[rtl_433] Publishing device info to MQTT topic "homeassistant/devices/[/model][/id]".
[rtl_433] Publishing events info to MQTT topic "homeassistant/events[/model][/id]".
[rtl_433] Publishing states info to MQTT topic "homeassistant/states[/model][/id]".
[rtl_433] Registered 176 out of 223 device decoding protocols [ 1-4 8 11-12 15-17 19-23 25-26 29-36 38-58 63 67-71 73-81 83-87 91-94 96-100 102-105 108-109 111-116 119 121 124-128 130-139 141-149 151-155 157-161 163-167 170-175 177-179 181-185 187-197 199 202 204-215 217-223 ]
[rtl_433] Found Rafael Micro R820T tuner
[rtl_433] Exact sample rate is: 250000.000414 Hz
[rtl_433] [R82XX] PLL not locked!
[rtl_433] Sample rate set to 250000 S/s.
[rtl_433] Tuner gain set to Auto.
[rtl_433] Tuned to 433.920MHz.
[rtl_433] Allocating 15 zero-copy buffers
[rtl_433] baseband_demod_FM: low pass filter for 250000 Hz at cutoff 25000 Hz, 40.0 us
[rtl_433] MQTT Connected...
[rtl_433] MQTT Connection established.
[rtl_433] _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
[rtl_433] time      : 2023-02-22T16:08:44.481854-0500        Protocol  : 42
[rtl_433] model     : Hideki-TS04  Rolling Code: 9
[rtl_433] Channel   : 1            Battery   : 1             Temperature: 71.6 F       Humidity  : 52 %          Integrity : CRC
[rtl_433] Modulation: ASK          Freq      : 433.9 MHz
[rtl_433] RSSI      : -0.1 dB      SNR       : 25.5 dB       Noise     : -25.6 dB
[rtl_433] _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
[rtl_433] time      : 2023-02-22T16:08:44.624758-0500        Protocol  : 42
[rtl_433] model     : Hideki-TS04  Rolling Code: 9
[rtl_433] Channel   : 1            Battery   : 1             Temperature: 71.6 F       Humidity  : 52 %          Integrity : CRC
[rtl_433] Modulation: ASK          Freq      : 433.9 MHz
[rtl_433] RSSI      : -0.1 dB      SNR       : 26.0 dB       Noise     : -26.1 dB
[rtl_433] _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
[rtl_433] time      : 2023-02-22T16:08:44.768021-0500        Protocol  : 42
[rtl_433] model     : Hideki-TS04  Rolling Code: 9
[rtl_433] Channel   : 1            Battery   : 1             Temperature: 71.6 F       Humidity  : 52 %          Integrity : CRC
[rtl_433] Modulation: ASK          Freq      : 433.9 MHz
[rtl_433] RSSI      : -0.1 dB      SNR       : 24.5 dB       Noise     : -24.7 dB
```

5. Find devices you want to capture
```
[rtl_433] _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
[rtl_433] time      : 2023-02-22T16:08:44.768021-0500        Protocol  : 42
[rtl_433] model     : Hideki-TS04  Rolling Code: 9
[rtl_433] Channel   : 1            Battery   : 1             Temperature: 71.6 F       Humidity  : 52 %          Integrity : CRC
[rtl_433] Modulation: ASK          Freq      : 433.9 MHz
[rtl_433] RSSI      : -0.1 dB      SNR       : 24.5 dB       Noise     : -24.7 dB
```

6. Go to MQTT integration and click `Configure`

7. Go to `Listen to a topic` and add the topic format you specified in `rtl_433.conf.template` *or* if you did not, then use the default from the config and click `Start Listening`

8. Find an event for a device you want to capture.
```
{
    "time": "2023-02-22T16:13:02.769022-0500",
    "protocol": 42,
    "model": "Hideki-TS04",
    "id": 9,
    "channel": 1,
    "battery_ok": 1,
    "temperature_F": 71.6,
    "humidity": 52,
    "mic": "CRC",
    "mod": "ASK",
    "freq": 433.916,
    "rssi": -0.104359,
    "snr": 26.1292,
    "noise": -26.2336
}
```

9. In your `configuration.yaml`, create MQTT sensors.
    - the example below will create a device called `Attic Sensor` with entities `Attic Temperature` `Attic Humidity` and `Attic Sensor Battery`. The data in `device` must be the same for each entity for them to be grouped together in a single device. Note that `Attic Temperature` and `Attic Humidity` are [`MQTT sensors`](https://www.home-assistant.io/integrations/sensor.mqtt/) and  `Attic Sensor Battery` is a [`MQTT binary_sensor`](https://www.home-assistant.io/integrations/binary_sensor.mqtt/). 
```
mqtt:
  sensor:        
  - name: "Attic Temperature"
    state_topic: "homeassistant/events/Hideki-TS04/9"
    unique_id: attic_temperature
    qos: 0
    force_update: true
    unit_of_measurement: "°F"
    value_template: |
      {{ value_json.temperature_F }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }   
 
  - name: "Attic Humidity"
    state_topic: "homeassistant/events/Hideki-TS04/9"
    unique_id: attic_humidity
    qos: 0
    force_update: true
    unit_of_measurement: "%"
    value_template: |
      {{ value_json.humidity }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }
        
  binary_sensor:
  - name: "Attic Sensor Battery"
    state_topic: "homeassistant/events/Hideki-TS04/14"
    unique_id: attic_battery
    device_class: battery
    qos: 0
    force_update: true
    payload_on: 0
    payload_off: 1
    value_template: |
      {{ value_json.battery_ok }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }
```

10. Use your newly created sensor in your dashboards!

> One other thing to note: In my example, the Hideki-TS04 has a `rolling id`, which means that every time the batteries are changed, the `state_topic` and `identifiers` will need to be updated with the new `rolling id`. Not ideal, but I had this sensor laying around and batteries last for a long time in these devices. (I just replaced batteries that were over 7 years old in this device.)


## Optional split configuration file set up

> If your `configuration.yaml` is getting out of hand, you can split it up into several files. Some of these may already be split out, like `automations.yaml` and `scripts.yaml`. More information can be found here: [Splitting up the configuration](https://www.home-assistant.io/docs/configuration/splitting_configuration/). Below are basic steps for splitting out your `MQTT` configuration, specifically for this `rtl_433` scenario.

Instead of listing all of your sensors in your `configuration.yaml` like in step 9 above, you can create a new, separate file in the same directory as `configuration.yaml` and add a reference to that file in `configuration.yaml`.

1. Create a new file in the same directory as your `configuration.yaml` file. Let's call it `mqtt_rtl.yaml`. How you do this is up to you, using the `SSH & Web Terminal` or `Samba share` add ons or some other solution.

2. In your `configuration.yaml` file, copy everything under `mqtt:` but NOT `mqtt:`
> when I first set this up, I simply commented out all of the sensor lines in my `configuration.yaml` file in case I made a mistake. You could also create a back up version of file to easily revert, whatever you want.

```
mqtt: #DO NOT COPY THIS LINE#
  sensor:        
  - name: "Attic Temperature"
    state_topic: "homeassistant/events/Hideki-TS04/9"
    unique_id: attic_temperature
    qos: 0
    force_update: true
    unit_of_measurement: "°F"
    value_template: |
      {{ value_json.temperature_F }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }   
 
  - name: "Attic Humidity"
    state_topic: "homeassistant/events/Hideki-TS04/9"
    unique_id: attic_humidity
    qos: 0
    force_update: true
    unit_of_measurement: "%"
    value_template: |
      {{ value_json.humidity }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }
        
  binary_sensor:
  - name: "Attic Sensor Battery"
    state_topic: "homeassistant/events/Hideki-TS04/14"
    unique_id: attic_battery
    device_class: battery
    qos: 0
    force_update: true
    payload_on: 0
    payload_off: 1
    value_template: |
      {{ value_json.battery_ok }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }
```

3. Paste the sensors in your `mqtt_rtl.yaml` file.
```
  sensor:        
  - name: "Attic Temperature"
    state_topic: "homeassistant/events/Hideki-TS04/9"
    unique_id: attic_temperature
    qos: 0
    force_update: true
    unit_of_measurement: "°F"
    value_template: |
      {{ value_json.temperature_F }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }   
 
  - name: "Attic Humidity"
    state_topic: "homeassistant/events/Hideki-TS04/9"
    unique_id: attic_humidity
    qos: 0
    force_update: true
    unit_of_measurement: "%"
    value_template: |
      {{ value_json.humidity }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }
        
  binary_sensor:
  - name: "Attic Sensor Battery"
    state_topic: "homeassistant/events/Hideki-TS04/14"
    unique_id: attic_battery
    device_class: battery
    qos: 0
    force_update: true
    payload_on: 0
    payload_off: 1
    value_template: |
      {{ value_json.battery_ok }}
    device: {
        model: "Hideki-TS04",
        identifiers: ["9"],
        name: "Attic Sensor",
        suggested_area: "Attic"
        }
```

4. That leaves a single line for MQTT in your `configuration.yaml`. There you update it to use an include statement that references your `mqtt_rtl.yaml` file.
```
mqtt: !include mqtt_rtl.yaml
```

5. Don't forget to save both the `configuration.yaml` and `mqtt_rtl.yaml` files. Then check your configuration in Developer Tools -> YAML -> Check and Restart -> Check Configuration. If no errors, click restart! Upon completion of the restart, you should see no difference in how your sensors appear in HA.
