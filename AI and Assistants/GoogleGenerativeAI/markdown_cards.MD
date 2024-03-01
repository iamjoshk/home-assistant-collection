This is how I use the sensor data for history lesson.

```
type: markdown
content: |-
  **{{ now() | as_timestamp | timestamp_custom('%B %d')}}**

  {{ state_attr('sensor.history_lesson','response') }}
title: History Lesson
```

This is the markdown card for music across time.

```
type: markdown
content: >
  **{{ now() | as_timestamp | timestamp_custom('%B %d')}}**


  {{ state_attr('sensor.music_across_time','response')['song_name'] }} by
  {{state_attr('sensor.music_across_time','response')['band_name'] }}

  Released on {{
  state_attr('sensor.music_across_time','response')['date_released'] }}
title: Song of the Day
```
