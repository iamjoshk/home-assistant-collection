## Song ID and Remote Control Over Wire
This project combines a remote control over wire and song ID into a single ESP32-S3.


### Yamaha Remote Control

[More Info](https://github.com/iamjoshk/home-assistant-collection/tree/main/ESPHome/song_id_and_remote/yamaha)

This sends IR codes over wire using the remote control in jack on the back of the receiver.
To get the codes, I used an IR receiver module and pressed buttons on the remote. Lots of reading online found discrete codes for Pioneer that worked for power on and off instead of a toggle.

### Song ID

[More Info](https://github.com/iamjoshk/home-assistant-collection/tree/main/ESPHome/song_id_and_remote/song_id)

This project uses an I2S MEMS microphone module (ZTS6631) to record snippets of songs and send them to Shazam via ShazamIO API for song ID. It uses an external component for recording and saving the audio snippet to flash. Then a shell command gets the file from the ESP32 and copies it to local storage in Home Assistant, which then sends it to Shazam for ID.


### ESPHome YAML

[See file](https://github.com/iamjoshk/home-assistant-collection/blob/main/ESPHome/song_id_and_remote/esphome-song-id-and-remote.yaml)
Requires external component audio_recorder
