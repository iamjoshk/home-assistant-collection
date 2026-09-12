## Vent Fan Controller

#### An ESPHome node to control 2 PWM fans in a HVAC register vent for better air circulation.
The primary bedroom in my house has a single supply vent for the HVAC and it is barely sufficient. I decided to create a DIY vent fan controller similar to SmartCocoon Register Booster (which incidentally can also be [flashed with ESPHome](https://community.home-assistant.io/t/request-for-integration-smart-cocoon-smart-fans/561921/10)...) with local control.

This is based off of https://github.com/patrickcollins12/esphome-fan-controller

Parts used:
1. Seeed Studio ESP32S3
2. Two 120mm Corsair PWM fans (https://www.amazon.com/dp/B0D49QZ5SH)
    + One fan is $14.99 but the three pack is pretty consistently marked down to $30. I saved the third fan as a backup.
3. 12v 2.5a power supply with adapter (https://www.amazon.com/dp/B0GWV8RFLY)
4. Adjustable voltage regulator (https://www.amazon.com/dp/B0DBVYP91F)
5. 4 pin connector for a nicer connection to the breadboard (optional) (https://www.amazon.com/dp/B0BMDQLR4Q)
6. 470uF electrolytic capacitor (optional) (https://www.amazon.com/dp/B0F8C43XK9)
7. Small breadboard
8. Project box (https://www.amazon.com/dp/B07ZRBCCVC)

One requirement for this project was that it needed to look a bit nicer and finished. The project box holds everything nicely.

[vent-fan-controller.yaml](https://github.com/iamjoshk/home-assistant-collection/blob/main/ESPHome/vent-fan-controller/vent-fan-controller.yaml): config for the controller.

I want my vent fan to turn on when the HVAC blower turns on. I don't need it to try and reach a specific temperature. This is all about increasing air circulation.
My config creates a switch in Home Assistant that lets me adjust the speed of the fan. I have min and max speeds set on the output because below 16% power, the fan turns off. I picked 84% max power because the math works out that 50% in HA is actually 50% true power (or very close to it) and I like that.

I track the voltage and RPM just for datapoints that are interesting and could be helpful for tracking how effective the fan is doing its job.

Other than that, this is a pretty simple build.

I have an automation in Home Assistant that sets the fan speed variably based on the HVAC action and time of day. It has been working very well. 50% power is basically silent even at night.

### The Build

Follow the build instructions at https://github.com/patrickcollins12/esphome-fan-controller.
+ It is important to make sure you connect the 12v power supply ground to the ESP32 ground otherwise your fans will not turn off.
+ The capacitor is optional but smooths when plugging the power in (or if power returns from an outage) and the ESP32 booting up and enabling wifi. It is placed after the voltage regulator and before the ESP32S3.
+ The 4 pin connector is also optional, it was just easier to connect the PWM cable to the breadboard. The connector needs to be trimmed.
+ I connected the 2 fans together since I did not need independent control.

