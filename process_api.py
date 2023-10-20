import requests
from datetime import datetime
import json
import os

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
    

    def postViolation(self,api):
        try:
            #form of server data
            payload = {'tokenKey': 'meDTfKbvSyuGh5W1zUH5g!lCkCRekptttc0OEeY=ea1LmpaQh7taqIDyLfXUn0QBFnkneLp1-GLCaj/-srCaZIDzv/Vzevp/6Y3WMLQ=JyUgDC?kc4C0?0CSH59QxaQf=etmjeQdmM/cRzjSKf1/e-Mx=Zrq7/7EO2oe18wA/ZAXGlBt6!I3hHZHm?S?PL4WgLBaaG6NkSp1cpzvXfYPzq2y/adPbDwA-LbNbUD2SaW6Z1wMqR1nL3y47?OmkxzZ',
            'violation': self.type_violation,
            'licenseplate': self.licenseplate,
            "time":self.datetime,
            'cameraId': self.cameraId,
            "type_traffic":self.type_traffic,
            }

            #create file name from path
            filename_path_img_violation = self.path_img_violation.split("/")[2]
            filename_path_image_licenseplate = self.path_image_licenseplate("/")[2]
            file_name_video_violation = self.video_violation("/")[2]

            files=[
            ('image_violation',(filename_path_img_violation  ,open(self.path_img_violation,'rb'),'image/png')),
            (filename_path_image_licenseplate,('vuot_den_2023_09_09_09_14_05_car_248.png',open(self.path_image_licenseplate ,'rb'),'image/png')),
            ('video_violation',(file_name_video_violation,open(self.video_violation,'rb'),'application/octet-stream'))
            ]

            #post data to server
            response = requests.request("POST", self.url+api, data = payload, files = files)
        except:
            return "FAIL"
        
        # if server receive api then response messege "success" else return "FAIL"
        return json.load(response.text)["message"]
    def getCoorSetupLine(self,api,cameraId):
        try:
            payload = {
                'tokenKey': 'meDTfKbvSyuGh5W1zUH5g!lCkCRekptttc0OEeY=ea1LmpaQh7taqIDyLfXUn0QBFnkneLp1-GLCaj/-srCaZIDzv/Vzevp/6Y3WMLQ=JyUgDC?kc4C0?0CSH59QxaQf=etmjeQdmM/cRzjSKf1/e-Mx=Zrq7/7EO2oe18wA/ZAXGlBt6!I3hHZHm?S?PL4WgLBaaG6NkSp1cpzvXfYPzq2y/adPbDwA-LbNbUD2SaW6Z1wMqR1nL3y47?OmkxzZ',
                "cameraId":cameraId
            }
            files=[]
            response = requests.request("POST", self.url+api, data = payload, files = files)
            data = json.loads(response.text)["data"]
            lane_left = [data[0],data[1],data[2],data[3]]
            lane_center = [data[4],data[5],data[6],data[7]]
            lane_right = [data[8],data[9],data[10],data[11]]
            derect_left = [data[12],data[13],data[14],data[15]]
            derect_center = [data[16],data[17],data[18],data[19]]
            derect_right = [data[20],data[21],data[22],data[23]]
            traffic_light = [data[24],data[25],data[26],data[27]]

            #return lane_left, lane_center, lane_right, derect_left, derect_center, derect_right, traffic_light

        
            config = {
                "lane_left": lane_left,
                "lane_center": lane_center,
                "lane_right": lane_right,
                "derect_left": derect_left,
                "derect_center": derect_center,
                "derect_right": derect_right,
                "traffic_light": traffic_light

            }
            #convert to form json
            config_json = json.dumps(config, indent = 4)

            #path config file
            config_file_path = 'config.json'
            
            if os.path.exists(config_file_path) :
                os.remove(config_file_path)
            with open(config_file_path,'w') as config_file:
                config_file.write(config_json)
            return True
        except:
            return False
            


# if __name__ =="__main__":
    
#     url = "http://localhost:8888/Aithings-camAi"
#     dt = datetime.now()

#     # getting the timestamp
#     #print(dt)
#     # ts = datetime.timestamp(dt)
#     #payload = {'tokenKey': 'meDTfKbvSyuGh5W1zUH5g!lCkCRekptttc0OEeY=ea1LmpaQh7taqIDyLfXUn0QBFnkneLp1-GLCaj/-srCaZIDzv/Vzevp/6Y3WMLQ=JyUgDC?kc4C0?0CSH59QxaQf=etmjeQdmM/cRzjSKf1/e-Mx=Zrq7/7EO2oe18wA/ZAXGlBt6!I3hHZHm?S?PL4WgLBaaG6NkSp1cpzvXfYPzq2y/adPbDwA-LbNbUD2SaW6Z1wMqR1nL3y47?OmkxzZ',
#     violation = 'Sai lan duong'
#     licenseplate = '29A123'
#     time = dt
#     cameraId =  'CAM01'
#     type_traffic = "Xe ô tô"
#     #}

#     path_img_violation = './test_violation.png'
#     path_image_licenseplate = './test_licenseplate.png'
#     video_violation = './test_postapi.webm'
#     check_connect = callapi(violation, licenseplate, cameraId, type_traffic, url, time, path_image_licenseplate , 
#                             path_image_licenseplate, video_violation)
    
#     # print(check_connect.postViolation("/violation/addViolation"))
#     print(check_connect.getCoorSetupLine("/camera/get-line-painter","CAM04"))