## Google Generative AI in Home Assistant

- History Lesson - A script that uses the Google Generative AI integration to generate a random "Today-In-History" type of history fact, provided in the style of Dr. Seuss.  The `response_variable` is read aloud on a group of Google Homes. It is also sent via MQTT to an MQTT sensor and the response is stored in the sensor attribute. The state of the sensor is the month and day used to pick the history lesson. The sensor is displayed on a Markdown card for later reading.

- Music Across Time - A script that uses the Google Generative AI integration to generate a `response_variable` that provides a song, band, and date released as a dictionary. The response is sent as a notificaton to a phone and is published to an MQTT sensor. The sensor is displayed on a markdown card.
