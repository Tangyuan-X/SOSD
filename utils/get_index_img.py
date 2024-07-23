from PIL import Image
import os


def get_index_obj(input_img, index, output_path):
    """
    From "IndexObjxxxx.png", get the pure object mask with red color.
    :param input_img: the img read from "IndexObjxxxx.png"
    :param index: the serial number of the object
    :param output_path: the path to save the mask image
    :return: PIL.Image: the pure object mask
    """
    input_img = input_img.convert('RGBA')
    pixels = input_img.load()

    for i in range(input_img.width):
        for j in range(input_img.height):
            r, g, b, a = pixels[i, j]
            if r > 200 and g < 100 and b < 100:
                pixels[i, j] = (255, 0, 0, 255)
            else:
                pixels[i, j] = (0, 0, 0, 0)

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
                    r, g, b, a = pixels[i + di, j + dj]
                    if r == 255:
                        cnt += 1
            if cnt < 3:
                ret_pixels[i, j] = (0, 0, 0, 0)

    ret.save(output_path + os.sep + f'IndexObj{index:04d}.png')
    return ret
