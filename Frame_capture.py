import os
import cv2
import json
import shutil 

class Frame_capture:
    def __init__(self, data_dir = "./frame_data"):
        self.data_dir = data_dir
        if os.path.exists(self.data_dir):
            shutil.rmtree(data_dir)
            os.mkdir(self.data_dir)
        else:
            os.mkdir(self.data_dir)

        self.max_length = 5000
        self.frame_path_list = []
        self.json_path_list = []

    def _bbox2dict(self, boxes):
        boxes_dict = {}
        for box in boxes:
            x1,y1,x2,y2,label,track_id = box
            boxes_dict[str(track_id)] = (str(x1),str(y1),str(x2),str(y2), str(label))
        return boxes_dict
    
    def _release_data(self):
        for i in range(100):
            frame_path = self.frame_path_list.pop(0)
            jsondata_path = self.json_path_list.pop(0)
            os.remove(frame_path)
            os.remove(jsondata_path) 
        
    def push(self,frame_id, frame, boxes):
        if (len(self.frame_path_list) > self.max_length):
            self._release_data()
        frame_id = str(frame_id)
        cv2.imwrite(self.data_dir+"/"+frame_id+".jpg", frame)
        datajson = self._bbox2dict(boxes)
        with open(self.data_dir+"/"+frame_id+".json", "w") as fp:
            json.dump(datajson, fp)
        self.frame_path_list.append(self.data_dir+"/"+frame_id+".jpg")
        self.json_path_list.append(self.data_dir+"/"+frame_id+".json")

    