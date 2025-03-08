## Overview

Upgraded from my RPI4 4GB to a bare metal HAOS install on a Minisforum UN100P mini PC with 16GB RAM and 512 GB NVMe SSD.

## Activities
1. Make a full backup of HA.
  - If you don't already do this, move it to a remote location like Google Drive or another PC so that it is accessible once you take your existing environment down.
  - Having the back up `tar` file on the PC you will be using to access your HA environment will be helpful later.
  - If you don't normally, you may want to back up the media folder for this backup. 
2. Follow the [instructions here for installing HAOS](https://www.home-assistant.io/installation/generic-x86-64/) on a generic x86-64 PC.
  - It will be useful to have a monitor and keybaord (and mouse initially) connected to the new environment for now.
3. Once you've finished the install, boot up the fresh HA install. Take note of the IP address.
  - I suppose this would be the time to change the IP address of your new install, but I did not do this.
  - If the fresh install is not the same version as your existing environment, then run `ha core update --version xxxx.x.x` replacing `xxxx.x.x` with the version of your existing environment.
  - If you can do it now, move the backup you made to the new HA install in the `backups` folder. You can do this later, in other ways that might be easier,too.
4. From the PC you use to access HA, open the browser and navigate to the IP address:8123 or homeassistant.local:8123.
5. At the login screen, create a new user and log in.
  - The new user can be anything you want. It will get overwritten when you restore with the backup you've created.
6. From here, probably the easiest way to transfer your backup to the new install is via the Samba share add-on. Install this from the Add On Store, reboot, then set up access.
  - On a Linux PC, navigate to in your file manager `smb://192.168.xxx.xxx/backups` and copy the back up to this location.
  - Remember, make sure your existing enivronemtn and fresh install are the same HA version.
  - Copying the backup can take a while.
7. Once your backup is in the right place, restart HA again.
8. Once restarted, navigate to Settings -> Backups -> Manual Backups and select your backup to restore.
9. Once finished, restart HA.
10. When restarted, reboot the host (which is the actual mini PC).
11. Once rebooted and HA has restarted, if you have not changed the IP address to the same IP address as your old environment, you may need to update some settings, like MQTT Explorer, the MQTT IP address Frigate uses, etc.


    
