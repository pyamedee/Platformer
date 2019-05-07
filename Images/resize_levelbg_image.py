# -*- coding:Utf-8 -*-

import tkinter as tk
from PIL import Image, ImageOps

root = tk.Tk()

sw = 1280
sh = 800

img = Image.open('base_level1_bg.jpg')


img = ImageOps.fit(img, (sw, sh), Image.ANTIALIAS)

img.save('level1_bg.png')

print(sw, sh)