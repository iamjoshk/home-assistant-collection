## Overview

Create:
1. `timer` helper
2. `input_number` helper
3. script to increment a running timer by 5 minutes each time you run the script.

Optionally create:
1. create an `input_button` helper or use a dashboard card of some kind to call the script service on demand 
2. a way to reset the timer back to the default duration*

## Activities

1. Create the `timer` helper
2. Create [`input_number` helper](https://github.com/iamjoshk/home-assistant-collection/blob/main/automations/timer-incrementer/input_number-helper.MD)
3. Create [script](https://github.com/iamjoshk/home-assistant-collection/blob/main/automations/timer-incrementer/script.yaml)


### NOTE on TIMER DURATION
Even if you set a default duration in the timer, when you run the timer, it will use the duration from the last time it ran as the duration. This is annoying.

To workaround this, you basically need to move starting your timer to an automation or script in which you set the duration in the service call.

When you call the `timer.start` service, you can set the duration like this (this is in the script for incrementing the time):
```
service: timer.start
data:
  duration: |
    {{ states('input_number.your_timer_incrementer')|int }}
target:
  entity_id: timer.your_timer_helper
enabled: true
```

In the script, if you reset the incrementer to what your desired default duration as the last action of the script, then when you call the `timer.start` service the next time, it will use this value in your script/automation that starts the timer.
