import time

import pygetwindow as gw
import win32gui as w32
import numpy as np
import colorama
import pygame

from window_utils import get_citra_window, set_square_edges, get_screen_dimensions

# customizable properties
BUTTON_ID = 5       # integer id of the button that brings the secondary window into view (5 is the home button on switch pro controller)
CUSTOM_SCALE = 1    # custom scale factor for the dimensions of the secondary window

# constants
SCREEN_SCALE = get_screen_dimensions()[1]/1080 # scale factor to keep the secondary screen on the same proportions between all screen resolutions (default resolution is 1080p)

colorama.init()
Fore = colorama.Fore
Style = colorama.Style

pygame.init()
pygame.joystick.init()

if __name__ == "__main__":
    timeout = 10
    print(Fore.YELLOW + "Waiting for Citra window to be openned (timeout in 10 seconds)..." + Style.RESET_ALL)
    while not get_citra_window():
        time.sleep(0.5)
        timeout -= 0.5
        if timeout <= 0:
            exit(Fore.RED + "Citra window not found!" + Style.RESET_ALL)

    print(Fore.GREEN + "Citra window found!" + Style.RESET_ALL)

    while get_citra_window():
        # get windows info
        print(Fore.YELLOW + "Searching for game window..." + Style.RESET_ALL)
        while True:
            primary_window = get_citra_window("Janela Principal")
            secondary_window = get_citra_window("Janela Secundária")
            if not (primary_window and secondary_window):
                time.sleep(0.5)
            else:
                break

            if not get_citra_window():
                exit(Fore.RED + "Citra window closed!" + Style.RESET_ALL)

        print(Fore.GREEN + "Game window found!" + Style.RESET_ALL)

        # remove round borders and resize secondary window
        set_square_edges(secondary_window._hWnd)

        height = int((550 * SCREEN_SCALE) * CUSTOM_SCALE) - secondary_window.height
        width = int((725 * SCREEN_SCALE) * CUSTOM_SCALE) - secondary_window.width
        secondary_window.resize(width, height)

        top = (get_screen_dimensions()[1] - secondary_window.height) - secondary_window.top
        left = 0 - secondary_window.left
        secondary_window.move(left, top)

        # read input from gamepad
        print(Fore.YELLOW + "Waiting for gamepad..." + Style.RESET_ALL)
        gamepad = None
        while not pygame.joystick.get_count():
            if not w32.IsWindow(primary_window._hWnd):
                break
            time.sleep(0.5)
        else:
            gamepad = pygame.joystick.Joystick(0)

        if gamepad is None:
            print(Fore.RED + "Game window closed!" + Style.RESET_ALL)
            print(Fore.YELLOW + "Restarting..." + Style.RESET_ALL)
            continue

        print(Fore.GREEN + "Gamepad found!" + Style.RESET_ALL)

        print(Fore.GREEN + "Playing!" + Style.RESET_ALL)
        while True:
            for event in pygame.event.get():
                # if a button has been pressed
                if event.type == pygame.JOYBUTTONDOWN:
                    # if home button is pressed
                    if event.button == BUTTON_ID:
                        active_window = gw.getActiveWindow()
                        if active_window._hWnd == primary_window._hWnd:
                            # primary_window.activate()
                            secondary_window.activate()

                        elif active_window._hWnd == secondary_window._hWnd:
                            # secondary_window.minimize()
                            primary_window.activate()
            
            if not w32.IsWindow(primary_window._hWnd):
                print(Fore.RED + "Game window closed!" + Style.RESET_ALL)
                print(Fore.YELLOW + "Restarting..." + Style.RESET_ALL)
                break

            if not pygame.joystick.get_count():
                print(Fore.RED + "Gamepad disconnected!" + Style.RESET_ALL)
                print(Fore.YELLOW + "Restarting..." + Style.RESET_ALL)
                break
            
            time.sleep(1/60)
    exit(Fore.RED + "Citra window closed!" + Style.RESET_ALL)