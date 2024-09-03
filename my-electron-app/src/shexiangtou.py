import cv2

capture = cv2.VideoCapture(0)

# image=cv2.imread('src/img/main.png',0)



# image=image[130:1080,1200:1920]

# cv2.imshow("image",image)
# cv2.imwrite('src/img/main1.png',image)
# cv2.waitKey()








while True:
    ret, frame=capture.read()
    # _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    key=cv2.waitKey(1)
    if key!=-1:
        break
capture.release()