## Generic RF doorbell using an EV1527

I ordered a cheap 433MHz doorbell. Unfortunately, the transmission was not a decoded by `rtl_433` automatically. I needed to set up a flex decoder. While it is working, I am still tweaking it to improve reliability.

I added the following to my `rtl_433` config file.

```
decoder {n=doorbell_ev1527,m=OOK_PWM,s=164,l=552,r=5680,g=584,t=152,y=0,repeats>=5,rows>=25,bits=25,countonly,unique,get=@0:{24}:id,get=@0:{25}:channel
```

There are several EV1527 confs, including one a Reolink doorbell. The EV1527 is very common, but the timings are different for every device which is pretty annoying and this is why it requires a flex decoder. The right way to get the best flex decoder settings is to use rtl_433 to analyze the signal for your specific device and then set your flex decoder appropriately.

Below was the result from setting `analyze_pulses true` in the `rtl_c433.conf` file and then reviewing the log.

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
