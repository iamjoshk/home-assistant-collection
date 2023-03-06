## Overview

Example of a series of `timer helpers`, `scripts`, and `automations` that work together to create a timer to turn off a light, with a visual warning shortly before turning off.

## Components

+ `timer N`: timer for N minutes, where N represents the total number of minutes you want to countdown
+ `timer N-2`: timer for N-2 minutes, timer that is 2 minutes shorter than N
+ `timer 2 minutes`: timer for 2 minutes, timer that is 2 minutes long
+ script for triggering `timer N` and `timer N-2`
+ script for warning that the light will turn out soon
+ automation for actions at the end of `timer N`
+ automation for actions at the end of `timer N-2`
+ automation for actions at the end of `timer 2 minutes`



## Steps

## Create `timer N`, `timer N-2`, and `timer 2 minutes`
1. Under Integrations / Helpers, create a new `timer` helper
    - Name - what you want to name the timer
    - Icon - choose your icon
    - Duration - set the default duration for the timer
    - Restore - check this box if you want a running timer to persist through a restart
 
2. Repeat to create the other two timers

## Create script for starting `timer N` and `timer N-2`
> the script checks if the targeted light is on or off. If it is off, it turns it on before continuing.
1. Create script, click the three dots in the upper right corner, then select `Edit in YAML`
2. Copy and paste this script `yaml`.
```
alias: Light Timer
sequence:
  - if:
      - condition: device
        type: is_off
        device_id: your_device_id
        entity_id: light.your_light_id
        domain: light
    then:
      - type: turn_on
        device_id: your_device_id
        entity_id: light.your_light_id
        domain: light
      - service: timer.start
        data: {}
        target:
          entity_id: timer.n_timer
      - service: timer.start
        data: {}
        target:
          entity_id: timer.n_2_timer
    enabled: true
  - if:
      - condition: device
        type: is_on
        device_id: your_device_id
        entity_id: light.your_light_id
        domain: light
    then:
      - service: timer.start
        data: {}
        target:
          entity_id: timer.n_timer
      - service: timer.start
        data: {}
        target:
          entity_id: timer.n_2_timer
    enabled: true
mode: single
```

3. Switch back to the visual editor and update your entities and timer names.
4. Rename and save the script.

## Create script for warning that the light will turn out soon
> this script blinks the target light off and on twice as a visual warning that the light will turn out soon
1. Create script, click the three dots in the upper right corner, then select `Edit in YAML`
2. Copy and paste this script `yaml`.
```
alias: light off warning script
sequence:
  - if:
      - condition: device
        type: is_on
        device_id: your_device_id
        entity_id: light.your_light_id
        domain: light
    then:
      - repeat:
          count: 2
          sequence:
            - type: turn_off
              device_id: your_device_id
              entity_id: light.your_light_id
              domain: light
            - delay:
                hours: 0
                minutes: 0
                seconds: 0
                milliseconds: 250
            - type: turn_on
              device_id: your_device_id
              entity_id: light.your_light_id
              domain: light
            - delay:
                hours: 0
                minutes: 0
                seconds: 0
                milliseconds: 250
    else:
      - stop: The light is already off.
mode: single
```

3. Switch back to the visual editor and update your entities and timer names.
4. Rename and save the script.

## Create automation that triggers at the end of `timer N-2`
> this automation is triggered at the end of `timer N-2` and it triggers the warning script above and starts `timer 2 minutes`
1. Create automation, click the three dots in the upper right corner, then select `Edit in YAML`
2. Copy and paste this automation `yaml`
```
alias:  timer N-2 end automation
description: ""
trigger:
  - platform: event
    event_type: timer.finished
    event_data:
      entity_id: timer.timer.n_2_timer
condition: []
action:
  - service: script.light_off_warning
    data: {}
  - service: timer.start
    data: {}
    target:
      entity_id: timer.timer_2_minutes
mode: single
```

3. Switch back to the visual editor to update your entities and timer names.
4. Rename and save the automation.

## Create the automation to turn out the light
> this automation is triggered at the end of `timer 2 minutes`

1. Create automation, click the three dots in the upper right corner, then select `Edit in YAML`
2. Copy and paste this automation `yaml`
```
alias: turn light off after timer
trigger:
  - platform: event
    event_type: timer.finished
    event_data:
      entity_id: timer.timer_2_minutes
action:
  - service: light.turn_off
    target:
      entity_id: light.your_light_entity
    data: {}
mode: single
```

3. Switch back to the visual editor to update your entities and timer names.
4. Rename and save the automation.


## Additional notes
+ you can start the timers from your dashboard by using them as target entities in `button` cards, `entities` cards, or any variety of other card.
+ Only `entities` (and not `entity`) cards can show a live countdown of the time remaining on a timer
+ To see the overall time left before the light turns off, use `N timer` in an `entities` card
+ To see how much time before the warning, use `N-2 timer` in an `entities` card
+ To see how much time remains after the warning, use `timer 2 minutes` in an `entities` card
+ there may be simpler and more efficient ways of implementing these; this is only intended as a starting point







