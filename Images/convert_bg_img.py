# -*- coding:Utf-8 -*-

import tkinter as tk
from PIL import Image, ImageOps

root = tk.Tk()

sw = 1280
sh = 800

img = Image.open('landscape_painting_by_jonathandufresne-d5pwwbq.jpg')


img = ImageOps.fit(img, (sw, sh), Image.ANTIALIAS)

img.save('bg.png')

print(sw, sh)


