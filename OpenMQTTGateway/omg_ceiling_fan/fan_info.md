Automation:

```yaml
alias: Living Room Ceiling Fan and Light
description: ""
triggers:
  - entity_id:
      - sensor.ceiling_fan_last_value
    id: fan-on
    to: "1975"
    trigger: state
  - entity_id:
      - sensor.ceiling_fan_last_value
    to: "1981"
    id: fan-off
    trigger: state
conditions: []
actions:
  - choose:
      - conditions:
          - condition: trigger
            id:
              - fan-on
        sequence:
          - action: input_select.select_option
            target:
              entity_id: input_select.living_room_fan_speed
            data:
              option: "33"
      - conditions:
          - condition: trigger
            id:
              - fan-off
        sequence:
          - action: input_select.select_option
            target:
              entity_id: input_select.living_room_fan_speed
            data:
              option: "0"
    alias: ceiling fan on and off
mode: single
```

Script:

```yaml
alias: Living Room Fan Speed
sequence:
  - repeat:
      count: 2
      sequence:
        - data:
            qos: 0
            retain: true
            payload: >
              {% set speed = state_attr('fan.living_room_fan','percentage') |
              int(0) %}  
              {% if speed == 0 %}
              {"value":1981,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}
              {% elif speed == 33 %}
              {"value":1975,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}
              {% elif speed == 66 %}
              {"value":1967,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}
              {% elif speed == 100 %} 
              {"value":1951,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}
              {% endif %} 
            topic: home/omg_ceiling_fan/commands/MQTTto433
          action: mqtt.publish
        - delay:
            hours: 0
            minutes: 0
            seconds: 0
            milliseconds: 300
          enabled: false
    enabled: true
mode: restart
icon: mdi:ceiling-fan
```

Dropdown helper:

<img width="550" height="485" alt="Snapshot_2026-03-17_11-47-48" src="https://github.com/user-attachments/assets/fd4ae241-9f33-43ae-8069-c354ebe1ee61" />



Template fan:

```yaml
template:
  - fan:
    - unique_id: living_room_fan
      turn_on:
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1975,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1983,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110111111","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      turn_off:
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1981,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1983,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110111111","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      speed_count: 3
      set_percentage:
      - target:
          entity_id:
          - input_select.living_room_fan_speed
        data:
          option: '{{ percentage }}'
        action: input_select.select_option
      - action: script.living_room_fan_speed
      default_entity_id: fan.living_room_fan
      name: Living Room Fan
      percentage: '{{ states(''input_select.living_room_fan_speed'') }}'
      state: '{{ states(''sensor.living_room_fan_status'') }}'
      direction: "{{ 'forward' if is_state('input_boolean.ceiling_fan_direction', 'on') else 'reverse' }}"
      set_direction:
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1975,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1979,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110111011","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1983,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110111111","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      - action: mqtt.publish
        data:
          qos: 0
          payload: '{"value":1975,"protocol":8,"length":12,"delay":321,"tre_state":"-","binary":"011110110111","frequency":303.9}'
          topic: home/omg_ceiling_fan/commands/MQTTto433
      - action: input_boolean.toggle
        entity_id: input_boolean.ceiling_fan_direction
```

Direction helper:

<img width="540" height="496" alt="Snapshot_2026-03-17_11-54-20" src="https://github.com/user-attachments/assets/5206becb-0b9a-40a9-b0e9-14b2644b5aa1" />

