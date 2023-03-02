## Overview

rtl_433 can hop frequencies by specifiying multiple frequencies and the `hop_interval` in `rtl_433.conf.template`. But what if you want to switch to another frequency very infrequently (once a day) and for only a few minutes before switching back to your primary frequency?

>Example Use Case: You have a handful of sensors, like door/window contact sensors and temp/humidity sensors that transmit on 433Mhz but you also want to capture the consumption from your water meter on 915Mhz.

You can use Home Assistant's `shell_command` and an automation to switch frequencies on your own schedule with your own conditions.

This guide will demonstrate one way you could do this.

> Note: this example is based on the assumption that you are using `Home Assistant OS`. Otherwise, you will need to make changes based on your environment. In addition, this guide assumes you have some basic knowledge of Home Assistant and does not go into how to access the command line in Home Assistant OS. I use the 
[SSH & Web Terminal](https://github.com/hassio-addons/addon-ssh) add on. I use the [Samba share](https://github.com/home-assistant/addons/tree/master/samba) add on to easily access files.

## Activites covered
The steps below describe how to create and automation to switch to 915Mhz just after midnight for a few minutes and then switch back to 433Mhz.

You will:
+ create a second `rtl_433.conf.template` with a modified name 
+ write a bash script(s) to rename your `rtl_433.conf.template` files
+ add the `shell_command` integration to `configuration.yaml`
+ create an automation to run your bash scripts


## Create a second `rtl_433.conf.template` file with a modified name

1. In `/config/rtl_433/` make a copy of `rtl_433.conf.template` and rename the copy to `rtl_433.conf.template.915`
2. Edit `rtl_433.conf.template.915` and change the frequency to `915M`. Leave everything else the same and then save.

## Write a bash script(s) to rename your `rtl_433.conf.template` files when called in the `shell_command` service in the automation.
> You could combine these into a single bash script. I chose to create separate scripts.
1. In `/config/rtl_433/` create a new bash script file named `rtl_433_conf_template_915.sh`
2. In `rtl_433_conf_template_915.sh` write the following script:

```#! /bin/bash

if [ -f "/config/rtl_433/rtl_433.conf.template.915" ]; #tests whether rtl_433.conf.template.915 exists in the directory
then

mv /config/rtl_433/rtl_433.conf.template /config/rtl_433/rtl_433.conf.template.433 #renames the current rtl_433.conf.template to rtl_433.conf.template.413
mv /config/rtl_433/rtl_433.conf.template.915 /config/rtl_433/rtl_433.conf.template #renames rtl_433.conf.template.915 to rtl_433.conf.template
ls -la #just for a visual if you run from the command line

else

ls -la
echo "rtl_433.conf.template already set for 915Mhz" #just for a visual if you run from the command line

fi
```
4. Save your bash script.

3. Create a second new bash script file named `rtl_433_conf_template_433.sh`
4. In `rtl_433_conf_template_433.sh` write the following script:
```
#!/bin/bash

if [ -f "/config/rtl_433/rtl_433.conf.template.433" ]; #tests whether rtl_433.conf.template.433 exists in the directory
then

mv /config/rtl_433/rtl_433.conf.template /config/rtl_433/rtl_433.conf.template.915 #renames the current rtl_433.conf.template to rtl_433.conf.template.915
mv /config/rtl_433/rtl_433.conf.template.433 /config/rtl_433/rtl_433.conf.template #renames rtl_433.conf.template.433 to rtl_433.conf.template
ls -la #just for a visual if you run from the command line

else

ls -la
echo "rtl_433.conf.template already set for 433.92Mhz" #just for a visual if you run from the command line

fi
```
7. Save your second bash script.
8. You should now have 4 files in `/config/rtl_433/`:

`rtl_433.conf.template`
`rtl_433.conf.template.915`
`rtl_433_conf_template_433.sh`
`rtl_433_conf_template_915.sh`

## Add the `shell_command` integration to `configuration.yaml`
> These steps reference the [Shell Command](https://www.home-assistant.io/integrations/shell_command/) for Home Assistant.
1. In `configuration.yaml` add the following section, if you don't already have it:
```
shell_command:
```
2. Then add your two bash scripts. You create an `alias` for them that you'll use later to identify them in the automation. The `alias` can be anything, I chose `rtl_433_915` and `rtl_433_433`.
```
shell_command:
  rtl_433_915: bash /config/rtl_433/rtl_433_conf_template_915.sh
  rtl_433_433: bash /config/rtl_433/rtl_433_conf_template_433.sh
```
> This is an important note:
>
> ![image](https://user-images.githubusercontent.com/28068117/221301315-86580ca9-e8e6-4de9-a313-1fff05fb9383.png)
>
> This is why the scripts include the full directories for the files.

3. Save your `configuration.yaml`
4. Restart Home Assistant.

## Create an automation to run your bash scripts

1. After Home Assistant restarts, got to Automations and create a new automation from scratch. 
2. Click the three dots (kebab menu) in the upper right corner and select `Edit in YAML`
3. Copy and paste the following automation

```
alias: rtl_433 Frequency Switch
description: "Switch to 915Mhz for a few minutes in the middle of the night"
trigger:
  - platform: time
    at: "00:01:00"
    id: switch-to-915
  - platform: time
    at: "00:10:00"
    id: switch-to-433
condition: []
action:
  - if:
      - condition: trigger
        id: switch-to-915
    then:
      - service: shell_command.rtl_433_915
        data: {}
      - service: hassio.addon_restart
        data:
          addon: 9b13b3f4_rtl433
# you'll need to update the addon for your specific rtl_433 instance. You can switch back to the visual editor and select the correct addon.          
  - if:
      - condition: trigger
        id: switch-to-433
    then:
      - service: shell_command.rtl_433_433
        data: {}
      - service: hassio.addon_restart
        data:
          addon: 9b13b3f4_rtl433
# same as above, you'll need to update the addon for your specific rtl_433 instance.
mode: single
```

4. Save your automation.

5. You're done.

## Testing

I suggest testing your scripts from the command line prior to enabling creating the automations.
You can test the automation by changing the time triggers to a few minutes ahead of the current time and a few minutes apart and then when the first trigger runs, you can check the logs of the `rtl_433` add-on to make sure the frequency is what you expect. Then check again after the second trigger runs.

