# Troubleshooting

Notes about issues encountered with the NUT addon and NUT integration and steps taken to resolve.

1. Error fetching NUT resource status data / ERR DATA-STALE
  + NUT device becomes unavailable in the integration.
  + The error: `Error fetching NUT resource status data / ERR DATA-STALE` is in the NUT addon log.
  + WORKAROUNDS reported are:
    + restarting the NUT addon and reloading the NUT integration
    + rebooting HA
    + unplugging the USB cable between the UPS and HA, then plugging it back in and restarting the addon and integration
  + github issue here: https://github.com/home-assistant/core/issues/152219

2. NUT integration not connecting to NUT addon
  + Error in the integration indicates that connection cannot be made to 172.30.33.1
  + RESOLUTION/WORKAROUND:
    + Use SSH addon to check the IP address of the NUT addon using command: `docker exec addon_a0d7b954_nut hostname -I` with response received `172.30.33.3`.
    + Reconfigure NUT integration to use HOST `172.30.33.3` instead of `a0d7b954_nut`.
  + Unknown why IP address for the NUT addon changed.
  + Checked after some time (hour or two) and updated hostname in the integration to `a0d7b954_nut` again and it worked. 
