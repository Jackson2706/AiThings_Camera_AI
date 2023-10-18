import requests
from datetime import datetime
import json


class callapi:
    def __init__(self,type_violation,licenseplate,cameraId,type_traffic, url, datetime, path_img_violation, path_image_licenseplate,video_violation) -> None:
        self.url = url
        self.path_img_violation = path_img_violation
        self.path_image_licenseplate = path_image_licenseplate
        self.video_violation = video_violation
        self.datetime = datetime
        self.type_violation = type_violation
        self.licenseplate = licenseplate
        self.cameraId = cameraId
        self.type_traffic = type_traffic
    

    def request(self):
        payload = {'tokenKey': 'meDTfKbvSyuGh5W1zUH5g!lCkCRekptttc0OEeY=ea1LmpaQh7taqIDyLfXUn0QBFnkneLp1-GLCaj/-srCaZIDzv/Vzevp/6Y3WMLQ=JyUgDC?kc4C0?0CSH59QxaQf=etmjeQdmM/cRzjSKf1/e-Mx=Zrq7/7EO2oe18wA/ZAXGlBt6!I3hHZHm?S?PL4WgLBaaG6NkSp1cpzvXfYPzq2y/adPbDwA-LbNbUD2SaW6Z1wMqR1nL3y47?OmkxzZ',
        'violation': self.type_violation,
        'licenseplate': self.licenseplate,
        "time":self.datetime,
        'cameraId': self.cameraId,
        "type_traffic":self.type_traffic,
        }

        files=[
        ('image_violation',('video.jpg',open(self.path_img_violation,'rb'),'image/jpeg')),
        ('image_licenseplate_violation',('vuot_den_2023_09_09_09_14_05_car_248.png',open(self.path_image_licenseplate ,'rb'),'image/png')),
        ('video_violation',('a.mp4',open(self.video_violation,'rb'),'application/octet-stream'))
        ]

        response = requests.request("POST", self.url, data = payload, files = files)
        return response
    def post_value(self):
        response = self.request()
        data = json.load(response.text)["data"]
        
        lane_left = [data[0],data[1],data[2],data[3]]
        lane_center = [data[4],data[5],data[6],data[7]]
        lane_right = [data[8],data[9],data[10],data[11]]

        derect_left = [data[12],data[13],data[14],data[15]]
        derect_center = [data[16],data[17],data[18],data[19]]
        derect_right = [data[20],data[21],data[22],data[23]]

        traffic_light = [data[24],data[25],data[26],data[27]]

        return lane_left, lane_center, lane_right, derect_left, derect_center, derect_right, traffic_light

    def check_connect(self):
        response = self.request()
        return json.load(response.text)["message"]

# if __name__ =="__main__":

#     url = "http://white-dev.aithings.vn:18888/Aithings-camAi/violation/addViolation"
#     dt = datetime.now()
#     violation = 'Sai lan duong'
#     licenseplate = '29A123'
#     time = dt
#     cameraId =  'CAM01'
#     type_traffic = "Xe ô tô"
#     

#     path_img_violation = 'C:/Users/xuanp/Downloads/video.jpg'
#     path_image_licenseplate = 'C:/Users/xuanp/Downloads/vuot_den_2023_09_09_09_14_05_car_248.png'
#     video_violation = 'C:/Users/xuanp/Downloads/a.mp4'

#     check_connect = callapi(violation, licenseplate, cameraId, type_traffic, url, time, path_image_licenseplate , 
#                             path_image_licenseplate, video_violation).check_connect()

#     lane_left, lane_center, lane_right, derect_left, derect_center, derect_right, traffic_light = callapi(violation, licenseplate, cameraId, 
#                                                                                                           type_traffic, url, time, path_image_licenseplate , 
#                                                                                                           path_image_licenseplate, video_violation).post_value()

    
