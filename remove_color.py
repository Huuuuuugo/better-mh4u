from PIL import Image, ImageFilter
import numpy as np
import time
import cv2


def remove_color_range(image: Image, color, tolerance):
    # TODO: try using cv2's morph closing
    # convert image to RGBA
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # turn image into array
    img_arr = np.array(image)

    # get color range limits
    upper_bound = np.concatenate((np.array(color)[:] + tolerance, (255,)), axis=0)
    lower_bound = np.concatenate((np.array(color)[:] - tolerance, (0,)), axis=0)

    # apply morphological operation
    kernel = np.ones((5, 5), np.uint8)
    close_arr = cv2.morphologyEx(img_arr, cv2.MORPH_ERODE, kernel)

    # get images within range and apply mask to orinal image
    mask_arr = np.all((close_arr >= lower_bound) & (close_arr <= upper_bound), axis=-1)

    img_arr[mask_arr] = [0, 0, 0, 0]

    # turn into PIL Image and return
    return Image.fromarray(img_arr, "RGBA")

import os
path = "ignore/big_change"
mask = Image.open("__status_mask_clean.png")
for file in os.listdir(path):
    # load image
    image = Image.open(f"{path}/{file}")

    timer = time.perf_counter()
    image = image.filter(ImageFilter.SHARPEN())
    print(f"{path}/{file}")
    image = remove_color_range(image, (160, 130, 88), 60) # (140, 158, 123)


    # base mask
    new_img = Image.new("RGBA", image.size)
    new_img.paste(image, mask=mask)
    image = new_img
    
    # apply remove color mask
    print(time.perf_counter() - timer)
    
    image.save(f"{path}/__image.png")
    input()