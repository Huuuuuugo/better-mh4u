import ctypes
import time
import re

import pygetwindow as gw
import win32gui as w32
import pygame

pygame.init()
pygame.joystick.init()


def get_window(title_ending: str):
    """Gets the window object for the corresponding citra window.

    Atributes:
    ---------
    title_ending: str
        - Must be the exact string that appears at the end of the window title such as "Main Window" or "Secondary Window".
    """

    all_windows = gw.getAllWindows()
    regex = r"^Citra Nightly [0-9]+ \| .* \| " + title_ending
    window: gw.Win32Window = None

    for window in all_windows:
        if re.match(regex, window.title):
            return window
        
def set_square_edges(hwnd):
    # constants for window style
    GWL_STYLE = -16
    WS_BORDER = 0x00800000
    WS_OVERLAPPEDWINDOW = 0x00CF0000

    # Get the current window style
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
    
    # Modify the window style to have squared borders
    new_style = style & ~WS_OVERLAPPEDWINDOW | WS_BORDER
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)


if __name__ == "__main__":
    while True:
        # get windows info
        print("Searching for game window...")
        while True:
            primary_window = get_window("Janela Principal")
            secondary_window = get_window("Janela Secundária")
            if not (primary_window and secondary_window):
                time.sleep(0.5)
            else:
                break

        print("Game window found!")

        # remove round borders and resize secondary window
        set_square_edges(secondary_window._hWnd)

        height = 550 - secondary_window.height
        width = 725 - secondary_window.width
        top = 530 - secondary_window.top
        left = 0 - secondary_window.left

        secondary_window.resize(width, height)
        secondary_window.move(left, top)

        # gamepad info
        gamepad_id = 0
        button_id = 5

        # read input from gamepad
        print("Waiting for gamepad...")
        while not pygame.joystick.get_count():
            time.sleep(0.5)

        gamepad = pygame.joystick.Joystick(gamepad_id)

        print("Gamepad found!")

        while True:
            for event in pygame.event.get():
                # if button is pressed
                if event.type == pygame.JOYBUTTONDOWN and event.button == button_id:
                    active_window = gw.getActiveWindow()
                    if active_window._hWnd == primary_window._hWnd:
                        # primary_window.activate()
                        secondary_window.activate()

                    elif active_window._hWnd == secondary_window._hWnd:
                        # secondary_window.minimize()
                        primary_window.activate()
            
            if not w32.IsWindow(primary_window._hWnd):
                print("Game window closed!")
                break
            
            time.sleep(1/60)