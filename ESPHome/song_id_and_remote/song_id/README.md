### Song ID

This project uses an I2S MEMS microphone module (ZTS6631) to record snippets of songs and send them to Shazam via ShazamIO API for song ID.
It uses an external component for recording and saving the audio snippet to flash. Then a shell command gets the file from the ESP32 and copies it to local storage in Home Assistant, which then sends it to Shazam for ID.
