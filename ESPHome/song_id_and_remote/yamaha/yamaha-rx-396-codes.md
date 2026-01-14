# Working Yamaha and Pioneer IR Codes for Yamaha RX-396 Receiver

Yamaha Codes|Group|Name|Code|Address|Discrete|Description|
|-|-|-|-|-|-|-|
NEC|Power/Standby|Power Toggle|0xE01F|0x857A|no|toggles power on and off|
NEC|Volume|Volume Up|0xE51A|0x857A|yes|turns volume up| use `command_repeats=` the number of times you want the increase volume| example `command_repeats=10`|
NEC|Volume|Volume Down|0xE41B|0x857A|yes|turns volume down| use `command_repeats=` the number of times you want the decrease volume|
NEC|Input|AUX input|0xE817|0x857A|yes|switches to AUX input|
NEC|Input|Phono input|0xEB14|0x857A|yes|switches to Phono input|
NEC|Input|CD input|0xEA15|0x857A|yes|switches to CD input|
NEC|Input|Tuner input|0xE916|0x857A|yes|switches to Tuner input|
NEC|Input|Tape 1 input|0xE718|0x857A|yes|switches to Tape 1 input|
NEC|Input|Tape 2 input|0xE619|0x857A|yes|switches to Tape 2 Monitor input|
NEC|Power/Standby|Sleep|0xA857|0x857A|no|sets the sleep command|
NEC|Tape|DIR A|0x857A|0xF807|yes|sets direction of cassette player, captured code but do not own component to verify|
NEC|Tape|DIR B|0x857A|0xBF40|yes|sets direction of cassette player, captured code but do not own component to verify|
NEC|Tape|REC/PAUSE|0x857A|0xFB04|no|record and pause, captured code but do not own component to verify|
NEC|Tape|PLAY|0x857A|0xFF00|yes|plays cassette, captured code but do not own component to verify|
NEC|Tape|STOP|0x857A|0xFC03|yes|stops cassette, captured code but do not own component to verify|
NEC|Tape|REWIND|0x857A|0xFE01|yes|rewind, captured code but do not own component to verify|
NEC|Tape|FAST FORWARD|0x857A|0xFD02|yes|fast forward, captured code but do not own component to verify|
NEC|Tape|A/B|0x857A|0xF906|no|selects which cassette player to use for dual cassette components, captured code but do not own component to verify|
NEC|Tuner|PRESET -|0x857A|0xEE11|no|cycles through tuner presets in decreasing order|
NEC|Tuner|PRESET +|0x857A|0xEF10|no|cycles through tuener presets in increasing order|
NEC|Tuner|A/B/C/D/E|0x857A|0xED12|no|cycles through preset groups|
NEC|CD|REVERSE|0x857A|0xF20D|yes|scans back through track, captured code but do not own component to verify|
NEC|CD|FOWARD|0x857A|0xF30C|yes|scans forward through track, captured code but do not own component to verify|
NEC|CD|DISC|0x857A|0xB04F|no|selects disc to play, captured code but do not own component to verify|
NEC|CD|PLAY|0x857A|0xF708|yes|plays selected disc, captured code but do not own component to verify|
NEC|CD|PAUSE/STOP|0x857A|0xF609|no|pause then stop, captured code but do not own component to verify|
NEC|CD|SKIP REVERSE|0x857A|0xF40B|yes|skips to the previous track, captured code but do not own component to verify|
NEC|CD|SKIP FORWARD|0x857A|0xF50A|yes|skips to the next track, captured code but do not own component to verify|

**Examples for ESPHome:**

Single press example
```yaml
button:
  - platform: template
    name: "AUX Input"
    icon: "mdi:audio-input-rca"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x857A
          command: 0xE817
```
Repeated press example
```yaml
button:
  - platform: template
    name: "Stereo Volume Up"
    icon: "mdi:volume-plus"
    on_press:
      - remote_transmitter.transmit_nec:
          address: 0x857A
          command: 0xE51A
          repeat:
            times: 10
            wait_time: 50ms
```

Pioneer Codes|Name|Code|rc_code_X|Discrete|Description|
|-|-|-|-|-|-|
Pioneer|Power/Standby|Power Toggle|0x5E1F|rc_code_1|no|toggles power on and off|
Pioneer|Power/Standby|Power On|0x5E1D|rc_code_1|yes|turns power on|
Pioneer|Power/Standby|Power Off|0x5E1E|rc_code_1|yes|turns power off|


**Example for ESPHome:**

```yaml
button:
  - platform: template
    name: "Power On"
    icon: "mdi:power-on"
    on_press:
      - remote_transmitter.transmit_pioneer:
          rc_code_1: 0x5E1D
```

**Image of RAX7 (VZ45350) Remote**

<img width="232" height="640" alt="yamaha-remote-rax7" src="https://github.com/user-attachments/assets/d54dc55d-0811-4983-ac49-8e51ea93fc07" />
