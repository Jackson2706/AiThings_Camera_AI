import cv2
import threading
from FrameCapture import FrameCaptureQueue
from finedFrameCapture import finedFrameCaptureQueue
import numpy as np
import time 
import torch.cuda
from datetime import datetime
from law import colorDetector, midPoint, intersect
import tracker
from detector import Detector

# Biến hoặc cơ chế đồng bộ hóa chung để thông báo cho các luồng rằng nên kết thúc
exit_signal = threading.Event()

# Hàng đợi để lưu trữ các frame từ video
frame_queue = FrameCaptureQueue()
fined_frame_queue = finedFrameCaptureQueue()
violation_list = []
previous = {}
current = {}
t_counter1 = []
v_counter = []
lane_left = []
lane_center = [453,174,605,174] 
lane_right = []
detector = Detector()
# Functions
def violation_capture_thread():
    print(f"Luong {threading.current_thread().name}")
    while not exit_signal.is_set():
        # print(len(violation_list))
        if not violation_list:
            continue
        time.sleep(5)
        information = violation_list.pop(0)
        fined_frame_queue.generateVideo(information)

# Hàm để lấy frame từ video và đưa vào hàng đợi
def video_capture_thread():
    print(f"Luong {threading.current_thread().name}")
    cap = cv2.VideoCapture("rtsp://admin:Admin@123@27.72.149.50:1554/profile3/media.smp") # open one video
    frame_id = 0
    while not exit_signal.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        frame_queue.push([frame_id,frame])
        frame_id += 1
        # print(frame_queue.count)

    cap.release()

# Hàm để hiển thị frame từ hàng đợi
def display_thread():
    print(f"Luong {threading.current_thread().name}")
    while not exit_signal.is_set():
        if not frame_queue.isEnough():
            continue
        torch.cuda.empty_cache()
        t = time.time()
        frame_item = frame_queue.pop()
        frame = frame_item[1]
        # print(frame.shape)
        boxes = detector.detect(frame)
        if len(boxes):
            boxes = tracker.update(boxes, frame)
        fined_frame_queue.push([frame_item[0], frame_item[1], boxes])

        if fined_frame_queue.isFull():
            fined_frame_queue.pop()

        current_color = colorDetector(frame)
        time_stamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
        for i in range(len(boxes)):
            box = boxes[i][:4]
            track_id = boxes[i][-1]
            cls = boxes[i][4]
            x0 = int(box[0])
            y0 = int(box[1])
            x1 = int(box[2])
            y1 = int(box[3])
            current[track_id]  = midPoint(x0,y0,x1,y1)

            if track_id in previous:
                cv2.line(frame, previous[track_id], current[track_id], (0,255,0), 1)
                line_group0 = [lane_left, lane_center, lane_right]
                for element in line_group0:
                    if len(element):
                        # print(element)
                        start_line = element[0],element[1]
                        end_line = element[2], element[3]
                        cv2.line(frame, start_line, end_line, (0,0,255), 2)
                        if intersect(previous[track_id],current[track_id], start_line, end_line):
                            # print(intersect(previous[track_id],current[track_id], start_line, end_line))
                            if line_group0.index(element) == 1:
                                t_counter1.append(track_id)
                                if current_color != "red":
                                    print("Fined")
                                    information = [frame_item[0], track_id, "cross_light", time_stamp]
                                    violation_list.append(information)
                                    # updateCrossLight(frame,box=(x0, y0,x1,y1,cls, track_id), time_stamp=time_stamp)
            previous[track_id] = current[track_id]

        # print(colorDetector(frame=frame))
        # frame = tracker.draw_bboxes(frame,boxes, None)
        cv2.imshow("Video Stream", frame)

    # #    ` cv2.imwrite(f"law_img/{i}.jpg", frame)
    #     i += 1`
        duration = time.time() - t
        # print(f"fps: {1/duration}")
        if cv2.waitKey(1) == ord('q'):
            exit_signal.set()
            break

    cv2.destroyAllWindows()
if __name__ == "__main__":
    # Tạo và khởi động các thread
    capture_thread = threading.Thread(target=video_capture_thread,name="Thread 1")
    display_thread = threading.Thread(target=display_thread, name="Thread 2")
    violation_thread = threading.Thread(target=violation_capture_thread, name="Thread 3")
    capture_thread.start()
    display_thread.start()
    violation_thread.start()

    capture_thread.join()
    display_thread.join()
    violation_thread.join()