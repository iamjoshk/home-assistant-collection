### Song ID

This project uses an I2S MEMS microphone module (ZTS6631) to record snippets of songs and send them to Shazam via ShazamIO API for song ID.
It uses an external component for recording and saving the audio snippet to flash. Then a shell command gets the file from the ESP32 and copies it to local storage in Home Assistant, which then sends it to Shazam for ID.

> ### This is extremely early alpha and not fully working

**External Component**: [audio_recorder](https://github.com/iamjoshk/home-assistant-collection/tree/main/ESPHome/song_id_and_remote/song_id/components/audio_recorder)

**Addon and Custom Integration**: [HA ShazamIO](https://github.com/iamjoshk/ha_shazamio)

This attempts to wrap the ShazamIO API service into an HA addon and custom integration to provide a one to one HA action to ShazamIO API feature. It is heavily AI-coded and has not been reviewed and refactored yet. It could break at any time. 

