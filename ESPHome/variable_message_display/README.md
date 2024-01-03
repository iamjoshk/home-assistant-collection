A variable message display that shows:
- weather for today
- weather for tomorrow
- a quote of the day (option)
- pokemon of the day (option)

A button press cycles through the differen pages

Some tricks and workarounds:
- Pokemon of the Day uses an automation from HA to run a `shell_command` bash script that installs the esphome yaml for the display to update the images of the pokemon.
  - This requires setting up SSH to access the root HAOS container. Information about how to do this was found in various places:
    -  https://community.home-assistant.io/t/running-a-shell-command-from-home-assistant-to-remote-linux-pc/135221
    -  https://developers.home-assistant.io/docs/operating-system/debugging/#generating-ssh-keys
- Quote of the day uses a display lambda that wraps the text of the quote to fit the width of the screen.

Various other links I found helpful while creating these:
- https://github.com/sjhilt/esphome-display/blob/main/esphome_display.yaml
- https://github.com/landonr/lilygo-tdisplays3-esphome/blob/main/example.yaml
- https://community.home-assistant.io/t/eink-multi-line-text/255814
- https://community.home-assistant.io/t/shell-command-running-into-timeout/249190/12
- https://esphome.io/components/display/index.html
- https://community.home-assistant.io/t/sshing-from-a-command-line-sensor-or-shell-command/258731
- https://community.home-assistant.io/t/esphome-cli-from-ha/391465
- https://community.home-assistant.io/t/daily-random-pokemon/529978

Hardware:
- LILYGO T-Display-S3 ESP32-S3
