import time

import pygetwindow as gw
import numpy as np

from window_utils import *

class DisplayImage():
    health_bar_color = np.array((49, 203, 24)) # green
    black_color = np.array((0, 0, 0))
    toggle_tk_window = False

    @classmethod
    def start(cls, window):
        def start_window():
            time.sleep(0.5)
            tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")[0]
            time.sleep(0.2)
            set_window_opacity(tk_window._hWnd, 0.35)
            time.sleep(0.2)
            set_always_on_top(tk_window._hWnd)
            time.sleep(0.2)

            # wait for user to move window
            set_square_edges(tk_window._hWnd)
            time.sleep(0.2)

            # resize window
            img_w, img_h = image.size
            height = img_h - tk_window.height
            width = img_w - tk_window.width
            tk_window.resize(width, height)

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

            # TODO: create mask to only include the relevant portions of the image

            # image.save("ignore/__status.png")
            return image
        
        def update_image():
            # get image
            image = get_image()

            # test if image contains status hud
            img_arr = np.array(image)

            health_match = np.any(np.all(img_arr == cls.health_bar_color, axis=-1))
            black_match = np.any(np.all(img_arr == cls.black_color, axis=-1))

            if health_match and black_match:
                # get window back into view
                if cls.toggle_tk_window:
                    tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")
                    if tk_window:
                        tk_window = tk_window[0]
                        top = 595 - tk_window.top
                        left = 935 - tk_window.left
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
        label = tk.Label(root, image=tk_image)
        label.image = tk_image  # Keep a reference to avoid garbage collection
        label.pack()

        update_image()
        threading.Thread(target=start_window, daemon=True).start()

        root.mainloop()

if __name__ == "__main__":
    # debug thread
    def debug():
        time.sleep(3)
        # tk_window: gw.Win32Window = gw.getWindowsWithTitle("Display Image")[0]
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