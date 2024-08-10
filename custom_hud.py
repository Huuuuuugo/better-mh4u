from PIL import Image, ImageFilter, ImageTk
import tkinter as tk
import threading
import time

import pygetwindow as gw
import numpy as np
import psutil
import cv2

from window_utils import get_citra_window, background_screenshot

#TODO: end program when citra window is closed
#TODO: check for changes on the weapon info section along with health and stamina
#TODO: make it support different screen resolutions

# customizable properties
KEEP_CLOCK_ON_HUD = False   # show quest clock on HUD overlay
HIDE_HUD_DELAY = 2          # seconds untill the HUD is hidden due to inactivity
HUD_FPS = 20                # refresh rate of the HUD overlay, a higher refresh rate means a higher CPU use

# constants
HUD_FRAME_TIME = 1/HUD_FPS


def has_color(image: Image, color: tuple[int, int, int], tolerance: int, section: tuple | None = None):
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

def remove_color(image: Image, color, tolerance):
    # convert image to RGBA
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # turn image into array
    img_arr = np.array(image)

    # get color range limits
    upper_bound = np.concatenate((np.array(color)[:] + tolerance, (255,)), axis=0)
    lower_bound = np.concatenate((np.array(color)[:] - tolerance, (0,)), axis=0)

    # create mask from in bound pixels
    mask = cv2.inRange(img_arr, lower_bound, upper_bound)

    # apply morphological operations
    kernel = np.ones((3, 3), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel) # remove small noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # cover small holes
    mask = cv2.GaussianBlur(mask, (3, 3), 0) # smoth edges

    mask = cv2.bitwise_not(mask) # invert mask to remove specified color

    # apply mask to image array
    img_arr = cv2.bitwise_and(img_arr, img_arr, mask=mask)

    # convert from array to PIL Image and return
    return Image.fromarray(img_arr, "RGBA")


class DisplayImage():
    # colors that identify if the HUD is on screen
    p1_combat_color = (180, 30, 15) # red
    p2_color = (50, 175, 175) # cyan
    p3_spotted_color = (235, 230, 10) # yellow
    p4_color = (10, 205, 10) # green
    frenzy_color = (175, 80, 210) #purple

    # attributes related to the HUD overlay window
    toggle_tk_window = False
    tk_window: gw.Win32Window | None = None

    # selecting the base mask to include the quest clock or not
    if KEEP_CLOCK_ON_HUD:
        mask = Image.open("__status_mask_clock.png")
    else:
        mask = Image.open("__status_mask_clean.png")

    # declaration of other needed attributes
    prev_health_stamina_img = np.array(mask)[10: 10+20, 100:]
    prev_health_stamina_img = prev_health_stamina_img[:, :, :3]
    hud_timer = 0

    @classmethod
    def check_for_player(cls, image):
        # checks if any of the player colors is found within the section that shows the weapon
        return (has_color(image, cls.p1_combat_color, 30, (100, 10, 30, 30)) or 
                has_color(image, cls.p2_color, 30, (100, 10, 30, 30)) or
                has_color(image, cls.p3_spotted_color, 30, (100, 10, 30, 30)) or
                has_color(image, cls.p4_color, 30, (100, 10, 30, 30)) or
                has_color(image, cls.frenzy_color, 30, (100, 10, 30, 30)))

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
            # start frame timer
            frame_timer_start = time.perf_counter()

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
                if difference > 0:
                    # restart timer
                    cls.hud_timer = time.perf_counter()

                    # get window back into view
                    if cls.toggle_tk_window:
                        if cls.tk_window is not None:
                            top = 605 - cls.tk_window.top
                            left = 905 - cls.tk_window.left
                            cls.tk_window.move(left, top)
                            cls.toggle_tk_window = False
                
                # if there's no significant difference and HIDE_HUD_DELAY has be reached
                elif (time.perf_counter() - cls.hud_timer) >= HIDE_HUD_DELAY:
                    # hide window
                    if not cls.toggle_tk_window:
                        if cls.tk_window is not None:
                            top = 1080 - cls.tk_window.top
                            left = 1920 - cls.tk_window.left
                            cls.tk_window.move(left, top)
                            cls.toggle_tk_window = True
                
                # remove unnecessary portions of the image
                image = image.filter(ImageFilter.SHARPEN())
                image = remove_color(image, (138, 112, 81), 70)

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
                    if cls.tk_window is not None:
                        top = 1080 - cls.tk_window.top
                        left = 1920 - cls.tk_window.left
                        cls.tk_window.move(left, top)
                        cls.toggle_tk_window = True

            # wait untill frame timer reaches the frame time of the HUD refresh rate
            frame_timer_end = time.perf_counter() - frame_timer_start
            # print(f"\rprocessing time: {round(frame_timer_end, 5):.5f}", end="")
            while frame_timer_end < HUD_FRAME_TIME:
                time.sleep(0.0001)
                frame_timer_end = time.perf_counter() - frame_timer_start
            # print(f" | final time: {round(frame_timer_end, 5):.5f}", end="")

            label.after(1, update_image)

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

        def get_tk_window():
            time.sleep(0.5)
            windows_list = []
            while not windows_list:
                windows_list = gw.getWindowsWithTitle("Display Image")

            cls.tk_window = windows_list[0]
        threading.Thread(target=get_tk_window, args=(), daemon=True).start()

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

    def get_cpu_usage(interval=1):
        process = psutil.Process()
        time.sleep(3)
        usage_list = []
        max_usage_list_len = 10
        cpu_high = 0
        avg_usage = 0
        avg_high = 0

        while True:
            # Get CPU usage percentage of the process over the specified interval
            cpu_usage = process.cpu_percent(interval=interval)
            if cpu_usage > cpu_high:
                cpu_high = cpu_usage

            usage_list.append(cpu_usage)
            if len(usage_list) > max_usage_list_len:
                usage_list.pop(0)

            avg_usage = (sum(usage_list)/len(usage_list))
            if avg_usage > avg_high and len(usage_list) == max_usage_list_len:
                avg_high = avg_usage
            
            # Print the CPU usage
            print(f"CPU usage: {cpu_usage:.2f}% | average usage: {avg_usage:.2f}% | CPU high: {cpu_high:.2f}% | average high: {avg_high:.2f}%    \r", end='')

    # threading.Thread(target=debug, args=(), daemon=True).start()              # start debug thread
    # threading.Thread(target=get_cpu_usage, args=(0.5,), daemon=True).start()  # start cpu usage thread

    # get window
    window = get_citra_window("Janela Secundária")

    # display image on a separate window
    DisplayImage.start(window)