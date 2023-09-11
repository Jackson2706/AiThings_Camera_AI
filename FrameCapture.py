'''
    Creating a queue to store frames captured from camera
'''
class FrameCaptureQueue:
    def __init__(self):
        self.frame_queue = []
        self.count = -1
    
    def push(self,frame):
        self.frame_queue.append(frame)
        self.count = self.count + 1
    
    def pop(self):
        self.count = self.count - 1
        frame = self.frame_queue.pop(0)
        return frame
    
    def isEnough(self):
        return self.count > 1000
    
    def isEmpty(self):
        return self.count == -1
    

    
    
