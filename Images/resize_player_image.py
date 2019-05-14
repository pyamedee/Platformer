# -*- coding:Utf-8 -*-

from PIL import Image, ImageOps


def bg_transparency(img, color):
    new_data = list()
    for pixel in img.getdata():
        if all((abs(a - b) < 20 for a, b in zip(color, pixel))):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(pixel)
    return new_data


image = Image.open('base_player.png').convert('RGBA')
size = [int(round(a / 3)) for a in image.size]
image.putdata(bg_transparency(image, (255, 255, 255, 255)))

image = ImageOps.fit(image, size, Image.ANTIALIAS)
image.save('player.png')



