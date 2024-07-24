import pyautogui
import ctypes
import time
import re

import pygetwindow as gw
import win32gui as w32
import numpy as np
import pynput
import pygame
import cv2

keyboard = pynput.keyboard.Controller()
key = pynput.keyboard.Key

pygame.init()
pygame.joystick.init()


def get_window(title_ending: str = None):
    """Gets the window object for the corresponding citra window.

    Atributes:
    ---------
    title_ending: str
        - Must be the exact string that appears at the end of the window title such as "Main Window" or "Secondary Window".
    """

    if title_ending is None:
        regex = r"^Citra Nightly [0-9]+.*"
    else:
        regex = r"^Citra Nightly [0-9]+ \| .* \| " + title_ending

    all_windows = gw.getAllWindows()
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

def quick_press(key, wait):
    keyboard.press(key)
    time.sleep(wait)
    keyboard.release(key)

def screen_shot():
    # get screen dimensions
    screen_w, screen_h = pyautogui.size()

    # get screenshot dimensions
    x = int(screen_w // 1.8640776699029127)
    y = int(screen_h // 4.6956521739130440)
    w = int(screen_w // 2.5098039215686274)
    h = int(screen_h // 2.2500000000000000)

    # get screen shot, convert it to an np.array and grayscale it
    screen_shot = cv2.cvtColor(np.array(pyautogui.screenshot(region=[x, y, w, h])), cv2.COLOR_RGB2GRAY)

    # get binary image
    return cv2.threshold(screen_shot, 70, 255, cv2.THRESH_BINARY)[1]

def get_items(image):
    # get item square dimensions and offset to center
    img_h, img_w = image.shape[:2]

    item_h = img_h // 6
    item_w = img_w // 8

    # find line and column of the last occupied item square
    last_item = [0, 0]
    for line in range(6):
        curr_h = line * item_h
        for column in range(8):
            curr_w = column * item_w
            center = image[
                curr_h : curr_h + item_h,
                curr_w : curr_w + item_w,
            ]
            if np.any(center > 127):
                last_item = [line + 1, column + 1]

    # go through every item square until the last occupied one
    wait = 1/25
    quick_press(key.f1, wait)
    quick_press(key.f1, wait)
    quick_press(key.up, wait)
    quick_press("+", wait)
    time.sleep(wait)
    for line in range(last_item[0]):
        for column in range(8):
            quick_press("+", wait)
            quick_press(key.right, wait)
            if line == last_item[0] - 1 and column == last_item[1] - 1:
                break
        if line == last_item[0] - 1:
            break
        quick_press(key.down, wait)


if __name__ == "__main__":
    timeout = 10
    print("Waiting for Citra window to be openned (timeout in 10 seconds)...")
    while not get_window():
        time.sleep(0.5)
        timeout -= 0.5
        if timeout <= 0:
            exit("Citra window not found!")

    print("Citra window found!")

    while get_window():
        # get windows info
        print("Searching for game window...")
        while True:
            primary_window = get_window("Janela Principal")
            secondary_window = get_window("Janela Secundária")
            if not (primary_window and secondary_window):
                time.sleep(0.5)
            else:
                break

            if not get_window():
                exit("Citra window closed!")

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
        gamepad = None
        while not pygame.joystick.get_count():
            if not w32.IsWindow(primary_window._hWnd):
                break
            time.sleep(0.5)
        else:
            gamepad = pygame.joystick.Joystick(gamepad_id)

        if gamepad is None:
            print("Game window closed!")
            continue

        print("Gamepad found!")

        print("Playing!")
        while True:
            for event in pygame.event.get():
                # if a button has been pressed
                if event.type == pygame.JOYBUTTONDOWN:
                    # if home button is pressed
                    if event.button == button_id:
                        active_window = gw.getActiveWindow()
                        if active_window._hWnd == primary_window._hWnd:
                            # primary_window.activate()
                            secondary_window.activate()

                        elif active_window._hWnd == secondary_window._hWnd:
                            # secondary_window.minimize()
                            primary_window.activate()
                    
                    # if screenshot button is pressed
                    if event.button == 15:
                        image = screen_shot()
                        get_items(image)

                    # if up, down, left, right, A or B is pressed
                    if event.button == 11:
                        keyboard.press(key.up)

                    if event.button == 12:
                        keyboard.press(key.down)

                    if event.button == 13:
                        keyboard.press(key.left)

                    if event.button == 14:
                        keyboard.press(key.right)
                    
                    if event.button == 0:
                        keyboard.press("+")
                    
                    if event.button == 1:
                        keyboard.press(key.f1)
                    
                # if a button has been released
                elif event.type == pygame.JOYBUTTONUP:
                    # if up, down, left, right, A or B is released
                    if event.button == 11:
                        keyboard.release(key.up)

                    if event.button == 12:
                        keyboard.release(key.down)

                    if event.button == 13:
                        keyboard.release(key.left)

                    if event.button == 14:
                        keyboard.release(key.right)
                    
                    if event.button == 0:
                        keyboard.release("+")

                    if event.button == 1:
                        keyboard.release(key.f1)

            
            if not w32.IsWindow(primary_window._hWnd):
                print("Game window closed!")
                break
            
            time.sleep(1/60)
    exit("Citra window closed!")