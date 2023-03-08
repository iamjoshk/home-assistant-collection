## Overview

Details on [MZ-Z19B](https://esphome.io/components/sensor/mhz19.html) connected to ESP32-WROOM-32D

## Pinout
+ Only `Tx` `Rx` `Gnd` and `Vin` need to be connected to ESP32 as indicated on esphome.io
+ Connections without JST:

| Position | Pinout | Color | Esp32 |
|----|----|----|----|
| 1 | Vo | Brown  |
| 2 |    | White  |
| 3 | Gnd| Black  | Gnd |
| 4 | Vin| Red | 5v |
| 5 | Rx | Blue | GPIO32 |
| 6 | Tx | Green | GPIO35 |
| 7 |    | Yellow |


