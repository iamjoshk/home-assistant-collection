This is how I use the sensor data for history lesson.

```
type: markdown
content: |-
  **{{ now() | as_timestamp | timestamp_custom('%B %d')}}**

  {{ state_attr('sensor.history_lesson','response') }}
title: History Lesson
```

Results in:
