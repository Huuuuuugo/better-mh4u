import pygetwindow as gw
import pywinauto
from PIL import ImageGrab, ImageTk
import tkinter as tk

def capture_window_area(window_title, x, y, width, height):
    # Find the target window
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No window found with title: {window_title}")
        return None

    window = windows[0]
    hwnd = window._hWnd
    
    # Get the window's position
    app = pywinauto.Application().connect(handle=hwnd)
    rect = window.topleft + window.size
    
    # Calculate the area to capture
    capture_rect = (rect[0] + x, rect[1] + y, rect[0] + x + width, rect[1] + y + height)
    
    # Capture the area
    screenshot = ImageGrab.grab(capture_rect)
    return screenshot

def update_image(window_title, x, y, width, height, label):
    # Capture the new area
    image = capture_window_area(window_title, x, y, width, height)
    if image:
        # Convert the image to a format Tkinter can use
        tk_image = ImageTk.PhotoImage(image)
        label.config(image=tk_image)
        label.image = tk_image
    
    # Schedule the next update
    label.after(100, update_image, window_title, x, y, width, height, label)

def display_cropped_area(window_title, x, y, width, height):
    # Create a new Tkinter window
    root = tk.Tk()
    root.title("Cropped Window")

    # Initial capture
    initial_image = capture_window_area(window_title, x, y, width, height)
    if initial_image:
        tk_image = ImageTk.PhotoImage(initial_image)
        label = tk.Label(root, image=tk_image)
        label.image = tk_image  # Keep a reference to avoid garbage collection
        label.pack()
        
        # Start the update loop
        update_image(window_title, x, y, width, height, label)

    # Run the Tkinter main loop
    root.mainloop()

# Example usage: Capture a 200x200 area from the top-left corner of a window titled "Untitled - Notepad"
window_title = "Hoje.txt - Bloco de notas"  # Replace with the title of your target window
x, y, width, height = 0, 0, 200, 200

display_cropped_area(window_title, x, y, width, height)
