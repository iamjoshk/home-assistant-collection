## Google Generative AI in Home Assistant

- **History Lesson** - A script that uses the Google Generative AI integration to generate a random "Today-In-History" type of history fact, provided in the style of Dr. Seuss.  The `response_variable` is read aloud on a group of Google Homes. It is also sent via MQTT to an MQTT sensor and the response is stored in the sensor attribute. The state of the sensor is the month and day used to pick the history lesson. The sensor is displayed on a Markdown card for later reading.
  - `history_lesson_script.yaml`

<br><br>

- **Music Across Time** - A script that uses the Google Generative AI integration to generate a `response_variable` that provides a song, band, and date released as a dictionary. The response is sent as a notificaton to a phone and is published to an MQTT sensor. The sensor is displayed on a markdown card.
  - Updated the actionable notification to include a deep link to the song on Spotify. Getting the Spotify link uses a combination of Spotcast and Music Assistant addons. Unfortunately, Spotcast's search feature is terribly unreliable and would return results way off the mark. Music Assistant has a much better search and I grab the Spotify link from the results and provide that to Spotcast to start playing the song on a specific speaker. 
  - Added 2 buttons on a wall mounted dashboard:
    - Request a new song
    - Play the song on specific speakers
  - `music_across_time_script.yaml`
  - `play_song_of_the_day_script.yaml`


- **School Bus Reminder** - An automation with a time-based trigger that uses Google Generative AI to create a new, random reminder to get ready for the school bus on school days. Google discontinued Family Bell which we were using. Family Bell had limitations such as a static message, no consideration for holidays, etc. I took the opportunity to migrate the reminder from Family Bell to an HA automation. This let me set up the automation to only run on school days and to have a new randomly generated message every day. Super simple and the kids love it.

