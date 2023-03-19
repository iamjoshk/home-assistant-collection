## Overview
### Network UPS Tools set up

This set up guide is for using Network UPS Tools (NUT) with Home Assistant OS. This utilizes the community add-on [Network UPS Tools](https://github.com/hassio-addons/addon-nut) and the [NUT integration](https://www.home-assistant.io/integrations/nut).

### Preliminary Set Up
+ Confirm that your UPS is on the [hardware compatibility list](https://networkupstools.org/stable-hcl.html)
  > This guide uses the Tripp Lite INTERNET550U as the example UPS
+ Set up your UPS and plug in your devices.
+ Connect the USB from the UPS to your Home Assistant device.

### Install the Network UPS Tools add on.
1. Navigate to Add Ons, then click `Add-On Store`
2. Under `Home Assistant Community Add-ons` select Network UPS Tools
3. Click Install
4. Read the documentation
5. Under Configuration set up the parameters for your UPS. <br>
Example configuration:
```
devices:
  - config: []
    driver: usbhid-ups
    name: office-ups
    port: auto
mode: netserver
shutdown_host: false
users:
  - actions: []
    instcmds:
      - all
    password: ""
    username: ""
```

+ You need to change the driver name based on what is listed for your UPS on the [hardware compatibility list](https://networkupstools.org/stable-hcl.html).
+ After starting the add-on, check the log. For the Tripp Lite INTERNET550U, there was an error even though it was listed as the supported driver.  

`This TrippLite device (09ae:3024) is not (or perhaps not yet) supported by usbhid-ups. Please make sure you have an up-to-date version of NUT. If this does not fix the problem, try running the driver with the '-x productid=3024' option.`

In the configuration, change the `config` option to:
```
  - config: [productid=3024]
```
then save.

Check the log again. If it loads successfully, move to the next step.

### Add the Network UPS Tools Integration
1. Go to Integrations
2. Add Integration
3. Search for Network UPS Tools and add the integration
4. ***Important!*** In the Integration configuration, update `Hostname` to the hostname found on the Info page in the NUT add-on. <br>
  Example: `a0d7b954-nut`
5. Leave port unchanged (unless you've specified it in the NUT add-on configuration).
6. Username and Password are not needed.
7. Submit.
8. All done!

> Note: the entities created are dependent upon the supported sensors for your specific UPS.
