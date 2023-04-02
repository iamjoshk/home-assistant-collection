## Overview
Performace on my RPi4 with SD card was starting to get bogged down, especially in complex automations. I had read that upgrading to an SSD not only improved performance but was also more stable than using an SD card.
Upgrade from an SD card to an SSD for Raspberry Pi 4 (4GB) with Home Assistant OS

Specific Equipment used:
+ [UGREEN SATA to USB 3.0 Adapter Cable](https://www.amazon.com/dp/B07Y825SB8)
+ [Crucial BX500 240GB - CT240BX500SSD1](https://www.amazon.com/dp/B07G3YNLJB)


## Activities

1. Make a full backup of your HAOS instance and move it to a location you can retreive it later (not on your existing SD card running HAOS).
    - Having the `tar` file for your backup on the computer you will be using to access your HA instance will be helpful later.
2. Completely power down your RPi4 running HAOS. 
3. Remove your SD card with your HAOS on it
4. Using a different SD card of any size, use Raspberry Pi Imager to create a Bootloader - USB Boot image on the second SD card
5. Insert the bootloader SD card into your Rpi4 and power on.
    - After about 20 seconds, the green activity light will flash rapidly. This indicates that the RPi4 is ready to boot from USB. If you have a monitor attached to your RPi4, it will have a solid green screen.
6. Shut down the RPi4 again.
7. On another computer, prepare the SSD by installing a clean install of HAOS.
    - Connect the SSD to your computer.
    - Using BalenaEtcher, select the Flash from URL option and use the URL from Home Assistant OS Raspberry Pi [WRITE THE IMAGE TO YOUR BOOT MEDIA](https://www.home-assistant.io/installation/raspberrypi#write-the-image-to-your-boot-media)
    - When completed, disconnect SSD from your computer
8. Connect the SSD to one of the USB 3.0 ports on your RPi4 and power on.
9. When it's finished booting up, navigate to homeassistant.local:8123 on your computer's web browser.
10. At the start screen, select the link at the bottom that says `Restore from a previous backup`.
11. Select the backup file from your computer to load.
12. Start the restore process.
    - Note that there should be some sign of progress, however in my case, it looked like nothing was happening. I tried uploading the backup file again, got a `Failed to fetch` error message. Turns out it was just working invisibly in the background.

Notes:
 + When I restored, I had to access the environment from http://homeassistant.local:8123 and then change the external settings back to my preferred URL after logging in.
 + The Add Ons state were out of sync between the frontend and backend. They were running, and I could see activity in their logs, but the frontend thought they were stopped. To resolve this:
    - Based on [this comment](https://community.home-assistant.io/t/addons-not-starting/450322/44), I completely shut down the RPi4, waiting about 30 seconds, and then restarted. The addons were in sync again after this.

 + Overall system performance was greatly improved. Everything is more responsive, screens load faster, boot up after restart is faster. I am very pleased with this simple upgrade.
 + If you use `PiHole` or `AdGuard`, you may want to disable blocking while booting up the clean instance of HA for the first time (before you restore).
