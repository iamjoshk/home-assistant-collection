## Overview

Sensors that I've created for various purposes.

## Sensors
+ `timer_event_state` sensor sets the timer events as the state of the sensor and keeps a recent history in attributes. This extends functionality of timers in automations, scripts, and other elsewhere.
  + State is sent to the most recent timer event
    + timer.started
    + timer.paused
    + timer.restarted
    + timer.cancelled
    + timer.finished  
   
<br>

+ `lutron_aurora_sensor` sensor captures zha_event data as state and attributes which reduces the impact of the device keeping the state on board itself and extends potential functionality for automations and scripts.
  +  State is set by the `level` from `params`
  +  Attributes include:
      + time_fired 
      + params: level
      + params: transition_time
      + previous_level
      + previous_transition_time
      + brightness
      + action_type
      + rotate_right - enables continuous rotation to the right
      + rotate_left - enables continuous rotation to the left
