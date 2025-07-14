import pyrealsense2 as rs
import numpy as np
import cv2
import time
import socket
import json

IP = '127.0.0.1'
PORT = 5700
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

finger_position = [0, 0]
currently_touching = False
movement_mode = False
touch_timestamp = time.time()

MIN_SIZE = 50
MAX_SIZE = 2500

tap_timer = 0.1
topmost = (0,0)

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

def capture_background_image():
    start_frames = pipeline.wait_for_frames()
    start_color_frame = start_frames.get_color_frame()
    start_color_np = np.asanyarray(start_color_frame.get_data())
    return cv2.cvtColor(start_color_np, cv2.COLOR_BGR2GRAY)

try:
    #starting background
    background_frames = []
    start_time = time.time()
    while time.time() - start_time <= 6:
        background_frames.append(capture_background_image())
    starting_background = np.mean(background_frames, axis=0).astype(np.uint8)

    while True:
        active_contour = ""
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.flip(color_image, 1)
        image_height, image_width = color_image.shape[:2]
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        start_difference = cv2.absdiff(gray_image, starting_background)
        void, threshold = cv2.threshold(start_difference, 90, 255, cv2.THRESH_BINARY)
        contours, meep = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        fingertip_contour = None
        max_area = 0

        for contour in contours:
            contour_area = cv2.contourArea(contour)
            if MIN_SIZE < contour_area < MAX_SIZE and contour_area > max_area:
                fingertip_contour = contour
                max_area = contour_area

        if fingertip_contour is not None:
            topmost = tuple(fingertip_contour[fingertip_contour[:, :, 1].argmin()][0])
            cv2.circle(color_image, topmost, 10, (0, 0, 255), -1)
            finger_position = topmost
            if currently_touching == False:
                touch_timestamp = time.time()
            currently_touching = True
            #Falls die Zeit länger war als der Threshold, dann beginnt es, movements zu machen.
            if time.time() - touch_timestamp > tap_timer or movement_mode:
                movement_mode = True
                x, y = topmost
                print(x)
                print(y)
                print(image_height)
                message = json.dumps({"movement": {"x": int(x), "y": int(image_height)-int(y)}})
                sock.sendto(message.encode(), (IP, PORT))
        else:
            if currently_touching == True:
                #Es wurde getoucht und losgelassen
                #War es kurz genug, isses ein Tap gewesen.
                if time.time() - touch_timestamp <= tap_timer:
                    x, y = topmost
                    message = json.dumps({"tap": 1})
                    sock.sendto(message.encode(), (IP, PORT))
                    time.sleep(0.1)
                    message = json.dumps({"tap": 0})
                    sock.sendto(message.encode(), (IP, PORT))
            currently_touching = False
            movement_mode = False

        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.drawContours(color_image, fingertip_contour, -1, (0, 255, 0), 3)
        cv2.imshow('RealSense', color_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
