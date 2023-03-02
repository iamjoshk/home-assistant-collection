## Overview
Utilizes [gphotos-sync](https://gilesknap.github.io/gphotos-sync/main/index.html) to sync a Google Photos album to a Raspberry Pi 4 running Home Assistant OS.

Github: https://github.com/gilesknap/gphotos-sync

## Activities

## Installing `gphotos-sync`
I followed the instructions for [Local Installation](https://gilesknap.github.io/gphotos-sync/main/tutorials/installation.html#local-installation).

You will need to create a Google OAuth Client ID (you might have done this previously for another integration...)
https://gilesknap.github.io/gphotos-sync/main/tutorials/oauth2.html

The first time you run gphotos-sync, you will need to authorize the application in your Google account. This where I ran into a problem. The solution is found within this issue [356](https://github.com/gilesknap/gphotos-sync/issues/356).
Basically, I ended up installing gphotos-sync on a separate machine, running gphotos-sync to get through the authorization process, then moved the generated `.gphotos.token` file to my HAOS device and placed it in the `[your_destination_here]` directory mentioned below.

For the initial run, I recommend using a command similar to 

`gphotos-sync [your_destination_here] --secret [your_secret_location_here/client_secret.json] --skip-albums --skip-files --skip-index
`

+ `[your_destination_here]` is the directory you want gphotos-sync to place the synced photos and albums
+ `[your_secret_location_here/client_secret.json]` is where your `cient_secret.json` file is located - specifically if not in the default directory that `gphotos-sync` is expecting.
+ `--skip-albums --skip-files --skip-index` skips all the syncing so you can just worry about the authorization process.

Once you have completed the authorization and generated your `.gphotos.token` file is in place, you can run `gphotos-sync` with whatever attributes you prefer.

I use: 

`gphotos-sync [your_destination_here] --secret [your_secret_location_here/client_secret.json] --album ["your photo album name"] --use-flat-path --omit-album-date`


+ `--album` specifies the album you want to sync and prevents gphotos-sync from syncing other photos and albums.
+ `["your photo album name"]` is the name of your album in Google Photos. The name is case sensitive and use double quotes if the album name has spaces. 
+ `--use-flat-path` creates the sub-directories in the generated `Photos` directory as `YYYY-MM` instead of nesting the directories like `YYYY\MM`.
+ `--omit-album-date` similarly prevents sub-directories from being created and just creates the `your photo album name` directory as a sub-directory of `albums`. I found this to be a little easier for setting up the photos for the wall panel screensaver below.

> Note: currently I just run the `gphotos-sync` command manually from the command line using the `SSH & Web Terminal` add-on whenever photos are added to the album. If I get around to automating the process, I will update this documentation.

Now that the photos are located locally on your HA device, you can use them for whatever you want.

## Creating a digital photo frame

I use them to create a digital photo frame on a wall mounted tablet that is running [Fully Kiosk](https://www.fully-kiosk.com/) (for the dashboard interface) and the HA add-on [Wallpanel](https://github.com/j-a-n/lovelace-wallpanel) (for the screensaver).

> Note: On my HAOS device, my photo album directory is located in `/config/media`. The following HA set up is based on that information.

In my `configuration.yaml` I have the following entry:
```
homeassistant:
  media_dirs:
    local: /config/media
```

In the dashboard for which I am using wallpanel, I use the following in the dashboard yaml.
```
wallpanel:
  enabled: true
  hide_toolbar: true
  hide_sidebar: true
  fullscreen: true
  image_url: /local/your_destination_here/albums/
#note the image_url needs to include the destination directory you used in the gphotos-command above
  image_fit: contain
  image_order: sorted
  style:
    wallpanel-screensaver-container:
      background-color: '#000000FF'
    wallpanel-screensaver-info-box:
      '--wp-card-width': 300px
      background-color: none
    wallpanel-screensaver-info-box-content:
      '--ha-card-background': none
      '--ha-card-box-shadow': none
      '--ha-card-border-width': 0px
      '--primary-background-color': '#fafafa'
      '--secondary-background-color': '#e5e5e5'
      '--primary-text-color': '[#212121](https://github.com/j-a-n/lovelace-wallpanel/issues/212121)'
      '--secondary-text-color': '[#727272](https://github.com/j-a-n/lovelace-wallpanel/issues/727272)'
  cards:
#this puts a semi-transparent weather and clock display in the upper right corner of the screensaver photo display.
#you may need to adjust placement and size.
    - type: custom:clock-weather-card
      entity: weather.your_weather_integration
      sun_entity: sun.sun
      hide_forecast_section: true
      animated_icon: false
      locale: en-US
      date_pattern: MMMM dd y
      time_format: 12
      card_mod:
        style: |
          ha-card {
            padding-right: 15px !important;
            width: 300px
          }
          ha-card img.grow-img {
            padding-right: 40px !important;
          }
      wp_style:
        width: 300px
        grid-row: 1
        grid-column: 1
        '--ha-card-background': '#ffffff66'
        '--ha-card-box-shadow': none
```

