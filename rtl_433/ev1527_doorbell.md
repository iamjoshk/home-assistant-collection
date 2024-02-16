## Generic RF doorbell using an EV1527

I ordered a cheap 433MHz doorbell. Unfortunately, the transmission was not a decoded by `rtl_433` automatically. I needed to set up a flex decoder. While it is working, I am still tweaking it to improve reliability.

I added the following to my `rtl_433` config file.

```
decoder {n=doorbell_ev1527,m=OOK_PWM,s=164,l=552,r=5680,g=584,t=152,y=0,repeats>=5,rows>=25,bits=25,countonly,unique,get=@0:{24}:id,get=@0:{25}:channel
```

This is based off of the Elro_DB270 conf at https://github.com/merbanan/rtl_433/tree/master/conf. There are several EV1527 confs, including one a Reolink doorbell. The EV1527 is very common, but the timings are different for every device which is pretty annoying and this is why it requires a flex decoder. The right way to get the best flex decoder settings is to use rtl_433 to analyze the signal for your specific device and then set your flex decoder appropriately. I plan to do this at some point, but until then this is working relatively well. 
