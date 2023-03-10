## Overview

Details on [MZ-Z19B](https://esphome.io/components/sensor/mhz19.html) connected to ESP32-WROOM-32D

## Pinout
+ Only `Tx` `Rx` `Gnd` and `Vin` need to be connected to ESP32 as indicated on esphome.io
+ version with JST:

| JST Position |  JST cable Color |MH-Z19B Pinout | Esp32 Pinout |
|----|----|----|----|
| 1 | Brown  | Vo |
| 2 | White  |    |
| 3 | Black  | Gnd| Gnd    |
| 4 | Red    | Vin| 3V3    |
| 5 | Blue   | Rx | GPIO32 |
| 6 | Green  | Tx | GPIO35 |
| 7 | Yellow |    |
