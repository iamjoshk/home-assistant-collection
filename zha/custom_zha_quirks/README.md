The files contained within `custom_zha_quirks` are the files that you would place in your `/config/custom_zha_quirks` directory.

+ 3RSM0147Z_v2.py exposes humidity as (soil) moisture, which is what it is intended for.
+ LDHD2AZW_v2.py exposes the battery percentage.
+ b1naus01_v2.py enables decoupled mode and produces `zha_event` events for on and off.

+ [`e1e_g7f.py`](https://github.com/iamjoshk/home-assistant-collection/blob/main/zha/custom_zha_quirks/e1e_g7f.py): this is a quirk that I modified for my own use, forked from the original [`zha-device-handlers`](https://github.com/zigpy/zha-device-handlers) repo.
