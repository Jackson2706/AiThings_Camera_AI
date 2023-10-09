import cv2 
from yoloDet import YoloTRT
import torch
from datetime import datetime
from law import colorDetector, midPoint, intersect
import tracker
import cv2
import os
import time

import firebase_admin
import pyrebase
from firebase_admin import credentials, firestore
from firebase_admin import storage
import json 
from Frame_capture import Frame_capture
import shutil


f = open('config.json')
data_config = json.load(f)

# Định nghĩa độ dài tối đa của hàng đợi khung hình
frame_buffer_size = 100

frame_list = []  



config = {
    "apiKey": "AIzaSyAGEyO4ZN7gdrvuqY4Vd1SMMCUVmt6UDno",
    "authDomain": "aaaa-dbb41.firebaseapp.com",
    "databaseURL": "https://aaaa-dbb41-default-rtdb.firebaseio.com/",
    "projectId": "aaaa-dbb41",
    "storageBucket": "aaaa-dbb41.appspot.com",
    "messagingSenderId": "91945409393",
    "appId": "1:91945409393:web:1b17b16a8ad8d978bb74d0",
    "measurementId": "G-V374LENXFS",
    "serviceAccount":"serviceAccountKey.json"
    }
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "storageBucket": "aaaa-dbb41.appspot.com"
    }
)
db = firestore.client()
bucket = storage.bucket()
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()#geting a document with a known ID 
try :
    result = db.collection('cameraIp').document("7OcuvIELFU7IYGnlBN4S").get()

    # if result.exists:
    #     print(result.to_dict())
    data = result.to_dict()

    Ipcamera = data["Ipcamera"]
    point_center1_begin = data["point_center1_begin"]
    point_center1_end = data["point_center1_end"]
    point_center2_begin = data["point_center2_begin"]
    point_center2_end = data["point_center2_end"]

    point_left1_begin = data["point_center1_begin"]
    point_left1_end = data["point_left1_end"]
    point_left2_begin = data["point_left2_begin"]
    point_left2_end = data["point_left2_end"]

    point_right1_begin = data["point_right1_begin"]
    point_right1_end = data["point_right1_end"]
    point_right2_begin = data["point_right2_begin"]
    point_right2_end = data["point_right2_end"]

    lane_center = point_center1_begin + point_center1_end
    lane_left = point_left1_begin + point_left1_end
    lane_right = point_right1_begin + point_right1_end

    capture = data['Ipcamera']
    current = {}
    previous = {}
    t_counter1 = []
    v_counter = []
    config = {
        "capture": capture ,
        "detect_license": True ,
        "lane_center": lane_center, 
        "lane_left": lane_left,
        "lane_right": lane_right

    }
    # Chuyển đổi dữ liệu thành định dạng JSON
    config_json = json.dumps(config, indent=4)

    # Đường dẫn đến tệp server_config.json
    config_file_path = 'server_config.json'

    # Kiểm tra nếu tệp server_config.json đã tồn tại, thì xóa nó
    if os.path.exists(config_file_path):
        os.remove(config_file_path)
        print("Đã xóa tệp server_config.json")

    # Tạo một tệp mới và ghi dữ liệu JSON vào tệp đó
    with open(config_file_path, 'w') as config_file:
        config_file.write(config_json)

    print("Đã tạo và ghi dữ liệu vào tệp server_config.json")
except:
    f= open('server_config.json')
    datajson = json.load(f)
    current = {}
    previous = {}
    t_counter1 = []

    if data_config["detect_license_plate"]:
        lane_left= []
        lane_center = data_config["lane_center_local_video"]
        lane_right = []
        
    else:
        lane_left = datajson["lane_left"]
        lane_center = datajson["lane_center"]
        lane_right = datajson["lane_right"]
    v_counter = []


serverFile = open('server_config.json')
serverConfig = json.load(serverFile)


# def updateCrossLight(img, x0, y0, boxes, track_id, time_stamp):
#     # Violation data to be stored on server

#     # Draw and store violation image to local 
#     v_counter.append(track_id)
#     # cv2.rectangle(img, (x0, y0 - 10), (x0 + 10, y0), (0, 0, 255), -1)
#     cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 255), 2)
#     saveDir = "./Violation_image"
#     file_name = "{}_{}".format(violation,time_stamp)
#     image_path = "{}/{}.jpg".format(saveDir, file_name)
#     cv2.imwrite(image_path, img)

#     # TO DO: Draw and store license plate image to local
    
#     if data_config["detect_license_plate"]:
#         licenseplate_img = detector_lp(img, boxes)
#         try :
#             saveDir_lp = "./Violation_licenseplate_img"
#             file_name_lp = "{}_{}".format(violation,time_stamp)
#             licenseplate_image_path = "{}/{}.jpg".format(saveDir_lp, file_name_lp)
#             cv2.imwrite(licenseplate_image_path, licenseplate_img)
#             image_lp_violation_blob = bucket.blob(licenseplate_image_path)
#             image_lp_violation_link = image_lp_violation_blob.generate_signed_url(expiration=36000)  # Số giây URL ảnh sẽ tồn tại
#         except:
#             image_lp_violation_link = "\t"
#     else:
#         image_lp_violation_link = "\t"

    
#     # Form violation data and push to Firebase
#     data = {
#         'image_licenseplate_violation_link': image_lp_violation_link,
#         'image_violation_link': image_violation_link,
#         'licenseplate': licenseplate,
#         'local_camera': local,
#         'time': violatedTime,
#         'type_traffic': "car",
#         'video_violation_link': "\t",
#         "violation": violation
#     }
#     db.collection('violation').add(data)
    
#     # Push violation image to Firebase
#     storage.child("Violation_image/"+videoName+".jpg").put(image_path)
# 	# TO DO: Push license plate image to Firebase
#     try:
#         storage.child("License_plate_image/"+videoName+".jpg").put(licenseplate_image_path)
#     except:
#         pass

def violation_update(frame_id, track_id, time_stamp, violation):
    violation_dict = {
        "frame_id": str(frame_id),
        "track_id": str(track_id),
        "violation": violation,
        "time_stamp": time_stamp
    }
    violation_dir = "./violation_data"
    if not os.path.exists(violation_dir):
        os.mkdir(violation_dir)

    with open(violation_dir+"/"+time_stamp+ ".json", "w") as fp:
        json.dump(violation_dict, fp)

def init_app():
    violation_video_dir = "./violation_video_data"
    violation_data_dir = "./violation_data"
    frame_data_dir = "./frame_data"
    violation_image_dir = "./violation_image"
    violation_licenseplate_img_dir = "./violation_licenseplate_img"

    if os.path.exists(violation_video_dir):
        shutil.rmtree(violation_video_dir)
        os.mkdir(violation_video_dir)
    else:
        os.mkdir(violation_video_dir)

    if os.path.exists(violation_data_dir):
        shutil.rmtree(violation_data_dir)
        os.mkdir(violation_data_dir)
    else:
        os.mkdir(violation_data_dir)

    if os.path.exists(frame_data_dir):
        shutil.rmtree(frame_data_dir)
        os.mkdir(frame_data_dir)
    else:
        os.mkdir(frame_data_dir)

    if os.path.exists(violation_image_dir):
        shutil.rmtree(violation_image_dir)
        os.mkdir(violation_image_dir)
    else:
        os.mkdir(violation_image_dir)
    
    if os.path.exists(violation_licenseplate_img_dir):
        shutil.rmtree(violation_licenseplate_img_dir)
        os.mkdir(violation_licenseplate_img_dir)
    else:
        os.mkdir(violation_licenseplate_img_dir)


if __name__ == "__main__":
    init_app()
    frame_capture_control = Frame_capture()
    # use path for libraryupdateCrossLight and engine file
    model = YoloTRT(library="yolov5/build/libmyplugins.so", engine="yolov5/build/yolov5s.engine", conf=0.5, yolo_ver="v5")
    # If we config to detect license plate, then use local video, else use stream video
    if data_config["detect_license_plate"]:
        cap = cv2.VideoCapture(data_config["local_video_path"])
    else:
        cap = cv2.VideoCapture(serverConfig["capture"])
        # If fail to read camera stream, switch to local video
        if cap.read()[0] == False:
            cap = cv2.VideoCapture(data_config["local_video_path"])
        
    torch.cuda.empty_cache()
    time_list =[]
    stt = 0
    output_filename = 'output_video.mp4'
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(5))
    frame_id = 0
    while True:
        box=[]
        classes = []
        score = []
        ret, frame = cap.read()
        if ret:
            # Thêm khung hình hiện tại vào list
            frame_list.append(frame)
                # Loại bỏ khung hình cũ nhất nếu độ dài của danh sách vượt quá giới hạn tối đa
            if len(frame_list) > frame_buffer_size:
                frame_list.pop(0)  # Loại bỏ khung hình cũ nhất
            pass
        else:
            break
        # 
        startFlowTime = time.time()
        boxes, totalInference = model.Inference(frame)
        if len(boxes):
            boxes = tracker.update(boxes, frame)
        
        frame_capture_control.push(frame_id, frame, boxes)
        if frame_id < 150:
            frame_id +=1
            continue
        if data_config["detect_license_plate"]:
            rect = data_config["cordinate_light"]
            current_color = colorDetector(frame,rect)
        else:
            current_color =colorDetector(frame)

        time_stamp = datetime.now()
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
                cv2.line(frame, previous[track_id], current[track_id], (255,0,0), 1)
                line_group0 = [lane_left, lane_center, lane_right]
                for element in line_group0:
                    if len(element):
                        start_line = element[0],element[1]
                        end_line = element[2], element[3]
                        cv2.line(frame, start_line, end_line, (220,6,0), 2)
                        if intersect(previous[track_id],current[track_id], start_line, end_line):
                            #print(intersect(previous[track_id],current[track_id], start_line, end_line))
                            if line_group0.index(element) == 1:
                                t_counter1.append(track_id)
                                if current_color != "red":
                                    print("Xảy ra sự kiện vi phạm (đèn xanh)")
                                    violation_update(frame_id, track_id, str(time_stamp)[:19], "Vượt đèn xanh")
                                elif current_color == "red":
                                    print("Xảy ra sự kiện vi phạm (đèn đỏ)")
                                    violation_update(frame_id, track_id, str(time_stamp)[:19], "Vượt đèn đỏ")
                                # updateCrossLight(frame, x0, y0, box, track_id, time_stamp)

            previous[track_id] = current[track_id]
        endFlowTime = time.time()
        totalInference = totalInference * 5
        #t_error = datetime.now() - t_error
        # print("Tốc độ của hệ thống: {} fps".format(1/(endFlowTime - startFlowTime)))
        print("Tốc độ của hệ thống: {} fps".format(1/totalInference))
        # print("Total inferrence_time: {} sec".format(totalInference))
        #time_list.append([stt,t, t_track, t_error])
        #stt = stt + 1
        frame = tracker.draw_bboxes(frame, boxes, None)
        torch.cuda.empty_cache()
        frame_id += 1
        #frame = cv2.resize(frame,(300,300))
        #cv2.imshow("Output", frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
