from PIL import Image, ImageFilter
import time

import pygetwindow as gw
import numpy as np
import cv2

from window_utils import *

KEEP_CLOCK_ON_HUD = False
HIDE_HUD_DELAY = 2
HUD_UPDATE_DELAY = 100


def has_color(image: Image, color, tolerance, section: tuple | None = None):
    # convert image to RGBA
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # turn image into array
    img_arr = np.array(image)

    # get section of the image if it is set
    if section is not None:
        top, left, height, width = section
        img_arr = img_arr[top: top+height, left: left+width]

    # get color range limits
    upper_bound = np.concatenate((np.array(color)[:] + tolerance, (255,)), axis=0)
    lower_bound = np.concatenate((np.array(color)[:] - tolerance, (0,)), axis=0)

    # get pixels within bounds and return True if any is found
    return np.any(np.all((img_arr >= lower_bound) & (img_arr <= upper_bound), axis=-1), axis=None)

def remove_color_range(image: Image, color, tolerance):
    # convert image to RGBA
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # turn image into array
    img_arr = np.array(image)

    # get color range limits
    upper_bound = np.concatenate((np.array(color)[:] + tolerance, (255,)), axis=0)
    lower_bound = np.concatenate((np.array(color)[:] - tolerance, (0,)), axis=0)

    # apply morphological operation
    kernel = np.ones((3, 3), np.uint8)
    close_arr = cv2.morphologyEx(img_arr, cv2.MORPH_CLOSE, kernel)

    # get images within range and apply mask to orinal image
    mask_arr = np.all((close_arr >= lower_bound) & (close_arr <= upper_bound), axis=-1)

    img_arr[mask_arr] = [0, 0, 0, 0]

    # turn into PIL Image and return
    return Image.fromarray(img_arr, "RGBA")


class DisplayImage():
    p1_color = (180, 30, 15) # red
    p2_color = (50, 175, 175) # cyan
    p3_color = (235, 230, 10) # yellow
    p4_color = (10, 205, 10) # green

    toggle_tk_window = False

    if KEEP_CLOCK_ON_HUD:
        mask = Image.open("__status_mask_clock.png")
    else:
        mask = Image.open("__status_mask_clean.png")

    prev_health_stamina_img = np.array(mask)[10: 10+20, 100:]
    prev_health_stamina_img = prev_health_stamina_img[:, :, :3]
    
    hud_timer = 0

    @classmethod
    def check_for_player(cls, image):
        # checks if any of the player colors is found within the section that shows the weapon
        return (has_color(image, cls.p1_color, 30, (100, 10, 30, 30)) or 
                has_color(image, cls.p2_color, 30, (100, 10, 30, 30)) or
                has_color(image, cls.p3_color, 30, (100, 10, 30, 30)) or
                has_color(image, cls.p4_color, 30, (100, 10, 30, 30)))

    @classmethod
    def start(cls, window):
        def get_image():
            # take screenshot
            image = background_screenshot(window._hWnd, window.width, window.height)

            # remove top menu bar
            img_w, img_h = image.size
            left = 0
            upper = img_h//3//2
            right = img_w
            lower = img_h
            image = image.crop([left, upper, right, lower])

            # get status widget
            img_w, img_h = image.size
            left = 0
            upper = img_h//3
            right = left + img_w//2
            lower = upper + img_h//3
            image = image.crop([left, upper, right, lower])

            # image.save("ignore/__status.png")
            return image
        
        def update_image():
            # get image
            image = get_image()

            # test if image contains status hud
            if cls.check_for_player(image):
                # isolate portion of the image containing health and stamina
                health_stamina_img = np.array(image)[10: 10+20, 100:]
                
                # get difference between current and previous health_stamina_img
                difference = np.all((cls.prev_health_stamina_img != health_stamina_img), axis=-1)
                difference = np.sum(difference)

                # update previous value
                cls.prev_health_stamina_img = health_stamina_img

                # if the difference is grater than a given threshold
                if difference > 5:
                    # restart timer
                    cls.hud_timer = time.perf_counter()

                    # get window back into view
                    if cls.toggle_tk_window:
                        tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")
                        if tk_window:
                            tk_window = tk_window[0]
                            top = 605 - tk_window.top
                            left = 905 - tk_window.left
                            tk_window.move(left, top)
                            cls.toggle_tk_window = False
                
                # if there's no significant difference and HIDE_HUD_DELAY has be reached
                elif (time.perf_counter() - cls.hud_timer) >= HIDE_HUD_DELAY:
                    # hide window
                    if not cls.toggle_tk_window:
                        tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")
                        if tk_window:
                            tk_window = tk_window[0]
                            top = 1080 - tk_window.top
                            left = 1920 - tk_window.left
                            tk_window.move(left, top)
                            cls.toggle_tk_window = True
                
                # remove unnecessary portions of the image
                image = image.filter(ImageFilter.SHARPEN())
                image = remove_color_range(image, (155, 130, 100), 40)

                new_img = Image.new("RGBA", image.size)
                new_img.paste(image, mask=cls.mask)
                image = new_img

                # update tkinter window
                tk_image = ImageTk.PhotoImage(image)
                label.config(image=tk_image)
                label.image = tk_image

            # if image does not contain hud
            else:
                # hide window
                if not cls.toggle_tk_window:
                    tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")
                    if tk_window:
                        tk_window = tk_window[0]
                        top = 1080 - tk_window.top
                        left = 1920 - tk_window.left
                        tk_window.move(left, top)
                        cls.toggle_tk_window = True

            label.after(HUD_UPDATE_DELAY, update_image)

        # Create a new Tkinter window
        root = tk.Tk()
        root.title("Display Image")
        root.attributes('-transparentcolor', root['bg']) # make window properly display transparent images
        root.overrideredirect(True) # remove window decorations
        root.attributes('-alpha', 0.75) # make the window transparent
        root.wm_attributes("-topmost", 1)  # make the window stay always on top

        image = get_image()

        tk_image = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=tk_image, bg=root['bg'])
        label.image = tk_image  # Keep a reference to avoid garbage collection
        label.pack()

        update_image()

        root.mainloop()

if __name__ == "__main__":
    # debug thread
    def debug():
        time.sleep(3)
        tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")[0]
        while True:
            command = input("command: ")
            try:
                exec(command)
            except KeyboardInterrupt:
                return
            except EOFError:
                return
            except Exception as e:
                print(e)
    
    # threading.Thread(target=debug, args=(), daemon=True).start()

    # get window
    window = get_citra_window("Janela Secundária")

    # display image on a separate window
    DisplayImage.start(window)