import pygame as p


def colorSurface(surface, color):
    color = p.Color(color)
    red = color[0]
    green = color[1]
    blue = color[2]
    arr = p.surfarray.pixels3d(surface)
    arr[:, :, 0] = red
    arr[:, :, 1] = green
    arr[:, :, 2] = blue


def isValidColorString(colorStr):
    return any(colorStr == item[0] for item in p.colordict.THECOLORS.items())
