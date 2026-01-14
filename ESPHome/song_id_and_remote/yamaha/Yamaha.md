## Sending IR codes to the Yamaha RX-386 via remote control in jack using ESPHome.

My late 1990s Yamaha RX-396 stereo receiver does not have a 12v trigger. But it does have remote control in and remote control out jacks that allow daisy chaining multiple components for use with a single remote control. I decided to take advantage of the remote control in jack and send IR codes over wire to the receiver to bring control of the receiver into Home Assistant.

#### List of parts used
- ESP32-WROOM-32D with power supply (Final version uses an ESP32-S3, but this documents the original prototype)
- IR receiver component for discovering the IR codes to use - KY-022
- IR transmitter component for testing codes - KY-005
- BC547 transistor
- 1k ohm resistor (I used 3x 330 ohm resistors)
- 660 ohm resistor (I used 2x 330 ohm resistors)
- monaural 3.5mm jack with terminal end
- dupont connectors for prototype
- breadboard for prototype

### Prototyping
- Information for the remote control in and out connections on the back of the receiver was difficult to find. The receiver is a rather entry level component and it's almost 30 years old. I picked it up for $20 not long ago.
- I was able to piece together that the jacks are unpowered and expect the external remote system to provide the power for the signal. 
- I was pretty certain that it used mono jacks based on various forum posts around other Yamaha receivers.

There are many posts on the HA community forum, reddit, various AV related forums, and other DIY electronics blogs around using IR blasters, a few on sending IR over wire, and even less on specifically Yamaha equipment. Luckily, I have the remote for the receiver.

My first step was to use the ESPHome remote receiver component to discover the codes being used for specific remote buttons. I started with the power button, which on the remote is a toggle. There are discrete codes out there for various units. This will come up later.

I connected a KY-022 IR receiver module to the ESP32, using the following config based on ESPHome [Remote Receiver](https://esphome.io/components/remote_receiver/) component and information from [this HA community forum post](https://community.home-assistant.io/t/faking-an-ir-remote-control-using-esphome/369071).
```yaml
remote_receiver:
  pin:
    number: 26
    inverted: True
  dump: all
```

Pressing the power button on the remote generated codes in the log like these:
```
[23:32:48.522][I][remote.nec:097]: Received NEC: address=0x857A, command=0xE01F command_repeats=1
[23:32:48.522][I][remote.pioneer:149]: Received Pioneer: rc_code_X=0x5E1F
[23:32:48.522][I][remote.pronto:229]: Received Pronto: data=
[23:32:48.523][I][remote.pronto:237]: 0000 006D 0022 0000 0158 00AE 0014 0017 0014 0042 0014 0017 0014 0042 0014 0042 0014 0043 0014 0042 0014 0017 0014 0042 0014 0016 0015 0041 0014 0016 0015 0017 0013 0016 0015 0017 0014 0042 0014 0042 0014 0042 0015 0042 0014 0043 
[23:32:48.523][I][remote.pronto:237]: 0013 0043 0014 0017 0013 0017 0014 0017 0014 0017 0013 0017 0014 0017 0014 0017 0013 0017 0014 0043 0013 0043 0014
```

I connected a KY-005 IR transmitter and used the ESPHome [remote transmitter](https://esphome.io/components/remote_transmitter/) component to transmit the NEC code for the power button.
It was successful, and I could turn the receiver on and off using the IR transmitter. But this has a low spouse approval factor and I didn't like it either; I would need to have it directly in front of the receiver and it wouldn't look nice. My intention was to hide this behind the receiver so it wasn't visible.
```yaml
remote_transmitter:
  pin:
    number: 14
    inverted: False
    mode: OUTPUT      
  carrier_duty_percent: 50%
  non_blocking: true
```
So the next trick was sending the codes over the wire using the remote control in port on the back of the receiver. Since I didn't have a ton of information to go off of, I pieced together information from various sources and slowly made progress.
Eventually, I landed on this configuration and was successful. 
```yaml
button:
  - platform: template
    name: "Power Toggle"
    icon: "mdi:power"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x857A
          command: 0xE01F
```
Toggling power is functional but has a disadvantage in that it could get out of sync easiy and turn the device off when you wanted to turn it on. 
Once I was able to send commands over the wire, I started experimenting with different Yamaha discrete codes for power on and off to replace the power toggle. 

There are lots of discrete Yamaha codes that I found and none of them worked for me. Then I remembered that the IR receiver identified a Pioneer code for the power toggle. 
Sure enough, using that code toggled the power, so I started looking for discrete power codes for Pioneer instead. This is when I hit paydirt. I found discrete power codes for Pioneer that worked.
```yaml
button:
  # --- DISCRETE POWER via Pioneer IR codes ---
  - platform: template
    name: "Power On"
    icon: "mdi:power-on"
    on_press:
      - remote_transmitter.transmit_pioneer:
          rc_code_1: 0x5E1D

  - platform: template
    name: "Power Off"
    icon: "mdi:power-off"
    on_press:
      - remote_transmitter.transmit_pioneer:
          rc_code_1: 0x5E1E
```


### Notes
- I definitely accidentally let the smoke out of one transistor by not paying attention to my connections.
- There were many failed attempts to get the IR over wire working. I gloss over this, but it took me multiple days to hit on the config that worked.
