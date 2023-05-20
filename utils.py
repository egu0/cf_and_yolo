import random
import time

import pyautogui
import win32gui  # pip install pywin32
from PIL import ImageDraw, Image


def draw_frame_and_save(rectangle_info_list: list, screen_shot: Image.Image, target_point: tuple):
    """
    绘制边框、保存图片到 images/ 下
    :param rectangle_info_list: 边框信息
    :param screen_shot: 图像
    :param target_point:  目标点
    :return:
    """
    if rectangle_info_list is None or screen_shot is None or target_point is None:
        print('标注并保存图片失败，rect_list={},\nim={},\ntarget_point={}'.format(
            rectangle_info_list, screen_shot, target_point))
        return
    draw = ImageDraw.Draw(screen_shot)
    for coordination in rectangle_info_list:
        draw.rectangle(coordination, outline='red', width=2)
    draw.point(target_point, fill='blue')
    # screen_shot.show()
    name = time.time() + random.randint(0, 100)
    screen_shot.save("images/" + str(name) + ".png")


def get_window_location_info(title: str):
    """
    获取窗口坐标
    :param title: 窗口标题
    :return:
    """
    try:
        hwnd = win32gui.FindWindow(None, title)
        x1, y1, x2, y2 = win32gui.GetWindowRect(hwnd)
        # y1+30 偏移，去除顶部边框
        return x1, y1 + 30, x2 - x1, y2 - y1
    except Exception as e:
        print('获取窗口坐标时出错，', e)


def get_window_screen_shot(win_title):
    """
    窗口截图
    :param win_title: 窗口标题
    :return:
    """
    try:
        loc_info = get_window_location_info(win_title)
        if loc_info is None:
            return None
        x, y, w, h = loc_info
        if w > 0 and h > 0:
            return pyautogui.screenshot(region=loc_info)
        else:
            return None
    except Exception as e:
        print('截屏时出错，', e)


# region testcases

def enum_windows_callback(handler, window_titles):
    window_title = win32gui.GetWindowText(handler)
    if window_title != '':
        window_titles.append(window_title)


# 列出所有标题包含 keyword 的窗口
def list_chrome_window_info(keyword: str):
    window_titles = []
    win32gui.EnumWindows(enum_windows_callback, window_titles)
    for win_title in window_titles:
        if keyword in win_title:
            print(win_title, ' >> ', get_window_location_info(win_title))

# list_chrome_window_info("穿越火线")

# img = get_window_screen_shot('穿越火线 - Bing images - Google Chrome')
# if img:
#     img.show()

# endregion
