# Song of the Day
## How to create a song of the day randomizer based on the current day and month, with an actionable notification to play the song on your (android) phone or to various speakers.


## Prerequisites
- (Google Generative AI)[https://www.home-assistant.io/integrations/google_generative_ai_conversation/] integration (or similar)
- (Spotify)[https://www.home-assistant.io/integrations/spotify/] integration (or similar)
- (Spotcast)[https://github.com/fondberg/spotcast] addon integration
  - Unfortutately, the owner of the original Spotcast repo passed away. As of March 2024, others are maintaining the repo, but I suspect it could move to a new repo at some point.
- (Music Assistant)[https://music-assistant.io/] addon integration
  - Music Assistant is a cool, full-featured music library manager, but in this scenario, I am just using it for it's effective Spotify search capability. Spotcast's Spotify search is terribly ineffective. There are PRs to improve it, but until then, Music Assistant's search and results are very effective.
- MQTT and MQTT broker integrations
  - There are lots of options for MQTT brokers. I use the Mosquitto addon as my MQTT broker. It's easy and self-contained within HAOS.

## Steps

1. Install the Google Generative AI integration and follow configuration instructions
2. Install the Spotify integration
3. Install the Spotcast addon integration through HACS
4. Install the Music Assistant addon through HACS

5. With everything installed, we need to create some scripts, automations, MQTT sensors, and some buttons.

6. to-do...
