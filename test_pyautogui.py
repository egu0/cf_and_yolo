import time
import win32gui
import pyautogui

title = '穿越火线'
width, height = pyautogui.size()
hwnd = win32gui.FindWindow(None, title)
x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
w = x2 - x1
h = y2 - y1

if w > 0 and h > 0:
    time.sleep(1)
    region = (x1, y1 + 30, int(w), int(h))
    print(region)
    im = pyautogui.screenshot(region=region)
    im.show()
else:
    print('invalid rect info')
