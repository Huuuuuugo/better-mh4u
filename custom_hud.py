import time

import pygetwindow as gw

from window_utils import *

def display_image(window):
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

        # move window
        top = 595 - tk_window.top
        left = 935 - tk_window.left
        tk_window.move(left, top)

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
        image = get_image()
        tk_image = ImageTk.PhotoImage(image)
        label.config(image=tk_image)
        label.image = tk_image

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
    display_image(window)