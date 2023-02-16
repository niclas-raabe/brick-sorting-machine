# Brick Sorting machine

This repository is about our little home project building a brick sorting machine using an Lego EV3.

## Installation

To make it work with other motors than the EV3, you have to remove the motor check from the `motor.py` from the `ev3_dc` dependeny (lines 151-163 in version 0.9.10.1).

Please check the used camera and maybe you have to change the index of `cv2.VideoCapture(0)` to another index (e.g. `cv2.VideoCapture(1)`).
