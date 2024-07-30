from PIL import Image, ImageTk
import tkinter as tk
import threading
import ctypes
import time
import re

import pygetwindow as gw
import win32gui
import win32con
import win32api
import win32ui

def get_citra_window(title_ending: str = None):
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

def set_window_opacity(hwnd, opacity):
    # Set window style to layered
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    
    # Set window opacity
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), int(255 * opacity), win32con.LWA_ALPHA)

def set_always_on_top(hwnd):
    # Set the window to be always on top
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def background_screenshot(hwnd: int, width: int, height: int, filename: str | None = None):
    #hwnd is window handle
    #width, height are in pixels
    #filename is name of screenshot file
    
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
   
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)    
    saveDC.SelectObject(saveBitMap)    
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)
    
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        if filename:
            img.save(filename)
        return img
    