## Generic RF doorbell using an EV1527

I ordered a cheap 433MHz doorbell. Unfortunately, the transmission was not a decoded by `rtl_433` automatically. I needed to set up a flex decoder. While it is working, I am still tweaking it to improve reliability.

I added the following to my `rtl_433` config file.

```
decoder name=doorbell,modulation=OOK_PWM,short=200,long=580,tolerance=152,gap=564,reset=5824,bits>=24,rows>=25,unique,countonly,get=@0:{24}:id
```

This is based off several of the EV1527 confs at https://github.com/merbanan/rtl_433/tree/master/conf. This includes a Reolink doorbell. The EV1527 is very common, but the timings are different for every device which is pretty annoying and this is why it requires a flex decoder. The right way to get the best flex decoder settings is to use rtl_433 to analyze the signal for your specific device and then set your flex decoder appropriately. I plan to do this at some point, but until then this is working relatively well. 
