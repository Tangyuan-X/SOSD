from PIL import Image
import colorsys
import os


# 导出阴影
def get_shadow_hard_mask(input_img, index, output_path, filename="shadow_mask"):
    """
    From pure shadow image, get its hard mask with lime color.
    :param input_img: the img read from pure shadow
    :param index: the serial number of the object
    :param output_path: the path to save the mask image
    :param filename: the output file will be named as "{filename}{xxxx}.png"
    :return: PIL.Image: the shadow hard mask
    """
    input_img = input_img.convert('RGBA')
    pixels = input_img.load()

    for i in range(input_img.width):
        for j in range(input_img.height):
            r, g, b, a = pixels[i, j]
            if a <= 6 or (r > 2 and g > 2 and b > 2):
                pixels[i, j] = (0, 0, 0, 0)
            else:
                pixels[i, j] = (0, 255, 0, 255)

    ret = input_img.copy()
    ret = ret.convert('RGBA')
    ret_pixels = ret.load()
    delta = [0, 1, -1]
    w = ret.width
    h = ret.height
    # remove noise
    for i in range(w):
        for j in range(h):
            cnt = 0
            for di in delta:
                for dj in delta:
                    if j + dj < 0 or j + dj >= h or i + di < 0 or i + di >= w:
                        continue
                    r, g, b, a = pixels[i+di, j+dj]
                    if g == 255:
                        cnt += 1
            if cnt < 3:
                ret_pixels[i, j] = (0, 0, 0, 0)

    ret.save(output_path + os.sep + filename + f'{index:04d}.png')
    return ret
