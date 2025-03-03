## Project
Proof of concept Edge AI functionality using LLMVision Data Analyzer to read my AprilAire humidifier control panel and report status in Home Assistant.

### Requirements
- [LLMVision](https://github.com/valentinfrlch/ha-llmvision)
- Camera entity: in my case, I used an ESP32Cam I had laying around unused.
- Access to the LLM provider of your choice: I used Google since I already had an API key set up, it's free, and through my own testing was better
  than other free options. YMMV. Get this set up before starting.
  > Be aware of the quotas from your LLM provider - 1 request per minute every hour is 1440 requests.
  > Google Gemini 2.0 Flash Lite allows 1500 Records Per Day (RPD) in the free tier.
- Something for the camera to look at: a humidifier control panel (in my case), HVAC control board with blinking lights, washer and dryer, or maybe even
  utility meters, providing an easier entry point than the AI on the Edge project.
- Some helpers: To start, I created a template sensor helper

### Steps
1. Have a camera entity in Home Assistant using one of the various methods and integrations for cameras. Point it at your subject of interest.
2. Install the LLMVision add-on (available through HACS)
3. Add the LLMVision integration after the add-on is installed and select your model provider.
4. Go to Developer Tools -> Actions
5. Select `llmvision.data_analyzer`
6. Starting in UI mode, fill in the relevant data.
   > My example:
   > ```
   > action: llmvision.data_analyzer
   > data:
   >   include_filename: false
   >   temperature: 0.1
   >   provider: YOURIDWILLBEDIFFERENT
   >   image_entity:
   >     - camera.your_camera
   >   message: >-
   >     Analyze the provided image of a humidifier control panel. Extract the
   >     current humidity setting in the blue box displayed as a two digit numerical
   >     value without commas or spaces (h). Additionally, determine the status (1/0)
   >     of the red Maintenance LED (m) , orange Filter  LED(f) , and green Running
   >     LED (r) indicators. Output the information in the following format:
   > 
   >     hmfr
   >   model: gemini-2.0-flash-lite
   >   sensor_entity: sensor.llmvision_test_variable
   >   max_tokens: 5
   >   target_width: 1280
   >   ```
   The `message` field should be your prompt. The quality of the ESP32Cam is pretty low, and it is a non-optimal distance from the control panel, so it
   appears small in the frame of the stream. However, it is clear enough for my proof of concept.

   ![snapshot_camera_esp32cam_ai_my_camera_3_3_2025, 2_27_35 PM](https://github.com/user-attachments/assets/f09d5a02-ebc8-49fd-a9ea-ed31cf2e0391)

7. This prompt returns the response `35001` and updates the entity `sensor.llmvision_test_variable`. Combining the values into a single sensor helps cut down on
   the number of RPD to your LLM provider. Then from there, you can use templates to split the value out into separate helpers.
   > For example:
   > 
   > ```{{ (states('sensor.llmvision_test_variable') | int(0) | string)[:2] }}``` = 35, the humidity
   > 
   > ```{{ (states('sensor.llmvision_test_variable') | int(0) | string)[2:-2] }}``` = 0, the maintenance LED is off
   > 
   > ```{{ (states('sensor.llmvision_test_variable') | int(0) | string)[3:-1] }}``` = 0, the filter change LED is off
   > 
   > ```{{ (states('sensor.llmvision_test_variable') | int(0) | string)[4:] }}``` = 1, the humidifier is on (running)
   > 

9. Once you have gotten your tests where you want them, you can you can create an automation to update the sensor on a schedule using the same action data as your tests.
 
