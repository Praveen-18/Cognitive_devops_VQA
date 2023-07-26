import imutils
import time
import cv2
import csv
import os
from VQA.svm_face_recognation.preprocessingEmbeddings import preprocessingEmbeddings
from VQA.svm_face_recognation.trainingFaceML import trainingFaceML
from django.shortcuts import render, redirect

def imageCapture(cam , Name , Roll_Number):
    cascade = 'VQA/svm_face_recognation/haarcascade_frontalface_default.xml'
    detector = cv2.CascadeClassifier(cascade)

    dataset = "VQA\svm_face_recognation\dataset"
    sub_data = Name
    path = os.path.join(dataset, sub_data)
    print(path)
    if not os.path.isdir(path):
        os.mkdir(path)
        print(sub_data)

    info = [str(Name) , str(Roll_Number)]
    with open('student.csv', 'a') as csvFile:
        write = csv.writer(csvFile)
        write.writerow(info)
    csvFile.close()

    total = 0

    while total < 50:
        print(total)
        gen(cam)
        frame = cam.get_frame()
        img = imutils.resize(frame, width=400)
        rects = detector.detectMultiScale(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if total == 49:
                cv2.putText(frame, "Press Stop Recognition to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255),2)
            p = os.path.sep.join([path, "{}.png".format(str(total).zfill(5))])
            cv2.imwrite(p, img)
            total += 1
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cam.stop_streaming()
    preprocessingEmbeddings()
    trainingFaceML()
    redirect('register')



class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        # ret, jpeg = cv2.imencode('.jpg', frame)
        # return jpeg.tostring()
        return frame

    def get_frame1(self):
        ret, frame = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tostring()

    def stop_streaming(self):
         self.video.release()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
