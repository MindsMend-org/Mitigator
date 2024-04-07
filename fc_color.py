#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
# PRIVATE AND CONFIDENTIAL [Intellectual Property Of Brett Palmer mince@foldingcircles.co.uk]
# [No Copying Or Reading Or Use Permitted !]
"""
Copyright (c) 2023, Brett Palmer (Mince@foldingcircles.co.uk)

All rights reserved. No permission is granted for anyone, except the software owner, Brett Palmer, to use, copy, modify,
distribute, sublicense, or otherwise deal with the software in any manner.

Any unauthorized use, copying, or distribution of this software without the explicit written consent of the software
owner is strictly prohibited.

For permission requests, please contact the software owner, Brett Palmer, at Mince@foldingcircles.co.uk.
"""

# FoldingCircles Making The Unknown Known


__version__ = "0.0.01"
print(f'fc_color.py {__version__}')

import random

def clamp(value, min_value=0, max_value=255):
    """
    Clamp the value between the minimum and maximum values.
    """
    return max(min_value, min(value, max_value))

def rgb_color(red, green, blue):
    """
    Generate an RGB color code for terminal text.
    """
    red, green, blue = clamp(red), clamp(green), clamp(blue)
    return f"\033[38;2;{red};{green};{blue}m"

def random_color():
    """
    Generate a random RGB color code for terminal text.
    """
    return rgb_color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def reset_color():
    """
    Reset the terminal text color to default.
    """
    return "\033[0m"