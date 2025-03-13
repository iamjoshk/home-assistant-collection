# Overview
A project to add a secondary RTSP microphone stream to my BirdNET-Go add-on in Home Assistant.

## Summary

I used a Raspberry Pi0 2 W and added a inexpensive lavalier microphone with a 3.5mm jack to USB-C adapter plugged into a UBS-C to micro USB adapter.

- Installed Raspberry Pi OS Lite (64bit) using Raspberry Pi Imager. Use this to enable SSH, create user account, set wifi settings.
- Recommend reserving the IP address for your RPi in your router so that it does not change on reboots. 

- After booting up for the first time, log in and run `sudo apt update` and `sudo apt full-upgrade`.
- Reboot, then log in and run `sudo su` then `passwd root` and change the password for the root user.
- Then run `sudo nano /etc/ssh/sshd_config`.
- Go to line with `#PermitRootLogin without-password` and remove `#` and change to `PermitRootLogin yes`.
  > **IMPORTANT NOTE and DISCLAIMER**: IN CASE IT IS NOT OBVIOUS, YOU ARE ENABLING SSH ACCESS FOR THE ROOT USER. THIS IS A POTENTIAL SECURITY RISK. I AM NOT RESPONSIBLE IF SOMEONE HACKS YOUR NETWORK THROUGH YOUR RPI, OR THROUGH ANY OTHER VECTOR INTO YOUR NETWORK.
- Then log out and log in as root.
- Move to (or confirm you are in) the `/root` directory and install ffmpeg with `apt-get install ffmpeg`
- Then install lsof with `apt-get install lsof`
- Then install mediamtx while still in the `/root` directory with
  `
  wget -c https://github.com/bluenviron/mediamtx/releases/download/v1.0.0/mediamtx_v1.0.0_linux_arm64v8.tar.gz -O - | sudo tar -xz
  `
- Run `lsub` to make sure your microphone is recognized (if it is a usb mic)
- Run `arecord -l` to get a list of capture hardware devices. This is important as it will tell you the card and device ID for your hardware.
  ```
  **** List of CAPTURE Hardware Devices ****
  card 0: Adapte [USB-C to 3.5mm-Headphone Adapte], device 0: USB Audio [USB Audio]
  Subdevices: 0/1
  Subdevice #0: subdevice #0
  ```
- Run `arecord --dump-hw-params -D hw:0,0` where `0,0` are the card and device number of your microphone from above.
- You should get something similar in output:
  ```
  Warning: Some sources (like microphones) may produce inaudible results
         with 8-bit sampling. Use '-f' argument to increase resolution
         e.g. '-f S16_LE'.
  Recording WAVE 'stdin' : Unsigned 8 bit, Rate 8000 Hz, Mono
  HW Params of device "hw:1,0":
  --------------------
  ACCESS:  MMAP_INTERLEAVED RW_INTERLEAVED
  FORMAT:  S24_3LE
  SUBFORMAT:  STD
  SAMPLE_BITS: 24
  FRAME_BITS: 48
  CHANNELS: 2
  RATE: 48000
  PERIOD_TIME: [1000 1000000]
  PERIOD_SIZE: [48 48000]
  PERIOD_BYTES: [288 288000]
  PERIODS: [2 1024]
  BUFFER_TIME: [2000 2000000]
  BUFFER_SIZE: [96 96000]
  BUFFER_BYTES: [576 576000]
  TICK_TIME: ALL
  --------------------
  arecord: set_params:1352: Sample format non available
  Available formats:
  - S24_3LE
  ```
- The available format will determine your sampling format.
- Once you have the hardware and the format, you can run a little test using `ffmpeg -f alsa -acodec pcm_s24le -ac 2 -ar 44100 -i hw:0,0 test.wav` where `pcm_s24le` and `hw:0,0` match your format and hardware. This should start a recording, talk into your mic, and then hit `q` to finish the recording. A file called `test.wav` will be generated. Move this to a directory you have access in (or run your recording test in a directory you have access to) from your client device. Then play the recording to see if it recorded sound from your mic.
- If this worked, test the RTSP stream by removing `test.wav` and adding `-ac 1 -content_type 'audio/mpeg' -f rtsp rtsp://localhost:8554/birdmic -rtsp_transport tcp` to the end of your command like: `ffmpeg -f alsa -acodec pcm_s24le -ac 2 -ar 44100 -i hw:0,0 -ac 1 -content_type 'audio/mpeg' -f rtsp rtsp://localhost:8554/birdmic -rtsp_transport tcp` making sure `pcm_s24le` and `hw:0,0` match your settings.
- While this is running, open up VLC on your client machine and open a network stream by going to Media -> Open Network Stream and entering `rtsp://IPofyourRPI:8554/birdmic` and click Play. It should connect and you should hear your mic (might be a second or two of a delay). You can close the stream once you confirm it is working.
- Back on the RPi, `q` to quit your mic stream.
- Try changing `hw:0,0` to `default` and start the stream again. The hardware card and device number can change on reboots and `default` avoid a failure if they change. If you get an error, reboot your RPi, then log in as root again, and try running it with `default` again. (I needed to reboot for `default` to work.)
- In the `/root` directory, run `nano startmic.sh` to create a bash script called `startmic.sh` and copy your command into it, then exit and save.
- Then run `chmod +x startmic.sh` to make the script executable.
- Then run `crontab -e` and select nano (option 1).
- Add `@reboot /root/startmic.sh` to the end of the file, then exit and save.
- Reboot your RPi and test with VLC to make sure that the RTSP stream started on reboot.
- If your stream is working, then go to your BirdNet-Go settings and add your audio source in settings with `rtsp://IPoyourRPI:8554/birdmic`. Save your settings. Restart your Birdnet-Go instance.
- In the log, you should see the new stream added. Talk into your mic and a second or two later the log should indicate that a human was detected from the stream IP address.
- Go set your RPi and mic up to capture bird sounds!



---
NOTES:
- This guide is a combination of lots of searching and reading.
- This post from BirdNet-Pi's github was my launching point: https://github.com/mcguirepr89/BirdNET-Pi/discussions/1006#discussioncomment-6747450
- I had a ton of trouble figuring out the sampling format for my mic. Finding a 10 year old Stackexchange (HA!) with the `arecord` commands was the piece of the puzzle I needed.
- I use BirdNet-Go as an add-on in my Home Assistant instance.
- This mic is my second RTSP audio stream source. The first is a camera RTSP, so keep in mind if you have cameras outdoors, you might be able to use those, too.
- Ultimately, this command is what worked for me:
```
./mediamtx & ffmpeg -f alsa -acodec pcm_s24le -ac 2 -ar 44100 -i default -ac 1 -content_type 'audio/mpeg' -f rtsp rtsp://localhost:8554/birdmic -rtsp_transport tcp
```
