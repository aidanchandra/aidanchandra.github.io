---
title: Exoskeletons and Motors 0 - Introduction
date: 2023-09-15 13:00:00 +/-0800
categories: [Exoskeleton]
tags: [exoskeleton]     # TAG names should always be lowercase
math: true
---

## Introduction

Truly assistive movement for humans seeks to revolutionize the way we conceptualize several different fields and pushes the boundaries of what is possible in medicine, defense, and industry.

Effective assistive movement for humans has proven a major challenge for industry to address. The nature of human movement is difficult to assist in a natural and noninvasive manner. 

Some attempts have utilized machine-learning models to sense newly discovered nerve signals that precede actual movement, but to no avail. It is clear that human movement *must* be considered unpredictable but constrained.

So therefore we must conceptualize attempts at assistive movement as just that - assisting movement already initiated by the wearer. Movements should not be preprogrammed or predicted, but simply feel lighter.

## Problem Statement
We often consider motors as interfacing with the physical world in two ways, (1) either *'go-to'* positioning where we want a motor to go to a specific angle like sweeping a camera, or (2) to spin at a specific velocity, such as for a RC car. These control modes directly correspond to bsaic calculus principles - 'go-to' positioning being the function itself, and velocity control being a first-order derivative. 

However, it's a much less common application for motors to provide a set-torque. One great example of this is in segways - the torque of the motor driving the segway must be precisely modulated so as to not buck the rider off of the device, but also provide a forward motion.

The same requirement is present in exoskeletons. 

## Control Modes:
Imagine an exoskeleton system, where we can (miraculously) perfectly sense the pose of our user in small enough time-steps to generate an accuraate velocity of each of their limbs, as well as accelerometers/IMUs to be able to detect the linear and angular acceleration on any limb of the body.

With all this data available, let's walk through a few practical examples of different abstract control modes. For the sake of argument, let's also only discuss an exoskeleton assisting one's arm - with a motor meant to assist the elbow joint.

1. Position-Control: Telling the elbow to go to a certain anble
2. Velocity-Control: Telling the elbow motor to spin at a certain speed in a certain direction
3. Acceleration-Control: Telling the elbow motor to apply a certain torque in order to achieve some additional torque on the already-moving elbow.

What I hope to demonstrate is the precise reasons for our selected control mode, and the physical requirements that then are needed for that control mode.
