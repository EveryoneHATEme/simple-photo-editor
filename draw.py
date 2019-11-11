from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


class TransposeHandler:
    @staticmethod
    def resize(image: Image.Image, width, height):
        return image.resize((width, height))

    @staticmethod
    def rotate(image: Image.Image, rotation: int):
        return image.rotate(rotation)

    @staticmethod
    def horizontal_flip(image: Image.Image):
        return image.transpose(Image.FLIP_LEFT_RIGHT)

    @staticmethod
    def vertical_flip(image: Image.Image):
        return image.transpose(Image.FLIP_TOP_BOTTOM)

    @staticmethod
    def crop(image: Image.Image, side: str, percents: float):
        width, height = image.size
        if side == 'left':
            width_percent = width / 100
            return image.crop((width_percent * percents, 0, width, height))
        if side == 'right':
            width_percent = width / 100
            return image.crop((0, 0, width - width_percent * percents, height))
        if side == 'top':
            height_percent = height / 100
            return image.crop((0, height_percent * percents, width, height))
        if side == 'bottom':
            height_percent = height / 100
            return image.crop((0, 0, width, height - height_percent * percents))


class AdjustmentHandler:
    @staticmethod
    def brightness(image: Image.Image, factor):
        factor /= 50
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def contrast(image: Image.Image, factor):
        factor /= 50
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def sharpness(image: Image.Image, factor):
        factor /= 50
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)


class FilterHandler:
    @staticmethod
    def black_white(image: Image.Image):
        res = image.copy()
        pixels = res.load()
        for i in range(res.width):
            for j in range(res.height):
                color = sum(pixels[i, j]) // 3
                pixels[i, j] = (color, color, color)
        return res

    @staticmethod
    def sepia(image: Image.Image, k=30):
        res = image.copy()
        pixels = res.load()
        for i in range(image.width):
            for j in range(image.height):
                color = sum(pixels[i, j]) // 3
                pixels[i, j] = (color + k ** 2, color + k, color)
        return res

    @staticmethod
    def negative(image: Image.Image):
        pixels = 255 - np.array(image)
        return Image.fromarray(pixels)


class BlurHandler:
    @staticmethod
    def horizontal_blur(image: Image.Image):
        res = image.copy()
        width, height = res.size
        blur(res, (0, 0, width, height // 4))
        blur(res, (0, 0, width, 3 * height // 8))
        blur(res, (0, 0, width, 5 * height // 16))
        blur(res, (0, height - height // 4, width, height))
        blur(res, (0, height - 3 * height // 8, width, height))
        blur(res, (0, height - 5 * height // 16, width, height))
        return res

    @staticmethod
    def vertical_blur(image: Image.Image):
        res = image.copy()
        width, height = res.size
        blur(res, (0, 0, width // 4, height))
        blur(res, (0, 0, 3 * width // 8, height))
        blur(res, (0, 0, 5 * width // 16, height))
        blur(res, (width - width // 4, 0, width, height))
        blur(res, (width - 3 * width // 8, 0, width, height))
        blur(res, (width - 5 * width // 16, 0, width, height))
        return res


def blur(image: Image.Image, box):
    piece = image.crop(box)
    piece = piece.filter(ImageFilter.GaussianBlur(1))
    image.paste(piece, box)


def default_image(image: Image.Image):
    return image
