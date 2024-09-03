import threading
from paddleocr import PaddleOCR
import numpy as np
from PIL import ImageGrab

def capture_screen():
    screenshot = ImageGrab.grab()
    return np.array(screenshot)

ocr = PaddleOCR(use_angle_cls=False, lang="ch")


picture = capture_screen()
ocr.ocr(picture,cls=False)

def test():
    
    print(1)
    threading.Timer(0.5,test).start()
    return
    
test()