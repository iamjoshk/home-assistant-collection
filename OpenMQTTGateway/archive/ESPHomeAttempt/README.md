This directory holds the remnants of my attempt to set this up with ESPHome. Unfortunately, I did not save the `yaml` configuration for the device.
I used dbuezas' great work as a starting point. https://github.com/dbuezas/esphome-cc1101
I modified the `cc1101.h` file to separate tx and rx pins (`GDO0` and `GDO2`) and removed `noInterrupts();` from the `beginTransmission` class. 

