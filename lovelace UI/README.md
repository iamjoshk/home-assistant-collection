## Dashboards

Current [mobile dashboard](https://github.com/iamjoshk/home-assistant-collection/blob/main/lovelace%20UI/mobile_dashboard.yaml) with fixed header and footer using sections.
The dashboard requires:
+ using Sections view in the dashboard
+ using the Wallpanel add-on: https://github.com/j-a-n/lovelace-wallpanel
+ using the card-mod add-on: https://github.com/thomasloven/lovelace-card-mod
  - card-mod in cards
  - [card-mod theme](https://github.com/iamjoshk/home-assistant-collection/blob/main/lovelace%20UI/card_mod_theme.yaml)
+ creating helpers:
  - Toggle (input_boolean) helpers to turn room views on and off in the header chips
  - Group helpers for the quick status chips in the footer
+ creating an automation to prevent multiple room view toggles from being on at the same time


