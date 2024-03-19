---
layout: post
title:  "Building a BLDC Driver - The Schematic"
date:   2024-02-14 16:51:36
categories: [category]
---

#
## Introduction

We can split the entire schematic into four sub-sections:
1. Digital logic/control circuitry
2. Local power supplies and regulation
3. Motor sensing circuitry
4. Motor driving

## 1. Digital Logic & Control
![DigitalSheet](/assets/building-bldc/Screenshot%202024-03-03%20at%201.30.13 AM.png)
#### Overview
The board is entirely based around the RP2040, who's many advantages outweigh the disadvantages. Specifically, the RP2040 is [cheap](https://www.mouser.com/ProductDetail/Raspberry-Pi/SC09147?qs=T%252BzbugeAwjhSpdbCB4ve%252Bg%3D%3D) and widely available dual-core ARM Cortex M0+ with 2 cores that runs at ~130MHz (though, we can overclock this both [responsibly](https://forums.raspberrypi.com/viewtopic.php?t=301902) and [irresponsibly](https://www.raspberrypi.com/news/dont-try-this-at-home-overclocking-rp2040-to-1ghz/))

The RP2040's got an amazing SDK, which is very well documented in traditional Raspberry Pi Foundation style. Furthermore, it's [PIO cores](https://tutoduino.fr/en/pio-rp2040-en/) make this device incredibly flexible. You can emulate several simultaneous SPI busses that are all pulling/pushing from/into DMA without any main processing core intervention whatsoever. There are 8 PIO blocks divided into 2 different instances, but I don't want to get too heavily into the semantics. What's particularly cool about this is that these PIO blocks are programmed with a custom assembly instruction set made specifically for the RP2040 - which means that these blocks run each instruction at *system speed*. This means we can generate PWM signals of, yes, up to 65MHz! We'll end up seeing some practical uses of these PIO blocks later.

For this revision, since this is intended to be a hardware development platform, I chose to integrate the RP2040 by simply using the Raspberry Pi Pico - the development board based on the RP2040. This was done because, more times than I'd like to admit, I've somehow damaged the RP2040 or some of it's GPIO pins - so it's *incredibly* nice to be able to pull out the malfunctioning one and place in a functioning one. In later revisions, I'll integrate the RP2040 right onto the board.

#### Power
The Raspberry Pi Pico will give an output of 5V and 3.3V (from it's own terrible onboard buck regulator). We optionally allow the Raspberry Pi Pico to supply the motordriver's 5V and 3.3V rails from it's own (all from a USB connection when plugged in) to make developing a bit easier. [The Raspberry Pi Pico's 3.3V buck regulator is awful.](https://pico-adc.markomo.me/PSU-Noise/)

#### Breakouts
**SPI Control**
To control the motor driver, it was determined that SPI would be the most practical for the following reasons.
1. The RP2040 can attach an interrupt to the CS pin of the master SPI control bus, meaning we are never listening for data but only paying attention when data is present
2. The SPI bus is very low latency - USB Serial has a best-case latency of 1ms 
3. Datarate - the SPI bus can achieve a very modest 1.25MB/s. If the control loop of our motor runs at a rate of 10kHz (very fast), we can expect a max of 125 bytes in 1/10th of a millisecond - plenty for our purposes. For comparison, i2c in it's highest supported speed configuration is 3400kBit/s which is 425MB/s... Not so good. i2c is also subject to some more noise concerns over long wires, and since i2c is open drain/open collector, that makes differential signaling over said long wires a lot more complicated. 

**IMU Header**
We breakout a simple SPI interface (the standard MOSI/MISO/SCK pins) as well as a GPIO CS pin to be able to read an IMU at a fast datarate eventually. This is more of an extension to help aid with calibrating our control algorithms later on.

**Encoder Header**
Finally, we breakout another header that will be compatible with the AMT102V encoder, but can also be adapted to run a fake SPI bus to interface with SPI magnetic encoders. How, you ask? Not bitbanging. Well - yes bitbanging but bitbanging at system clock speed. As aforementioned, we can use PIO blocks to emulate a SPI interface on ANY GPIO pins we want, and be constantly pulling data into DMA to be easily accessed *without* any latency within our control loop. Kind of beautiful that we can not waste either of our true SPI drivers or either of our main processing cores on something so simple.

#### Closing Notes
**Practical PIO** The last thing worth mentioning is that we take advantage of the PIO PWM mentioned earlier for the ADC_CLKIN output. Our ADC, the ADS131M04 (more on that later), needs a clock input to trigger sampling. The frequency needed to achieve the highest sample rates is 8.192MHz, which we generate using PIO blocks.
```
; Side-set pin 0 is used for PWM output

.program pwm
.side_set 1 opt
loop:
    nop         side 1
    nop         
    nop         
    nop         
    nop         
    nop         
    nop         
    nop         
    nop        side 0
    nop        
    nop        
    nop        
    nop        
    nop         
    nop        
    jmp loop


% c-sdk {
static inline void pwm_program_init(PIO pio, uint sm, uint offset, uint pin) {
   pio_gpio_init(pio, pin);
   pio_sm_set_consecutive_pindirs(pio, sm, pin, 1, true);
   pio_sm_config c = pwm_program_get_default_config(offset);
   sm_config_set_sideset_pins(&c, pin);
   pio_sm_init(pio, sm, offset, &c);
}
%}
```
This code gives us approximately a 16 clock divider from the approximately 130MHz system clock, resulting in approximately 8.125MHz. That's a lot of 'approximately', which is because I've measured the actual frequency to be 8.000-8.100MHz and I don't really care to investigate further.

<details markdown="1">
<summary>See GPIO Map</summary>

![a](/assets/building-bldc/Screenshot%202024-03-03%20at%2012.54.26 AM.png)

</details>

## 2. Local power supplies and regulation
![DigitalSheet](/assets/building-bldc/Screenshot%202024-03-03%20at%201.31.18 AM.png)

