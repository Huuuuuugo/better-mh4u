import pygetwindow as gw
import win32gui
import win32con
import win32api
import ctypes

def set_square_edges(window_title):
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No window found with title: {window_title}")
        return
    
    for window in windows:
        # Get the handle of the window
        hwnd = window._hWnd
    
    # constants for window style
    GWL_STYLE = -16
    WS_BORDER = 0x00800000
    WS_OVERLAPPEDWINDOW = 0x00CF0000

    # Get the current window style
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
    
    # Modify the window style to have squared borders
    new_style = style & ~WS_OVERLAPPEDWINDOW | WS_BORDER
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)

def set_window_opacity(window_title, opacity):
    # Find windows with titles containing the partial title
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No window found with title: {window_title}")
        return

    for window in windows:
        hwnd = window._hWnd
        
        # Set window style to layered
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        
        # Set window opacity
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), int(255 * opacity), win32con.LWA_ALPHA)

def set_always_on_top(window_title):
    # Find windows with titles containing the partial title
    windows = gw.getWindowsWithTitle(window_title)
    if not windows:
        print(f"No window found with title: {window_title}")
        return

    for window in windows:
        # Get the handle of the window
        hwnd = window._hWnd
        
        # Set the window to be always on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


# Example usage: Pin a window with a specific title
window_title = "Hoje.txt - Bloco de notas"  # Replace with the title of your target window
set_always_on_top(window_title)

# Example usage: Set a window with a specific title to 50% opacity
set_window_opacity(window_title, 0.5)  # Opacity value between 0.0 (completely transparent) and 1.0 (completely opaque)

set_square_edges(window_title)