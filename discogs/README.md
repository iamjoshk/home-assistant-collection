# Discogs and Pixel Album Art

## Discogs
I really wanted to integrate my Discogs collection into Home Assistant and was pretty underwhelmed by the core integration. I wanted to see individual releases from my collection as a way for guests to browse and pick physical media to play.

That led to creating my custom integration [Discogs Sync](https://github.com/iamjoshk/discogs_sync). Discogs Sync leverages an authenticated API call to retrieve your user collection, folders, and wantlist. It also allows the user to download cover art and thumbnails. Discogs does not allow for unauthenicated downloads of images.

Discogs collections can be huge, and even a small collection would exceed the limits for states and attributes. The actions to download collections and wantlists return responses only or provide an option to download the results to JSON. It does not save it in an entity because of the size. To workaround this, Flex Table Card can take the response from the action and populate a table for viewing. This works great to display a live view of your collection.

There is also the random record entity that makes an API call and returns a random release from your collection. You can specify the folder you want to use for the random selection. I found this is a great way to pick an album to play when you just can't decide what to listen to.

<img width="1000" height="1056" alt="discogs_dashboard" src="https://github.com/user-attachments/assets/256250e3-b332-47c4-9ba5-e7dbf8995d26" />

---


## Pixel Album Art
I was gifted an [Apollo Automation M-1](https://apolloautomation.com/products/m-1-led-matrix) HUB75 LED matrix display for the holidays. This enabled another idea I had to display the random record cover art on a lofi pixel display. The trick was converting the cover art for the display. I attempted to use [Apollo Automation's fork of Pixel Magic Tool](https://github.com/ApolloAutomation/PixelMagicTool) but even the thumbnails seemed to present it with a challenge for converting the images. I couldn't get the images to load on the M-1 with any consistency and compression often rendered the image completely unrecognizable. The black box that is WLED didn't help. While searching for solutions, I discovered [WLEDVideoSync](https://github.com/zak-45/WLEDVideoSync) which streams a live image to WLED devices. This worked great via the project's webUI. The next challenge was integrating that functionality into Home Assistant. This led me to creating my custom integration [HA DDP2WLED](https://github.com/iamjoshk/ha_ddp2wled) which lets you use an action to start a DDP stream to a specified WLED host. From there it was a matter of telling it which image to stream to the LED display. This is when I discovered that Discogs doesn't allow unauthenticated downloads of the cover art or thumbnails for releases. So I added the image download action to the Discogs Sync custom integration. This action allows you to download either the cover image or the thumbnail to local storage. Using images from local storage is Discogs' preferred way for API integrations to leverage their images, since it is resource heavy to repeatedly download and use images from their servers. I use thumbnails from Discogs since they are much smaller and the detail is not needed for the display.

Discogs Sync combined with HA DDP2WLED enabled my vision of displaying lofi pixel versions of album art on the M-1.

You can use album art provided by other integrations, like Music Assistant or other media integrations, to stream to the LED matrix. I use a Wiim Ultra for streaming and when it is actively streaming, I use the album art from the [Wiim custom integration](https://github.com/mjcumming/wiim) for the display. A longer term goal for me is to implement song recognition via audio clips so I can look up album art on MusicBrainz or similar services when I am using analog music sources like a turntable or CD player or cassette player.

<img width="300" alt="coltrane" src="https://github.com/user-attachments/assets/14ec6c01-4665-4542-b025-e9ff9e4c9e1a" /><img width="300" alt="eurythmics" src="https://github.com/user-attachments/assets/a62d4265-6690-43dd-8775-8adfe760a834" /><img width="300" alt="hancock" src="https://github.com/user-attachments/assets/d51cfd43-07e0-42de-a33b-a3ea684e0026" />



