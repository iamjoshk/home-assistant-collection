# "Persistent" Wireless ADB Bridge for a Facebook Portal

## Goal

Enable wireless ADB access to a Facebook Portal running [Immortal](https://github.com/starbrightlab/immortal) and [Kiosk Satellite](https://kiosksatellite.com/), using a Raspberry Pi as a permanently USB-tethered relay — so wireless ADB comes back automatically after every Portal reboot, without manually reconnecting a cable.

The Portal's bootloader can't (currently) be unlocked, so it can't be rooted. On the Portal, the wireless ADB command `adb tcpip 5555` does not survive a reboot.

This workaround uses an RPi0 2W I had lying around permanently connected to the Portal over USB and reissues the necessary `adb` commands every time it detects the Portal has reconnected: when the Portal reboots, the RPi reboots, or the USB cable is disconnected/reconnected.

## Hardware

- **Raspberry Pi Zero 2 W** The RPi0 2W and not the RPi0W. The RPi0W is not compatible because it is 32-bit and `adb` needs 64-bit. `adb` installs on the RPi0W, but running it returns an `illegal instruction` response.
- **OS:** Raspberry Pi OS Lite (64-bit) — running headless to conserve resources.
- **Cabling:**
  - RPi0 2W's **USB** (data) port → micro-USB-to-USB-A OTG adapter → USB-A-to-USB-C cable → Portal.
  - RPi0 2W's **PWR** port powered separately from a standard USB power supply.

## Portal identification
If you don't already have it run `lsusb` to get the Portal's identification info. Response should be similar to: 
```
Bus 001 Device 006: ID 2ec6:1804 Facebook Portal
```
- Vendor ID: `2ec6`
- Product ID: `1804`

Replace the values for your Portal in the scripts below.

## One-time setup steps

1. Install `adb` on the Pi (`sudo apt install adb`).
2. Connect the Portal via USB, run `adb devices`, and accept the "Always allow from this computer" prompt on the Portal's screen. This authorization is stored in Android settings and **does** survive reboots.
3. Update the scripts with your portal's IP address and the vendor and product IDs.
4. Deploy the scripts and udev rule below.

## Scripts

### `enable-wireless-adb.sh`

Fires whenever the Portal (re)connects over USB. Waits for the device, runs the two Kiosk Satellite ADB commands, switches ADB into wireless mode, and verifies the wireless connection came up.

- `<user>` — the non-root Linux user on the RPi that owns the `adb` server and keys (the account you authorized the Portal from).
- Scripts are installed in `/usr/local/bin/` (`sudo cp` then `sudo chmod +x`), and the log is written to `/var/tmp/portal-adb.log` so it's writable by any user. Change either path to taste.
- `PORTAL_IP` is the Portal's reserved DHCP address; replace it with yours.



```bash
#!/bin/bash
LOCKFILE=/tmp/portal-adb.lock
LOG=/var/tmp/portal-adb.log
PORTAL_IP=<your portal IP address>   #good idea to have a DHCP reservation in your router for the portal so it doesn't chnage IP addresses

# Debounce: switching to tcpip mode itself causes a brief USB re-enumeration,
# which would otherwise re-trigger this script in an infinite loop.
if [ -f "$LOCKFILE" ]; then
    last=$(stat -c %Y "$LOCKFILE")
    now=$(date +%s)
    if [ $(( now - last )) -lt 30 ]; then
        exit 0
    fi
fi
touch "$LOCKFILE"

echo "$(date): Portal USB event detected, waiting for device..." >> "$LOG"

# Retry a few times to ride out USB flicker during the Portal's own boot sequence
attempt=0
until /usr/bin/adb wait-for-device; do
    attempt=$((attempt + 1))
    if [ $attempt -ge 5 ]; then
        echo "$(date): adb wait-for-device failed after $attempt attempts" >> "$LOG"
        exit 1
    fi
    echo "$(date): wait-for-device attempt $attempt failed, retrying in 3s..." >> "$LOG"
    sleep 3
done

# Disable Meta's package verifier so Kiosk Satellite updates can install
# (persistent Android setting — safe to reissue every time)
/usr/bin/adb shell settings put global package_verifier_enable 0
echo "$(date): package_verifier_enable set to 0" >> "$LOG"

# Start the Kiosk Satellite update helper (must be restarted every reboot)
/usr/bin/adb shell "content read --uri content://me.jxl.kiosk_satellite.update-helper/start | sh" >> "$LOG" 2>&1
echo "$(date): update helper start command issued" >> "$LOG"

# Switch ADB into wireless mode
/usr/bin/adb tcpip 5555 >> "$LOG" 2>&1
echo "$(date): adb tcpip 5555 issued, Portal IP is $PORTAL_IP" >> "$LOG"

sleep 3
/usr/bin/adb connect "$PORTAL_IP:5555" >> "$LOG" 2>&1

if /usr/bin/adb devices | grep -q "$PORTAL_IP:5555.*device"; then
    echo "$(date): wireless adb confirmed working at $PORTAL_IP:5555" >> "$LOG"
else
    echo "$(date): wireless adb connect did not succeed" >> "$LOG"
fi
```

### `/usr/local/bin/recheck-update-helper.sh`

Runs on a schedule as a backstop, in case the update helper is killed by something other than a full reboot (e.g. low memory).

```bash
#!/bin/bash
LOG=/var/tmp/portal-adb.log
PORTAL_IP=<your portal IP address>

/usr/bin/adb connect "$PORTAL_IP:5555" >> "$LOG" 2>&1

if /usr/bin/adb -s "$PORTAL_IP:5555" shell "content read --uri content://me.jxl.kiosk_satellite.update-helper/start | sh" >> "$LOG" 2>&1; then
    echo "$(date): [recheck] update helper start reissued via $PORTAL_IP:5555" >> "$LOG"
else
    echo "$(date): [recheck] failed to reach $PORTAL_IP:5555 - Portal may be offline or USB link needs attention" >> "$LOG"
fi
```

Both scripts need `chmod +x`.

## udev rule

`/etc/udev/rules.d/99-portal-adb.rules` — fires the main script as the `<user>` user (not root) any time the Portal's specific vendor/product ID (re)appears on the USB bus:

```
SUBSYSTEM=="usb", ATTR{idVendor}=="2ec6", ATTR{idProduct}=="1804", RUN+="/sbin/runuser -u <user> -- /usr/local/bin/enable-wireless-adb.sh"
```

Reload after editing:
```bash
sudo udevadm control --reload-rules
```

Note about `runuser -u <user>`: udev's `RUN+=` executes as root by default. The Pi's `adb` server (and its key/state files under `~/.android/`) belongs to the `<user>` user. Running the script as root pointed it at a different, non-existent adb context, causing `adb wait-for-device` to hang.

## Cron job (periodic recheck)

This was added as an extra check. Probably not necesssary, just covering my bases.
Added to `<user>`'s crontab (`crontab -e`):

```
0 */2 * * * /usr/local/bin/recheck-update-helper.sh
```

Runs every 2 hours, at the top of each even hour.

## Result

On every Portal reboot (or Pi reboot, or cable reseat), the following happens automatically:
1. Package verifier disabled (idempotent, mainly relevant on first run)
2. Kiosk Satellite update helper started
3. ADB switched to wireless mode
4. Wireless connection established and verified

From any machine on the same network:
```bash
adb connect PORTAL_IP:5555
```
