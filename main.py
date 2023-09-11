import cv2
import threading
from FrameCapture import FrameCaptureQueue
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

frame_id = 0
previous = {}
current = {}
t_counter1 = []
v_counter = []
lane_left = []
lane_center = [453,174,605,174] 
lane_right = []
detector = Detector()
# Functions
def updateCrossLight(image, box,time_stamp):
    line_thickness = round(
        0.002 * (image.shape[0] + image.shape[1]) * 0.5) + 1

    list_pts = []
    point_radius = 4
    (x1, y1, x2, y2, cls_id, pos_id) = box
    color = (0, 255, 0)

    # 撞线的点
    check_point_x = x1
    check_point_y = int(y1 + ((y2 - y1) * 0.6))

    c1, c2 = (x1, y1), (x2, y2)
    cv2.rectangle(image, c1, c2, color, thickness=line_thickness, lineType=cv2.LINE_AA)

    font_thickness = max(line_thickness - 1, 1)
    t_size = cv2.getTextSize(cls_id, 0, fontScale=line_thickness / 3, thickness=font_thickness)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
    cv2.putText(image, '{} ID-{}'.format(cls_id, pos_id), (c1[0], c1[1] - 2), 0, line_thickness / 3,
                [225, 255, 255], thickness=font_thickness, lineType=cv2.LINE_AA)

    list_pts.append([check_point_x - point_radius, check_point_y - point_radius])
    list_pts.append([check_point_x - point_radius, check_point_y + point_radius])
    list_pts.append([check_point_x + point_radius, check_point_y + point_radius])
    list_pts.append([check_point_x + point_radius, check_point_y - point_radius])

    ndarray_pts = np.array(list_pts, np.int32)

    cv2.fillPoly(image, [ndarray_pts], color=(0, 0, 255))

    list_pts.clear()
    saveDir = "./law_img"
    file_name = "vuot_den_{}_{}_{}".format(time_stamp, cls_id, pos_id)
    cv2.imwrite("{}/{}.png".format(saveDir, file_name), image)



# Hàm để lấy frame từ video và đưa vào hàng đợi
def video_capture_thread():
    cap = cv2.VideoCapture("rtsp://admin:Admin@123@27.72.149.50:1554/profile3/media.smp") # open one video

    while not exit_signal.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        frame_queue.push([frame_id,frame])
        frame_id += 1
        print(frame_queue.count)

    cap.release()

# Hàm để hiển thị frame từ hàng đợi
def display_thread():
    while not exit_signal.is_set():
        if not frame_queue.isEnough():
            continue
        torch.cuda.empty_cache()
        t = time.time()
        frame_item = frame_queue.pop()
        print(frame.shape)
        boxes = detector.detect(frame)
        if len(boxes):
            boxes = tracker.update(boxes, frame)

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
                            print(intersect(previous[track_id],current[track_id], start_line, end_line))
                            if line_group0.index(element) == 1:
                                t_counter1.append(track_id)
                                if current_color != "red":
                                    print("Fined")
                                    updateCrossLight(frame,box=(x0, y0,x1,y1,cls, track_id), time_stamp=time_stamp)
            previous[track_id] = current[track_id]

        print(colorDetector(frame=frame))
        frame = tracker.draw_bboxes(frame,boxes, None)
        cv2.imshow("Video Stream", frame)

    # #    ` cv2.imwrite(f"law_img/{i}.jpg", frame)
    #     i += 1`
        duration = time.time() - t
        print(f"fps: {1/duration}")
        if cv2.waitKey(1) == ord('q'):
            exit_signal.set()
            break

    cv2.destroyAllWindows()
if __name__ == "__main__":
    # Tạo và khởi động các thread
    capture_thread = threading.Thread(target=video_capture_thread)
    display_thread = threading.Thread(target=display_thread)

    capture_thread.start()
    display_thread.start()
    
    capture_thread.join()
    display_thread.join()
