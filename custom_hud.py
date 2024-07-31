import time

import pygetwindow as gw
import numpy as np

from window_utils import *


def remove_color_range(image: Image, color, tolerance):
    # convert image to RGBA
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # turn image into array
    img_arr = np.array(image)
    # print(img_arr[0][0])

    # get color range limits
    upper_bound = np.concatenate((np.array(color)[:] + tolerance, (255,)), axis=0)
    lower_bound = np.concatenate((np.array(color)[:] - tolerance, (0,)), axis=0)
    # print(upper_bound)
    # print(lower_bound)

    # get images within range and apply mask to orinal image
    mask_arr = np.all((img_arr >= lower_bound) & (img_arr <= upper_bound), axis=-1)
    img_arr[mask_arr] = [0, 0, 0, 0]

    # turn into PIL Image and return
    return Image.fromarray(img_arr, "RGBA")


class DisplayImage():
    health_bar_color = np.array((49, 203, 24)) # green
    poison_color = np.array((200, 3, 192))
    black_color = np.array((0, 0, 0))
    prev_img_arr = np.array((0, 0, 0))
    toggle_tk_window = False
    hide_delay_timer = time.perf_counter()
    startup = False

    mask = Image.open("ignore/status/status_mask_v3.png")

    @classmethod
    def start_window(cls, image):
        tk_window = []
        while not tk_window:
            tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")
            
        time.sleep(0.5)

        tk_window = tk_window[0]
        # set_window_opacity(tk_window._hWnd, 0.7)
        set_always_on_top(tk_window._hWnd)

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
        
        cls.toggle_tk_window = True
        def update_image():
            # get image
            image = get_image()

            if cls.startup:
                cls.start_window(image)
                cls.startup = False

            # test if image contains status hud
            new_img = Image.new("RGBA", image.size)
            new_img.paste(image, mask=cls.mask)
            image = new_img

            image = remove_color_range(image, (155, 130, 100), 35)

            if True:
                # get window back into view
                if cls.toggle_tk_window:
                    tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")
                    if tk_window:
                        tk_window = tk_window[0]
                        top = 605 - tk_window.top
                        left = 905 - tk_window.left
                        time.sleep(0.1)
                        tk_window.move(left, top)
                        cls.toggle_tk_window = False

                tk_image = ImageTk.PhotoImage(image)
                label.config(image=tk_image)
                label.image = tk_image

            else:
                # hide window
                if not cls.toggle_tk_window:
                    tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")
                    if tk_window:
                        tk_window = tk_window[0]
                        top = 1080 - tk_window.top
                        left = 1920 - tk_window.left
                        time.sleep(0.1)
                        tk_window.move(left, top)
                        cls.toggle_tk_window = True

            label.after(100, update_image)

        # Create a new Tkinter window
        root = tk.Tk()
        root.title("Display Image")
        root.attributes('-transparentcolor', root['bg'])

        image = get_image()

        tk_image = ImageTk.PhotoImage(image)
        label = tk.Label(root, image=tk_image, bg=root['bg'])
        label.image = tk_image  # Keep a reference to avoid garbage collection
        label.pack()

        root.overrideredirect(True)
        root.attributes('-alpha', 0.75)

        update_image()
        cls.startup = True

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