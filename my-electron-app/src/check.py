import cv2
import numpy as np
from PIL import ImageGrab
import threading
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import difflib
import pygetwindow as gw
import win32gui
import win32con
import win32api
import os
import json
import logging
import time
from PyQt5.QtWidgets import QApplication
import sys

#关闭paddleocr的日志输出
logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印

# 将当前工作目录设置为脚本文件所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 初始化 OCR
ocr = PaddleOCR(use_angle_cls=False, lang="ch")

#查询是否需要运行
pause_file = 'pause.flag'

client_width = 1600
client_height = 900
# 获取窗口
window = gw.getWindowsWithTitle('崩坏：星穹铁道')

while not window:
    time.sleep(5)
    window = gw.getWindowsWithTitle('崩坏：星穹铁道')
    
def get_screen_scaling_factor(monitor_info):
    # 获取显示器的设备名
    device = monitor_info['Device']

    # 使用EnumDisplaySettings获取DPI设置
    devmode = win32api.EnumDisplaySettings(device, win32con.ENUM_CURRENT_SETTINGS)
    dpi = devmode.PelsWidth / (monitor_info['Monitor'][2] - monitor_info['Monitor'][0]) * 96
    
    scaling_factor = dpi / 96.0
    return scaling_factor


while window:
    # 获取窗口句柄
    hwnd = window[0]._hWnd
    
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    
    # 确保窗口处于正常状态
    win32gui.ShowWindow(hwnd, 9)
    # 获取窗口矩形
    rect = win32gui.GetWindowRect(hwnd)
    # 获取客户区矩形
    client_rect = win32gui.GetClientRect(hwnd)
    # 计算客户区的宽高
    width = (rect[2] - abs(rect[0]))
    height = (rect[3] - abs(rect[1]))
    
    window_center_x = int(width) // 2
    window_center_y = int(height) // 2
    
    monitor = win32api.MonitorFromPoint((window_center_x, window_center_y), win32con.MONITOR_DEFAULTTONEAREST)
    monitor_info = win32api.GetMonitorInfo(monitor)
    scaling_factor = get_screen_scaling_factor(monitor_info)
    client_width = (client_rect[2] - client_rect[0])*scaling_factor
    client_height = (client_rect[3] - client_rect[1])*scaling_factor
    print(client_width)
    print(client_height)
    if client_width == 0:
        time.sleep(1)
    else:
        break


#遗器名称栏
f = open("./xml/yiqiname.txt", "r",encoding='utf-8')
yiqiname = []
line = f.readline()
while line:
    yiqiname.append(line.strip())
    line = f.readline()


buwei = ["头部","手部","躯干","脚部","位面球","连结绳"]
citiaozhushuxing = [["生命值"],["攻击力"],["攻击力","防御力","生命值","暴击率","暴击伤害","治疗量加成","效果命中"],["攻击力","防御力","生命值","速度"],["攻击力","防御力","生命值","物理属性伤害提高","火属性伤害提高","冰属性伤害提高","雷属性伤害提高","风属性伤害提高","量子属性伤害提高","虚数属性伤害提高","凝冰属性伤害提高"],["攻击力","防御力","生命值","击破特攻","能量恢复效率"]]
citiaofushuxing = ["生命值","攻击力","防御力","速度","暴击率","暴击伤害","击破特攻","效果命中","效果抵抗"]

#检查是否有数据错误
def correct_ocr_reading(text):
    # 检查是否包含百分号
    if '%' in text:
        # 去掉所有的百分号和多余的小数点
        text = text.replace('%', '')
        text = text.replace(' ', '')
        parts = text.split('.')
        if len(parts) > 2:
            # 将所有部分合并为一个字符串并重新插入小数点
            corrected_text = ''.join(parts[:-1]) + '.' + parts[-1]
        else:
            corrected_text = text

        # 最后添加一个百分号
        return corrected_text + '%'
    else:
        # 如果没有百分号，直接返回原始文本
        return text

#整个页面的截图
def capture_screen():
    
    screen = QApplication.primaryScreen()

    if screen is None:
        raise Exception("无法获取到屏幕，请检查 QApplication 是否正确初始化")

    # 使用 grabWindow 捕捉指定窗口
    img = screen.grabWindow(hwnd).toImage()
    
    # 将 QImage 转换为 numpy 数组
    width = img.width()
    height = img.height()
    ptr = img.bits()
    ptr.setsize(img.byteCount())
    arr = np.array(ptr).reshape(height, width, 4)  # QImage 默认格式是 32-bit (RGBA)
    
    return arr

#读取处理后图片的字
def extract_text_from_image(image):

    #删除标点符号
    def remove_punctuation(text):
    # 使用 rstrip 方法去掉首尾的问号
        cleaned_text = text.strip('?')
        return cleaned_text
    
    result = ocr.ocr(image, cls=False)
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            a = remove_punctuation(line[1][0])
            line[1]=(a,line[1][1])
    image = image[:, :, ::-1]
    image = Image.fromarray(image)
    # image_rgb = image.convert('RGB')
    result = result[0]
    # boxes = [line[0] for line in result]
    # tots = [line[1][0] for line in result]
    # scores = [line[1][1] for line in result]
    
    # im_show = draw_ocr(image_rgb, boxes, tots, scores, font_path='/path/to/PaddleOCR/doc/fonts/simfang.ttf')
    # im_show = Image.fromarray(im_show)
    # im_show.save('result.jpg')
    return result

#处理文字
def parse_attributes(text):
    attributes = {}
    have_yiqi = False
    cishu = 0

    # 检查是否包含仪器名称
    def fuzzy_match(name, candidates):
        matches = difflib.get_close_matches(name, candidates, n=1, cutoff=0.6)
        return matches[0] if matches else None

    #判断是否为数字
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False
    
    # 检查是否包含仪器名称
    for line in text:
        name = fuzzy_match(line[1][0], yiqiname)
        if name:
            attributes["name"] = name
            have_yiqi = True
            break
    #确认是否正确
    if have_yiqi:
        # 查找部位信息
        for line in text:
            matched_buwei = fuzzy_match(line[1][0], buwei)
            if matched_buwei:
                attributes['buwei'] = matched_buwei
                cishu = buwei.index(matched_buwei)
                break

        # 查找主要属性信息
        for i in range(len(text)):
            line = text[i]
            for attribute in citiaozhushuxing[cishu]:
                if line[1][0] == attribute:
                    attributes['main_attributes'] = [attribute, text[i + 1][1][0]]
                    if line[1][0] == "速度" and not is_number(text[i + 1][1][0]):
                        attributes['main_attributes'] = [attribute, 4]
                    break
            if 'main_attributes' in attributes:
                break
        
        #查找副属性信息
        attributes['second_attributes'] = []
        for i in range(len(text)):
            line = text[i]
            for attribute in citiaofushuxing:
                if line[1][0] == attribute and text[i+1][1][0] != attributes['main_attributes'][1]:
                    if line[1][0] == "速度" and not is_number(text[i + 1][1][0]):
                        break
                    attributes['second_attributes'].append([attribute, correct_ocr_reading(text[i + 1][1][0])])
                    break
            
            
    return attributes

#无用，原意是处理数据，但是还没改好
def evaluate_relic_usefulness(attributes):
    if attributes.get('攻击力', 0) > 100 and attributes.get('防御力', 0) > 50:
        return True
    return False

#匹配图片
def match_template(screenshot, template_path, threshold):
    template = cv2.imread(template_path, 0)
    if client_width != 1600 or client_height != 900:
        width, height = Image.open(template_path).size
        img_new_size = (int(width*(client_width/1600)), int(height*(client_height/900)))
        template = cv2.resize(template, img_new_size, interpolation=cv2.INTER_AREA)
        cv2.imshow('test',template)
        cv2.waitKey(0)

    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    coordinates = list(zip(*loc[::-1]))  # 转换为坐标列表
    return coordinates

#截图后匹配
def is_detail_view_open(screenshot, template_paths, threshold=0.8):
    match_counts = []
    match_loc = []
    for template_path in template_paths:
        loc = match_template(screenshot, template_path, threshold)
        match_counts.append(len(loc))
        match_loc.append(loc)
    match_isopen = 0
    if match_counts[0] > 0 and match_counts[1] > 0 and match_counts[2] > 0:
        match_isopen = 1
    if match_counts[3] > 0 and match_counts[4] > 0:
        match_isopen = 2
    if match_counts[5] > 0 and match_counts[6] > 0:
        match_isopen = 3
    return match_isopen > 0, match_loc, match_isopen

#主程序
def capture_and_process(template_path, interval=0):
    if not os.path.exists(pause_file):
        threading.Timer(interval, capture_and_process, [template_path, interval]).start()
        return
    screenshot = capture_screen()
    match_isopen = 0
    is_open, coords, match_isopen = is_detail_view_open(screenshot, template_path)
    
    image=cv2.imread(template_path[0],0)
    cv2.imshow('test',image)
    cv2.imshow('test1', screenshot)
    cv2.waitKey(0)
    if not is_open:
        threading.Timer(interval, capture_and_process, [template_path, interval]).start()
        return
    
    if match_isopen == 1:
        image = Image.open(template_path[2])
        width, height = image.size
        width = int(width*(client_width/1600))
        height = int(height*(client_height/900))
        screenshot = screenshot[coords[0][0][1]:coords[2][0][1] + height * 3, coords[0][0][0]:coords[1][0][0] + coords[1][0][0] - coords[0][0][0]+10]
    elif match_isopen == 2:
        image = Image.open(template_path[4])
        width, height = image.size
        width = int(width*(client_width/1600))
        height = int(height*(client_height/900))
        image1 = Image.open(template_path[3])
        _, height1 = image1.size
        height1 = int(height1*(client_height/900))
        screenshot = screenshot[coords[4][0][1]:coords[4][0][1] + height1 * 5, coords[3][0][0]:coords[4][0][0] + width]
    elif match_isopen == 3:
        image = Image.open(template_path[6])
        width, height = image.size
        width = int(width*(client_width/1600))
        height = int(height*(client_height/900))
        screenshot = screenshot[coords[5][0][1]:coords[6][0][1], coords[6][0][0]:coords[6][0][0] + width]

    screenshot = screenshot[:, :, ::-1]
    
    
    text = extract_text_from_image(screenshot)
    attributes = parse_attributes(text)
    
    print(json.dumps(attributes, ensure_ascii=True))
    # is_useful = evaluate_relic_usefulness(attributes)
    #print("遗器是否有用:", is_useful)

    threading.Timer(interval, capture_and_process, [template_path, interval]).start()
    return



if __name__ == "__main__":
    template_path = [
        './img/main2.png',
        './img/main3.png',
        './img/main4.png',
        './img/main5.png',
        './img/main6.png',
        './img/main7.png',
        './img/main8.png'
    ]  # 模板图像的路径
    app = QApplication(sys.argv)  # 确保 QApplication 被正确初始化

    capture_thread = threading.Thread(target=capture_and_process, args=(template_path,))
    capture_thread.start()

