<!-- ---
layout: post
title:  "Exoskeletons and Motors 2 - Building A BLCD Driver"
date:   2023-09-23 13:14:26
categories: [category]
--- -->
## Introduction
In this post, I will begin with creating a set of requirements and constraints for my design. We will then break the solution into four different components, explain 

## Version 0.1

Version 0.1 is split into four sub-sections:
1. Digital logic/control circuitry
2. Local power supplies and regulation
3. Motor sensing circuitry
4. Motor driving

## Motor Drive:
ABC
### Operating Theory

The Motor Drive section has to serve two main functions:

- Three half-bridges, allowing for sourcing or sinking current from any of the three phase-connections
- Optimal performance is defined as fast switching, high efficiency, high voltage/current capabilities
- Finally, the current through each coil needs to precisely be known at a high speed in order to achieve low latency FOC (field oriented control)

### Component Selection

The motor drive circuitry is, in essence, just mosfets in a special configuration and some supplemental components to help those mosfets work best. We need to organize the mosfets in three H-bridges to be able to drive the BLDC, and chose the right mosfets and design elegant supporting circuitry to improve performance.

The mosfets chosen were selected for the following reasons:

- Maximum Vds and Ids: The maximum Vds and Ids were well above our expected maximum
- Rds: The Rds was low which means low losses in the mosfets when they are fully on. However this is only guaranteed in the fully on state, and mosfets are not fully on while they are transitioning from off-to-on or on-to-off.
- Gate Capacitance: The gate capacitance also was low because higher gate capacitances means it takes longer for the equivalent capacitor created at the gate’s silicon junction to charge, leading to a simply longer time to fully turn on. During that time it takes to charge up, the mosfet itself is actually in a higher-resistance state. For typical applications, this doesn’t much matter, because either the mosfet itself is not switching high currents or it is not being PWM-pulsed at a very high frequency. However, in this case, where we are switching high current at a high speed, we absolutely need to do everything possible minimize inefficiencies.

Note that I said frequency and not duty cycle - it is the frequency of operation that matters most when considering gate capacitance, and not the duty cycle. Also - practically - the duty cycle is not constant and completely indeterminant in field-oriented-control, which means we need to consider the worst case, which is the maximum drive frequency. The time to fully turn on is dependent on only the gate voltage and equivalent gate capacitance, which is essentially constant, and therefore as the frequency increases 

<!-- ![Untitled](Untitled%2037186a4120414e62856bf80df2bcbbe9/Untitled.jpeg) -->

TODO continue with frequency and draw the smoothed-square-wave

## Sensing:

### Operating Theory

The sensing section is the most complex and has the most functionality

- Three current-sense amplifiers with adjustable gain
- One multi-channel high-speed 10-bit ADC that outputs its data in parallel format (more on that later)
- Finally, a single temperature sensor is included on the board (however, in routing Version 0.1, it was not placed close enough to the mosfets to be particularly useful).

### Component Selection

Current Sense Amplifiers:

Each phase has two parallel 2mOhm shunt resistors, for an equivalent series resistance of 1mOhm. At any given moment when driving the motor (not braking or coasting), exactly one half-bridge will be sourcing current and another will be sinking current. This means that if we add current sensing capabilities to only two of the half-bridges, we could effectively always measure the coil current through the motor. However, for the sake of this revision, it was determined that the marginal added cost was more than worth the potential time saved debugging. The precise resistance was chosen to me 1mOhm because at higher currents, the primary concern becomes the power dissipation of the sensitive shunt resistors, more so than the actual sense-able voltage drop.

The power dissipation for a shunt resistor is given by the following

$$
P=(I^2)R
$$

Whereas the voltage drop across a shunt resistor is given by

$$
V=IR
$$

At 50A, the power dissipation across a 1mOhm resistor is a massive 2.5W. Note - we are using two shunts in parallel, so theoretically the power consumption between the two is equally split (1.25W per resistor) which is fortunately safely under the maximum wattage of our [chosen shunt resistor](https://www.notion.so/37186a4120414e62856bf80df2bcbbe9?pvs=21). For context, the average power of my M1 Macbook Air while writing this (with multiple apps open, including EagleCAD and Chrome) was just about 2.5W. The power consumption of just the shunt resistors alone when a 50-amp motor is connected could itself power my computer’s entire CPU. That’s all just to show how massive the power consumption of shunt resistors can be, due to their squared proportionality to current. 

<!-- ![Untitled](Untitled%2037186a4120414e62856bf80df2bcbbe9/Untitled%203.png) -->

Each phase, therefore, has current sensing capabilities through a [low-side](https://www.google.com/search?sxsrf=APwXEddz8kJJu5bUV-iESsi4bSXwxBztvA:1682568787677&q=low+side+vs+high+side&tbm=isch&sa=X&ved=2ahUKEwiA4ZiXmcn-AhUsIkQIHYDpBVAQ0pQJegQIChAB&biw=1600&bih=1598&dpr=0.8#imgrc=gkDsywB1BgVp-M) shunt resistor. Using ohm’s law, we can see that the voltage drop across the shut resistor is equal to

 

$$
Vshunt=I * Rshunt
$$

At a maximum current of approximately 50A (constrained primarily by the copper on the board, not the mosfets), the voltage drop will only be at max 0.05V. This resulting voltage quite low and it’s also prone to noise. We could use a 10x (0.5V output at max current), or even a 80x amplifier (4V output at max current), to help amplify this voltage. This amplifier would be placed as close to the current shunt to minimize the attenuation of noise along longer traces. 

However, we can reasonably expect motor currents to only be in the range of 1-10A in some applications, which would result in a worst-case maximum voltage drop of a mere 0.001V (1A across a 0.001 shunt). Still, even with an 80x amplifier, that voltage would only be amplified to 0.08V - which itself is tiny.

We realize the need for an adjustable-gain current amplifier, which was placed as close as possible to the shunt resistor.

The [MAX9939](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX9939.pdf) was chosen specifically for this purpose. It’s sort of the perfect chip for this application. We need an analog output to be used with the ultra-high speed ADC. We also need to be able to fine-tune the gain in the order of approximately 160x. It is SPI addressable and even includes an additional internal amplifier to allow for differential outputs, further helping us minimize the effect of noise across longer traces. This is especially important in our case, because the three half-bridges of the motor are far-separated from each other given the trace widths and mosfet sizes - and so the outputs of these amplifiers likely have to travel a far length (in the order of centimeters) near high-current signals, the perfect storm for bad noise. Read more about differential signals and how they minimize noise [here](https://hackaday.com/2016/03/29/when-difference-matters/) if you’re interested.

We’ve established the need for our current-sense amplifier and found the best-fit part. Fortunately, our MAX9939 gives us the following available programmable gains.

0.2V/V, 1V/V, 10V/V, 20V/V, 30V/V, 40V/V, 60V/V, 80V/V, 119V/V, and 157V/V

To see the maximum dynamic range, we can calculate the voltage drops for the lowest expected current and the highest expected current, and then select the amplification that maximizes that voltage as long as it’s under 4.096. For reference, our ADC (to be discussed in more detail in the next section) has a voltage reference of 4.096V. That means that each bit of our 10-bit ADC allows us to sense, at most, 0.004V/bit. But, again, more on that later. 

At a maximum current of 50A, we have a voltage drop of 0.05V, which we can amplify to 3V using the 60V/V setting (Why not 80V/V? More on that later). 

$$
Vout(Iout) = Gain * IR = 60*(Iout)(0.001)
$$

We also know that the minimum detectable voltage is 0.004V (equivalent to a 10b0000000001 from the ADC, but again, more on that later). If we set the Vout to be exactly the lowest detectable voltage, we see the increment of current we can sense. 

$$
0.004 = 60*(Iout)(0.001)
$$

$$
Iout = 0.067A
$$

Being able to detect up to 50A with steps of 60mA is spectacular.

Now, at a minimum expected current of 1A, we have a voltage drop of 0.001V, which we can amplify to 0.157V using the 157V/V setting.

$$
0.004 = 157*(Iout)(0.001)
$$

$$
Iout = 0.025A
$$

Being able to detect currents as low as 1A with steps of 25mA is also spectacular when we consider that we can achieve this without any desoldering and re-soldering of shunt resistors. This range-switching is done completely automatically. More on this in another blog post, but a technique the Odrive uses is to pulse a known voltage across the motor and detect current to determine the maximum current and adjust the amplifiers to that maximum current *********only once*********.

Note - we use 60V/V instead of the 80V/V so that we do not accidentally apply too high of a voltage to the ADC. 80V/V would result in a theoretical max output voltage from the amplifier into the ADC of 4V - which only leaves 0.096V of headroom, and when dealing with high-inductance coils, it’s a reasonable risk to see higher than expected currents. 

ADC:

Temperature Sensor:

The temperature sensor chosen was the [PCT2075](https://www.nxp.com/docs/en/data-sheet/PCT2075.pdf) because of its [availability](https://octopart.com/search?q=pct2075&currency=USD&specs=0) and [price](https://www.mouser.com/ProductDetail/NXP-Semiconductors/PCT2075TP147?qs=8kBc1%252BPe71eEyKWf3YBaGA%3D%3D). It is a simple i2c-capable temperature sensor. Conveniently, the thermal pad on the bottom of the HWSON8 package is directly coupled to the temperature sensor internally. The datasheet says “For enhanced thermal, electrical, and board-level performance, the exposed pad should be soldered to the board using a corresponding thermal pad on the board, and for proper head conduction through the board thermal vias need to be incorporated in the PCB in the thermal pad region.”