import pyrebase
import glob
import os
import time
config ={
    "apiKey": "AIzaSyASLSs9V-4r0eY129zPY1awkd2SQKxr2IA",
    "authDomain": "aithingscameraai.firebaseapp.com",
    "projectId": "aithingscameraai",
    "storageBucket": "aithingscameraai.appspot.com",
    "messagingSenderId": "421530780939",
    "appId": "1:421530780939:web:31357eebfed91e68d3ce0e",
    "databaseURL": ""
}



# path_on_cloud = "images/test.png"
# path_local = "law_img/vuot_den_2023_08_24-16_44_09_motorcycle_32.jpg"
# storage.child(path_on_cloud).put(path_local)

while True:
    if glob.glob("law_img/*.png"):
        firebase = pyrebase.initialize_app(config=config)
        storage = firebase.storage()
        for image_path in glob.glob("law_img/*.png"):
            path_local = image_path
            path_on_cloud = image_path
            storage.child(path_on_cloud).put(path_local)
            print(f"Transmit: {image_path}")
            time.sleep(2)
            os.remove(image_path)
    else:
        continue
