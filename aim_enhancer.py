import math
import threading
import time
from pynput.mouse import Listener

import pydirectinput as direct
from ultralytics import YOLO

from utils import get_window_location_info, get_window_screen_shot, draw_frame_and_save

# ------------------- 使用鼠标中键进行自瞄控制 ----------------------

# 是否需要瞄准。全局变量，线程间共享
aiming = False


class Mouse_listener_thread(threading.Thread):
    def __init__(self):
        self.last_click_ts = None
        super().__init__()

    def run(self):
        def on_click(x, y, button, pressed):
            global aiming
            if button == button.middle:
                if pressed:  # 只判断点击事件
                    if self.last_click_ts is None:
                        print('打开')
                        aiming = True
                        self.last_click_ts = time.time_ns()
                    else:
                        now = time.time_ns()
                        ms_offset = (now - self.last_click_ts) / 1000_000
                        print(ms_offset)
                        if ms_offset > 400:
                            aiming = False
                            print('关闭')
                            self.last_click_ts = None

        # 创建鼠标监听器
        with Listener(on_click=on_click) as listener:
            listener.join()


thread = Mouse_listener_thread()
thread.start()
print('开启了鼠标监听线程...，请按下鼠标中键开启或关闭瞄准辅助')

# ------------------- 瞄准逻辑 ----------------------

direct.PAUSE = False
model = YOLO('yolov8n.pt')

window_title = '穿越火线'
fixed_window_location_info = get_window_location_info(window_title)
if fixed_window_location_info is None:
    print('窗口')
    exit(555)
left, top, weight, height = fixed_window_location_info
if weight == 0 and height == 0:
    exit(555)
mp = (weight / 2, height / 2)

print('start....')
while True:
    time.sleep(0.05)
    while aiming:
        image = get_window_screen_shot(window_title)
        print("拍摄了图片...")
        result = model(source=image, device=0, classes=0)
        boxes = result[0].boxes
        point = None
        rect_info_list = []
        distance = 999999
        for box in boxes:
            cls = box.cls.cpu().numpy().tolist()[0]
            conf = boxes.conf.cpu().numpy().tolist()[0]
            if int(cls) == 0 and conf >= 0.6:
                points = box.xyxy.cpu().numpy().tolist()[0]
                x1, y1, x2, y2 = points
                # temp_point 表示识别出来的矩形框中点的相对坐标
                temp_point = (x1 + (x2 - x1) / 2, y1 + (y2 - y1) / 4)
                # 距离准心的距离
                temp_distance = math.sqrt(math.pow((temp_point[0] - mp[0]), 2) + math.pow(temp_point[1] - mp[1], 2))
                rect_info_list.append(points)
                if temp_distance < distance:
                    point = temp_point
                    distance = temp_distance
                    print("更新坐标：{:>5},{:>5}，距离：{}".format(point[0], point[1], distance))
                    break
        if point and distance <= 200:
            print("射击...")
            xOffset = int(point[0] - mp[0])
            yOffset = int(point[1] - mp[1])
            # 移动准心
            direct.moveRel(xOffset=xOffset, yOffset=yOffset, relative=True)
            # 绘制画面
            # draw_frame_and_save(rect_info_list, image, point)
        else:
            print("未识别到结果...")
