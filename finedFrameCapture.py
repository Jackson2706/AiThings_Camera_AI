import cv2
import numpy as np


def drawObject(image, box):
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
    return image

def frame_to_video(frame_list,output_filename, frame_rate = 30):
    height, width, layers = frame_list[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_filename, fourcc, frame_rate, (width, height))
    for frame in frame_list:
        out.write(frame)
    out.release()



class finedFrameCaptureQueue:
    def __init__(self):
        '''
        @param frame_capture: a list contains [frame_id, frame, bounding_box]
        in which:
            bounding_box includes [x,y,h,w,cls_id, track_id]
        '''
        self.frame_capture = []
        self.count = -1
    
    def push(self, frame):
        self.frame_capture.append(frame)
        self.count = self.count + 1

    def pop(self, frame):
        a = self.frame_capture.pop(0)
        self.count = self.count - 1

    def isFull(self):
        return self.count > 2000
    '''
    @param information: a list contains [frame_id, track_id, violation, time]
    '''
    def generateVideo(self, information):
        frame_id, track_id, violation, time = information
        frame_list = []
        bbox_list = []
        for frame_information in self.frame_capture[track_id-500:track_id+500]:
            if not frame_information[2]:
                continue
            frame_list.append(frame_information[1])
            boxes = frame_information[2]
            for bb in boxes:
                if bb[-1] == track_id:
                    bbox_list.append(bb)

       
        draw_frame_list = []
        for frame, bbox in zip(frame_list, bbox_list):
            draw_frame = drawObject(frame, bbox)
            draw_frame_list.append(draw_frame)
        output_path = f"./violations/{time}_{violation}.mkv"
        frame_to_video(draw_frame_list, output_path)
        print("Done! Creating video")

