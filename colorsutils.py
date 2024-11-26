# colorutils library for https://github.com/hlnmplus/colorpreview

import json

fl = open('names.json')
db = json.loads(fl.read())
fl.close()

del fl

def hex2rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def hexbycolorname(name):
    if name in db.keys():
        rgb = db[name]
        hex = '%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])
        return hex
    else:
        return False
    
def colornamebyhex(hex):
    for i in db.keys():
        rgb = hex2rgb(hex)
        rgb = (rgb[0], rgb[1], rgb[2])
        if db[i] == rgb:
            return i
    return False
    
def nearestcolor(hex):
    rgb = hex2rgb(hex)
    print(rgb)
    result = ['', 10000]
    for i in db.keys():
        diff = 0
        diff += abs(rgb[0] - db[i][0])
        diff += abs(rgb[1] - db[i][1])
        diff += abs(rgb[2] - db[i][2])
        if diff < result[1]:
            result[0] = i
            result[1] = diff
    return result

def rgb2cmyk(r, g, b):
    if (r, g, b) == (0, 0, 0):
        return 0, 0, 0, 100

    c = 1 - r / 255
    m = 1 - g / 255
    y = 1 - b / 255

    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    return c * 100, m * 100, y * 100, k * 100