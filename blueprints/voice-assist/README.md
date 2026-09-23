## Voice Assist Blueprints

### Dice Roller
##### Blueprint import url: 
```
https://github.com/iamjoshk/home-assistant-collection/blob/main/blueprints/voice-assist/roll-dice/voice-assist-roll-die.yaml
```
A blueprint and pyscript for rolling dice with View Assist with an optional sound file to go along with it.

To use:
1. Import the blueprint in Home Assistant
2. Download and move the `roll_dice.py` pyscript to the `config/pyscript` directory
3. Optionally download the `dice_roll.wav` and/or `dice_roll_boost.wav` for an audio sound effect. Move the file to your media directory or other accessible location.
4. Create a new automation using the blueprint.
5. May the virtual math rocks be in your favor.


### Stardate
##### Blueprint import url: 
```
https://github.com/iamjoshk/home-assistant-collection/blob/main/blueprints/voice-assist/star-date/voice-assist-star-date.yaml
```

A blueprint that calculates a fictional Star Trek: The Next Generation stardate based on the current date.

It doesn't work well. 😅


### Timers
##### Blueprint import url: 
```
https://github.com/iamjoshk/home-assistant-collection/blob/main/blueprints/voice-assist/timers/voice-assist-timers.yaml
```

Works with the [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration)'s `voice_satellite.start_timer` action to set timers by name and includes setting timers for specific time of day in addition to duration timers.

### Weather Forecast
##### Blueprint import url: 
```
https://github.com/iamjoshk/home-assistant-collection/blob/main/blueprints/voice-assist/weather-forecast/voice-assist-weather-forecast.yaml
```

Works with a weather entity that provides daily, twice daily, and hourly forecasts to provide forecasts for today, tomorrow, today and tomorrow, extended 5 day, and detailed hourly for the next 6 hours or until end of day if fewer than 6 hours. Summarizes the forecast concisely in the response. 

### Show Camera
##### Blueprint import url: 
```
https://github.com/iamjoshk/home-assistant-collection/blob/main/blueprints/voice-assist/show-camera/kiosk-satellite-show-camera.yaml
```

Works with [Kiosk Satellite](https://github.com/jxlarrea/kiosk-satellite) to display specific cameras on screen by pressing the exposed camera view button(s) from Kiosk Satellite. Needs the entity name for the camera view to be specifically named `button.<area>_<device>_show_<camera view>_camera`, like `button.living_room_satellite1_show_driveway_camera`.

### Spell Word
##### Blueprint import url: 
```
https://github.com/iamjoshk/home-assistant-collection/blob/main/blueprints/voice-assist/spell-word/voice-assist-spell-word.yaml
```

Spells a requested word, with optional slow(er) spelling.

### Sports Scores
##### Blueprint import url: 
```
https://github.com/iamjoshk/home-assistant-collection/blob/main/blueprints/voice-assist/sports-scores/voice-assist-sports-scores.yaml
```

Provides the sports scores for team_tracker entities. Needs the entity names to be `sensor.team_tracker_<teamname>`, like `sensor.team_tracker_eagles`. Can add aliases to map back to the correct name, like `"birds":"eagles"`.
