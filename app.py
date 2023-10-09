import cv2 
from yoloDet import YoloTRT
import torch
from datetime import datetime
from law import colorDetector, midPoint, intersect
import tracker
import cv2
import os
import firebase_admin
import pyrebase
from firebase_admin import credentials
from firebase_admin import firestore
# import datetime as firebaseDatetime
from firebase_admin import storage
import json 
import numpy
import time

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
storage = firebase.storage()
area_threshold = 500
#Read data

#geting a document with a known ID 
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
    lane_left = datajson["lane_left"]
    lane_center = datajson["lane_center"]
    lane_right = datajson["lane_right"]
    v_counter = []

def detector_lp(img,box):
    #for i in range(len(box)):
        #confirm = 0
        #box[i].append(confirm)
    #print("box", box)
    for i in range(len(box)):
        t = time.time()
        #print("box", box[i])
        img2 = img.copy()
        img_crop = img2[int(box[i][1]):int(box[i][3]),int(box[i][0]):int(box[i][2])]

        value_thres = 130
        #img_crop = cv2.imread(img_path)
    
        h, w , c = img_crop.shape
    
        img_crop = img_crop[int(h/2):h , 0:w]
        img_crop0 = img_crop.copy()
        #print("img_crop0", img_crop0, type(img_crop0))
        if(numpy.size(img_crop0)):
            #cv2.imshow("img_crop",img_crop0)

            #convert to gray image
            gray_img = cv2.cvtColor(img_crop0, cv2.COLOR_BGR2GRAY)

            #Remove noise
            gray_img= cv2.bilateralFilter(gray_img, 11, 17, 17)
    
                #canny edge detection
            canny_img = cv2.Canny(gray_img,64 ,200)
            #find countor base on edge

            contours, new  = cv2.findContours(canny_img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            img3 = img_crop.copy()
            #
            #cv2.drawContours(img3, contours, -1, (0,255,0), 2)
            #cv2.imshow("contours_img",img3)

            #cv2.imwrite("contours247.jpg",img3)
            #cv2.waitKey()

            contours=sorted(contours, key = cv2.contourArea, reverse = True)[:1]
        
            img4 = img_crop.copy()
            #cv2.drawContours(img4,contours, -1,(0,255,0),3)
            contourImage = cv2.resize(img4, [640, 480])
            #cv2.imwrite("sort247.jpg",img4)
            # Initialize license Plate contour and x,y coordinates
            contour_with_license_plate = None
            license_plate = None
            x = None
            y = None
            w = None
            h = None
            # Find the contour with 4 potential corners and creat ROI around it
            for contour in contours:
                    if cv2.contourArea(contour) < area_threshold:
                        text = ""
                    
                    else:
                # Find Perimeter of contour and it should be a closed contour
                        perimeter = cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, 0.05 * perimeter, True)
                        if len(approx) == 4: #see whether it is a Rect
                            contour_with_license_plate = approx
                            x, y, w, h = cv2.boundingRect(contour)
                    #cv2.circle(img= img_crop,center=(x,y),radius=1,color=(0,0,255),thickness=3,lineType=cv2.LINE_AA,shift=0)
                            #print("tlwh", [x,y,w,h])
                            img6 = img_crop.copy()
                            license_plate = img6[y:y + h , x:x + w ]
                
    return license_plate

def updateCrossLight(img, x0, y0, boxes, track_id, time_stamp):

    # Violation data to be stored on server
    licenseplate = "38A3326" # REPLACE THIS WITH CORRECT PLATE IN THE FUTURE
    local = "Camera Jackson AGX" # ADD CAM ID OR UNIQUE CAM NAME IN THE FUTURE
    violatedTime = datetime.now()
    violationFieldName = 'Sai làn đường'
    violation = 'Sai_lan_duong'
    videoName = (str(violatedTime)[0:19] + "_" + violation +"_"+ licenseplate +"_"+ local).replace(":","_").replace(" ","_").replace("-","_")

    # Draw and store violation image to local 
    v_counter.append(track_id)
    # cv2.rectangle(img, (x0, y0 - 10), (x0 + 10, y0), (0, 0, 255), -1)
    cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 255), 2)
    saveDir = "./Violation_image"
    file_name = "{}_{}".format(violation,time_stamp)
    image_path = "{}/{}.jpg".format(saveDir, file_name)
    cv2.imwrite(image_path, img)

    # TO DO: Draw and store license plate image to local
    '''
    if data_config["detect_license_plate"]:
        licenseplate_img = detector_lp(img, boxes)
        saveDir = "./Violation_licenseplate_image"
        file_name = "{}_{}".format(violation,time_stamp)
        licenseplate_image_path = "{}/{}.jpg".format(saveDir, file_name)
        cv2.imwrite(licenseplate_image_path, licenseplate_img)
    '''
    # Form violation data and push to Firebase
    # data = {
	#     'licenseplate':licenseplate,
	#     'local_camera':local,
	#     'time':violatedTime, 
	#     'video_name':videoName, 
    #     'image_name': videoName,
    #     'license_plate_image_name': videoName,
	#     'violation':violationFieldName
    #         }
    image_violation_blob = bucket.blob(image_path)
    image_violation_link = image_violation_blob.generate_signed_url(expiration=3600)  # Số giây URL ảnh sẽ tồn tại
    print(image_violation_link)
    data = {
        'image_licenseplate_violation_link': "\t",
        'image_violation_link': image_violation_link,
        'licenseplate': licenseplate,
        'local_camera': local,
        'time': violatedTime,
        'type_traffic': "car",
        'video_violation_link': "\t",
        "violation": violation
    }
    db.collection('violation').add(data)
    
    # Push violation image to Firebase
    storage.child("Violation_image/"+videoName+".jpg").put(image_path)
	# TO DO: Push license plate image to Firebase
    #storage.child("License_plate_image/"+videoName+".jpg").put(licenseplate_image_path)

# use path for libraryupdateCrossLight and engine file
model = YoloTRT(library="yolov5/build/libmyplugins.so", engine="yolov5/build/yolov5s.engine", conf=0.5, yolo_ver="v5")
# cap = cv2.VideoCapture("/home/ctarg_lab_1/Desktop/video_output.mp4")
if data_config["detect_license_plate"]:
    cap = cv2.VideoCapture(data_config["local_video_path"])
else:
    cap = cv2.VideoCapture("rtsp://admin:Admin@123@27.72.149.50:1554/profile3/media.smp") # open one video
torch.cuda.empty_cache()
time_list =[]
stt = 0
output_filename = 'output_video.mp4'
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(5))
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))
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
    boxes, totalInference = model.Inference(frame)
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
            cv2.line(frame, previous[track_id], current[track_id], (255,0,0), 1)
            line_group0 = [lane_left, lane_center, lane_right]
            for element in line_group0:
                if len(element):
                    start_line = element[0],element[1]
                    end_line = element[2], element[3]
                    cv2.line(frame, start_line, end_line, (0,255,0), 2)
                    if intersect(previous[track_id],current[track_id], start_line, end_line):
                        print(intersect(previous[track_id],current[track_id], start_line, end_line))
                        if line_group0.index(element) == 1:
                            t_counter1.append(track_id)
                            """
                            if current_color != "red":
                                print("Fined")
                                updateCrossLight(frame, x0, y0, track_id, time_stamp)
                            """
                            print("Fined")
                            updateCrossLight(frame, x0, y0, boxes, track_id, time_stamp)

                            for f in frame_list:
                                print("write")
                                out.write(f)

                            out.release()
                            # firebaseVideoPath = "Video/" + videoName +'.mp4'
                            # storage.child(firebaseVideoPath).put("output_video.mp4","mp4")
        previous[track_id] = current[track_id]
    #t_error = datetime.now() - t_error
    print("Total FPS: {} sec".format(1/totalInference))
    print("Total inferrence_time: {} sec".format(totalInference))
    #time_list.append([stt,t, t_track, t_error])
    #stt = stt + 1
    frame = tracker.draw_bboxes(frame, boxes, None)
    torch.cuda.empty_cache()
    # cv2.imshow("Output", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
       break