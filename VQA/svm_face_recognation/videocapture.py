from django.http import StreamingHttpResponse
from VQA.svm_face_recognation.preprocessingEmbeddings import preprocessingEmbeddings
from VQA.svm_face_recognation.trainingFaceML import trainingFaceML
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from collections.abc import Iterable
import numpy as np
import imutils
import pickle
import time
import cv2
import csv
from django.http import HttpResponseRedirect
from django.urls import reverse
l = []
def lis():
    return l

def refresh():
    l = []
    l.clear()
def flatten(lis):
    for item in lis:
        if isinstance(item, Iterable) and not isinstance(item, str):
            for x in flatten(item):
                yield x
        else:
            yield item
class Video:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        return frame

    def stop_streaming(self):
         self.video.release()

def datacreation(camera , request):
    # preprocessingEmbeddings()
    # trainingFaceML()
    embeddingFile = "VQA/svm_face_recognation/output/embeddings.pickle"
    embeddingModel = "VQA/svm_face_recognation/openface_nn4.small2.v1.t7"
    recognizerFile = "VQA/svm_face_recognation/output/recognizer.pickle"
    labelEncFile = "VQA/svm_face_recognation/output/le.pickle"
    conf = 0.5

    print("[INFO] loading face detector...")
    prototxt = "VQA/svm_face_recognation/model/deploy.prototxt"
    model = "VQA/svm_face_recognation/model/res10_300x300_ssd_iter_140000.caffemodel"
    detector = cv2.dnn.readNetFromCaffe(prototxt, model)

    print("[INFO] loading face recognizer...")
    embedder = cv2.dnn.readNetFromTorch(embeddingModel)

    recognizer = pickle.loads(open(recognizerFile, "rb").read())
    le = pickle.loads(open(labelEncFile, "rb").read())

    box = []
    username = []
    print("[INFO] starting video stream...")

    for _ in range(20):
        frame = camera.get_frame()
        frame = imutils.resize(frame, width=600)
        (h, w) = frame.shape[:2]
        imageBlob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0),
                                          swapRB=False, crop=False)

        detector.setInput(imageBlob)
        detections = detector.forward()

        for i in range(0, detections.shape[2]):

            confidence = detections[0, 0, i, 2]

            if confidence > conf:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                face = frame[startY:endY, startX:endX]
                (fH, fW) = face.shape[:2]

                if fW < 20 or fH < 20:
                    continue

                faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, (96, 96), (0, 0, 0), swapRB=True, crop=False)
                embedder.setInput(faceBlob)
                vec = embedder.forward()

                preds = recognizer.predict_proba(vec)[0]
                j = np.argmax(preds)
                proba = preds[j]
                name = le.classes_[j]
                username.append(name)
                print(name)
                l.append(name)
                text = "{}  : {:.2f}%".format(name, proba * 100)
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                cv2.putText(frame, text, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame1 = jpeg.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame1 + b'\r\n')
    print(max(l) + " is present")



