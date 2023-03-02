## Overview

Basic instructions on adding custom `zha_quirks` to your Home Assistant instance. This assumes you already have a custom `zha_quirk` that you want to use.

## Activities
1. In your `/config` directory, create a new folder for your custom quirks. For example, `custom_zha_quirks`.
2. In `custom_zha_quirks` place the custom quirk you want to use. For example, `e1e_g7f.py`.
3. If your device is already added to Home Assistant, you will need to remove it.
4. Reboot Home Assistant.
5. When Home Assistant is finished rebooting, add your device back to your ZHA integration.
6. Your device should automatically select your custom quirk in your `custom_zha_quirks` folder.

