import os

from PIL import Image
import get_shadow_soft_mask_img as gss
import get_index_img as gi
import get_shadow_hard_mask_img as ghs


def handle_result(output_root_path, output_sub_path):
    """
    Handle the rendered images. Generate origin img, shadow-free img, mask img, etc.
    :param output_root_path: the path to the rendered images
    :param output_sub_path: the path to one data sample
    :return: None
    """
    if not os.path.exists(output_sub_path):
        os.makedirs(output_sub_path)

    png_num = len([lists for lists in os.listdir(output_root_path) if
                  os.path.isfile(os.path.join(output_root_path, lists)) and
                   os.path.join(output_root_path, lists).endswith('.png')])
                  
    origin_img = Image.open(output_root_path + os.sep + 'Image0000.png')
    shadow_free_img = Image.open(output_root_path + os.sep + 'Image0001.png')
    origin_img.save(output_sub_path + os.sep + 'origin.png')
    shadow_free_img.save(output_sub_path + os.sep + 'shadow_free.png')
    origin_img.close()
    shadow_free_img.close()

    index = 3
    count = 0
    frame_length = png_num//2-1
    print("###########frame length:", frame_length)
    while index <= frame_length:
        id_shadow_img = Image.open(output_root_path + os.sep + f'IndexObj{index:04d}.png')
        id_img = gi.get_index_obj(id_shadow_img.copy(), count, output_sub_path)

        pure_shadow = Image.open(output_root_path + os.sep + f'Image{index + 1:04d}.png')
        shadow_hard_mask = ghs.get_shadow_hard_mask(pure_shadow.copy(), count, output_sub_path)

        shadow_soft_mask = gss.get_shadow_soft_mask_img(pure_shadow.copy(), count, output_sub_path)

        self_shadow = Image.open(output_root_path + os.sep + f'Image{index + 2:04d}.png')
        self_shadow_hard_mask = ghs.get_shadow_hard_mask(self_shadow.copy(), count, output_sub_path, "self_shadow_mask")
        self_shadow_soft_mask = gss.get_shadow_soft_mask_img(self_shadow.copy(), count, output_sub_path, "self_shadow_soft_mask")

        index += 3
        count += 1

        shadow_hard_mask.close()
        id_shadow_img.close()
        id_img.close()
        pure_shadow.close()
        shadow_soft_mask.close()
        self_shadow.close()
        self_shadow_hard_mask.close()
        self_shadow_soft_mask.close()

    lists = os.listdir(output_root_path)
    for i in lists:
        if i.endswith('.png'):
            os.remove(os.path.join(output_root_path, i))
    
    