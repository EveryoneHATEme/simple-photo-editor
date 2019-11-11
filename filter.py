from PIL import Image


def some_filter(image: Image.Image):
    res = image.copy()
    pixels = res.load()
    for i in range(res.width):
        for j in range(res.height):
            r, g, b = pixels[i, j]
            pixels[i, j] = r // 2, g * 2, b * 2
    return res


def another_filter(image: Image.Image):
    res = image.copy()
    pixels = res.load()
    for i in range(res.width):
        for j in range(res.height):
            r, g, b = pixels[i, j]
            pixels[i, j] = r // 2, g // 2, b * 2
    return res
