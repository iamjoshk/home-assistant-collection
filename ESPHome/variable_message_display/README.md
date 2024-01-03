A variable message display that shows:
- weather for today
- weather for tomorrow
- a quote of the day (option)
- pokemon of the day (option)

A button press cycles through the differen pages

Some tricks and workarounds:
- Pokemon of the Day uses an automation from HA to run a 'shell_command' bash script that installs the esphome yaml for the display to update the images of the pokemon.
- Quote of the day uses a display lambda that wraps the text of the quote to fit the width of the screen.

Hardware:
- LILYGO T-Display-S3 ESP32-S3
