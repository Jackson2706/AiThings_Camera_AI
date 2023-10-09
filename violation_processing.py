from glob import glob
import os
import json
from time import sleep
import cv2
import numpy as np
from time import time
from datetime import datetime
import firebase_admin
import pyrebase
from firebase_admin import credentials, firestore
from firebase_admin import storage
import pytesseract
area_threshold = 500

'''
    Functions: detector_lp, crop license plate image from vehicle image
    @param img: np.array
    @box: bounding box of vehicle
'''
def detector_lp(img,box):
    x1,y1,x2,y2, label = box
    # if label != "car":
    #     return None
    img_crop = img[int(y1):int(y2),int(x1):int(x2)]
    value_thres = 130
    h, w , c = img_crop.shape
    img_crop = img_crop[int(h/2):h , 0:w]
    if (len(img_crop) == 0):
        return None
    license_plate = None
    #convert to gray image
    gray_img = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
    #cv2.write("Gray.jpg", gray_img)
    #Remove noise
    gray_img= cv2.bilateralFilter(gray_img, 11, 17, 17)
    #cv2.imshow("remove_noise_gray.jpg", gray_img)
        #canny edge detection
    canny_img = cv2.Canny(gray_img,64 ,200)
    #cv2.imshow("Canny_Image.jpg", canny_img)
    #find countor base on edge
    contours, new  = cv2.findContours(canny_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    img3 = img_crop.copy()
    contours=sorted(contours, key = cv2.contourArea, reverse = True)[0]
    img4 = img_crop.copy()
    contourImage = cv2.resize(img4, [640, 480])
    # Initialize license Plate contour and x,y coordinates
    contour_with_license_plate = None
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
                img6 = img_crop.copy()
                license_plate = img6[y:y + h , x:x + w ]
    return license_plate

def readLicenseplateNumber(img):
   h,w,c = img.shape
   img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   img_blur = cv2.blur(img_gray,(3,3))
   ret, binary_img = cv2.threshold(img_blur, 235, 255, cv2.THRESH_BINARY)

   if (h/w) > 2.1:
      text = pytesseract.image_to_string(binary_img, lang = 'eng', config = '--psm 8 -c page_separator=""')
   else:
      img_license1 = binary_img[0:h//2, :]
      img_license2 = binary_img[h//2 : h, :]
      text1 = pytesseract.image_to_string(img_license1, lang = 'eng', config = '--psm 8 -c page_separator=""')
      text2 = pytesseract.image_to_string(img_license2, lang = 'eng', config = '--psm 8 -c page_separator=""')
      text = text1 + "-" + text2
      text = [e for e in text if e.isalpha() or e.isnumeric() or e == "-" or e == "."]
      text = "".join(text)
   return text

def drawObject(image_path, box, transform_data, resize_width = 1280, resize_height = 960):
    image = cv2.imread(image_path)
    if not box:
        image = cv2.resize(image, (resize_width,resize_height))
        return image
    line_thickness = round(0.002 * (image.shape[0]+image.shape[1])*0.5)+1
    point_radius = 4
    list_pts = []
    [x1,y1,x2,y2, label] = box
    label = transform_data[label]
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    color = (0, 255, 0)
    check_point_x = x1
    check_point_y = int(y1 + ((y2 - y1) * 0.6))

    c1, c2 = (x1, y1), (x2, y2)
    cv2.rectangle(image, c1, c2, color, thickness=line_thickness, lineType=cv2.LINE_AA)

    font_thickness = max(line_thickness - 1, 1)
    t_size = cv2.getTextSize(label, 0, fontScale=line_thickness / 3, thickness=font_thickness)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
    cv2.putText(image, '{}'.format(label), (c1[0], c1[1] - 2), 0, line_thickness / 3,
                [225, 255, 255], thickness=font_thickness, lineType=cv2.LINE_AA)

    list_pts.append([check_point_x - point_radius, check_point_y - point_radius])
    list_pts.append([check_point_x - point_radius, check_point_y + point_radius])
    list_pts.append([check_point_x + point_radius, check_point_y + point_radius])
    list_pts.append([check_point_x + point_radius, check_point_y - point_radius])

    ndarray_pts = np.array(list_pts, np.int32)

    cv2.fillPoly(image, [ndarray_pts], color=(0, 0, 255))
    image = cv2.resize(image, (resize_width,resize_height))
    return image

def frame_to_video(frame_list,output_filename, frame_rate = 30):
    height, width, layers = frame_list[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, frame_rate, (width, height))
    for frame in frame_list:
        out.write(frame)
    out.release()


if __name__ == "__main__":
    f = open('config.json')
    data_config = json.load(f)


    '''
        Set up config to send data
    '''
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
#Read data

    violation_video_dir = "./violation_video_data"
    violation_data_dir = "./violation_data"
    frame_data_dir = "./frame_data"
    violation_image_dir = "./violation_image"
    violation_licenseplate_img_dir = "./violation_licenseplate_img"
    local = "Camera Jackson AGX" # ADD CAM ID OR UNIQUE CAM NAME IN THE FUTURE
    
    sleep(30)
    begin = None
    while True:
        file_list = glob(violation_data_dir+"/*.json")
        if (not file_list):
            if data_config["detect_license_plate"]:
                if begin is None:
                    begin = time()
                now = time()
                if (now - begin > 180):
                    break
            continue
        num_file = len(glob(frame_data_dir+"/*.json"))
        sleep(data_config["time_sleep"])
        for file in file_list:
            data = json.load(open(file))
            frame_id = int(data["frame_id"])
            track_id = data["track_id"]
            violation = data["violation"] 
            time_stamp = data["time_stamp"]
            '''
                Create videos
            '''
            violation_frame_list = [f"{frame_data_dir}/{i}.jpg" for i in range(frame_id-120, min(frame_id+120, num_file))]
            violation_data_list = [f"{frame_data_dir}/{i}.json" for i in range(frame_id-120, min(frame_id+120, num_file))]
            draw_frame_list = []
            for frame_data_path, bbox_data_path in zip(violation_frame_list,violation_data_list):
                bbox_data = json.load(open(bbox_data_path))
                try:
                    target_bbox = bbox_data[track_id]
                except:
                    target_bbox = []
                draw_frame = drawObject(frame_data_path, target_bbox, data_config["label"], data_config["resize_frame"][0], data_config["resize_frame"][1])
                draw_frame_list.append(draw_frame)
            violation_video_path = f"{violation_video_dir}/{time_stamp}_{violation}.mp4"
            frame_to_video(draw_frame_list, violation_video_path , 20)
            print("Tạo video vi phạm: {}/{}_{}.mp4".format(violation_video_dir,time_stamp, violation))

            '''
                Capture image at time which violation appears
            '''
            violation_image = draw_frame_list[120]
            violation_frame_path = f"{violation_image_dir}/{violation}_{time_stamp}.jpg"
            cv2.imwrite(violation_frame_path, violation_image)

            '''
                Capture image licenseplate of the fined vehicle
            '''
            violatedTime = datetime.strptime(time_stamp, '%Y-%m-%d %H:%M:%S')
            # violatedTime = time_stamp
            licenseplate = ""
            videoName = (str(violatedTime)[0:19] + "_" + violation +"_"+ licenseplate +"_"+ local).replace(":","_").replace(" ","_").replace("-","_")
            [x1,y1,x2,y2,label] = json.load(open(violation_data_list[120]))[track_id]
            if data_config["detect_license_plate"]:
                try:
                    for i in range(121):
                        try:
                            license_plate_image = detector_lp(draw_frame_list[i], json.load(open(violation_data_list[i]))[track_id])
                            if license_plate_image != None:
                                break
                        except:
                            continue
                    if license_plate_image != None:
                        licenseplate_image_path = f"{violation_licenseplate_img_dir}/{violation}_{time_stamp}.jpg"
                        cv2.imwrite(licenseplate_image_path, license_plate_image)
                        videoName = (str(violatedTime)[0:19] + "_" + violation +"_"+ licenseplate +"_"+ local).replace(":","_").replace(" ","_").replace("-","_")
                        storage.child("ImageLicenseplateViolation/"+videoName+".jpg").put(licenseplate_image_path)
                        bucket_path="ImageLicenseplateViolation"+"%2F"+videoName+".jpg"
                        image_lp_violation_link = 'https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media'.format(config["storageBucket"], bucket_path)
                        print("Bắn ảnh biển số xe: {}".format(image_lp_violation_link))
                        try:
                            licenseplate = readLicenseplateNumber(license_plate_image)
                        except:
                            licenseplate = ""
                    else:
                        image_lp_violation_link = "\t"
                except:
                    image_lp_violation_link = "\t"
            else:
                image_lp_violation_link = "\t"
                licenseplate = ""
            '''
                Send data to server
            '''
            # Push violation image
            storage.child("ImageViolation/"+videoName+".jpg").put(violation_frame_path)
            bucket_path="ImageViolation"+"%2F"+videoName+".jpg"
            image_violation_link = 'https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media'.format(config["storageBucket"], bucket_path)
            print("Bắn ảnh vi phạm: {}".format(image_violation_link))

            # Push violation video
            storage.child("VideoViolation/"+videoName+".mp4").put(violation_video_path)
            bucket_path="VideoViolation"+"%2F"+videoName+".mp4"
            video_violation_link = 'https://firebasestorage.googleapis.com/v0/b/{}/o/{}?alt=media'.format(config["storageBucket"], bucket_path)
            print("Bắn video vi phạm: {}".format(video_violation_link))
        
            # Form data and push to server
            data = {
                'image_licenseplate_violation_link': image_lp_violation_link,
                'image_violation_link': image_violation_link,
                'licenseplate': "38A-66876",
                'local_camera': local,
                'time': violatedTime,
                'type_traffic': data_config["label"][str(label)],
                'video_violation_link': video_violation_link,
                "violation": violation
            }
            db.collection('violation').add(data)
            print("Bắn dữ liệu vi phạm: {}".format(data))
            
            os.remove(file)




