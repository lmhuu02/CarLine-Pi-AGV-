import http.client as client
import cv2 as cv
import pytesseract
import numpy as np
import time
import sys
from picamera.array import PiRGBArray
from picamera import PiCamera


def readIP(LABELMAP_NAME = 'IP.txt'):
    labels=[]
    with open(LABELMAP_NAME, 'r') as f:
        for text in f.readlines():
            labels=np.append(labels,text.strip('\n'))
    return labels
def findContour(img,spa=200,f=0):
    bigger = np.array([])
    max_area = 0
    st = False
    img_Clone = img.copy()
    blur = cv.GaussianBlur(img_Clone,(7,7), 1)
    gray = cv.cvtColor(blur,cv.COLOR_BGR2GRAY)
    canny = cv.Canny(gray,spa,spa)
    dilate = cv.dilate(canny,kernel,iterations = 3)
    erode = cv.erode(dilate,kernel,iterations = 2)
    if f:
        cv.imshow('imh',erode)
    contours = cv.findContours(erode, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)[1]
    
    for contour in contours:
       max_temp = int(cv.contourArea(contour))
       if max_temp > 40000:
           peri = cv.arcLength(contour,True)
           approx = cv.approxPolyDP(contour,0.02*peri,True)
           if max_area < max_temp and len(approx) == 4:
               max_area = max_temp
               bigger = approx
               if not st:
                   st = True
    return st,bigger
def warpImg(img,bigger,widht=320,hight=240):
    myP = bigger.reshape((4,2))
    myPNew = np.zeros((4,2),np.int32)
    add = myP.sum(1)
    myPNew[0] = myP[np.argmin(add)]
    myPNew[3] = myP[np.argmax(add)]
    diff = np.diff(myP,axis=1)
    myPNew[1] = myP[np.argmin(diff)]
    myPNew[2] = myP[np.argmax(diff)]
    pts1 = np.float32(myPNew)
    pts2 = np.float32([[0,0],[widht,0],[0,hight],[widht,hight]])
    matrix = cv.getPerspectiveTransform(pts1,pts2)
    imgWarp = cv.warpPerspective(img,matrix,(widht,hight))
    return imgWarp
def checkWord(img,labels):
    size = img.shape[0:2]
    word = 'Unknow'
    id_word = None
    index =-1
    st=False
    img = cv.resize(img,(size[1],size[0]))
    text = pytesseract.image_to_data(img,lang='eng',config='--psm 6')
    for t in text.splitlines():
        t = t.split()
        if len(t)==12 and t[0] == '5':
            tam = str(t[11])
            tam = tam.lower()
            for i,label in enumerate(labels):
                if tam == label.lower():
                    x,y,w,h = int(t[6]),int(t[7]),int(t[8]),int(t[9])
                    img = cv.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    img = cv.putText(img,t[11],(x,y-10),2,0.6,(0,0,255),2)
                    st=True
                    word = label
                    break
    return st,img,word
def stackImages(img,img1,labels,sizeWork=0.5,size = (680,480)):
    img = cv.resize(img,(size[0],size[1]))
    img1 = cv.resize(img1,(size[0],size[1]))
    img1 = cv.rectangle(img1,(0,size[1]//4*3),(size[0],size[1]),(255,255,255),-1)
#     img1 = cv.putText(img1,word,(int(size[0]//2.5),int(size[1]//4*3.4)),2,0.8,(100,50,0),2)
    img1 = cv.putText(img1,'Ma Vung: ',(int(size[0]//15),int(size[1]//4*3.3)),2,sizeWork,(100,250,0),2)
    if len(labels) > 0:
        for i,label in enumerate(labels):
            img1 = cv.putText(img1,str(label),((int(size[0]//5)*(i+1)),int(size[1]//4*3.7)),2,sizeWork,(0,50,255),2)
    else:
        img1 = cv.putText(img1,'[Nothing!]',(int(size[0]//2.2),int(size[1]//4*3.7)),2,sizeWork,(0,0,255),2)
    img_ = np.hstack((img,img1))
    return img_
def getClient(IP):
    code =[]
    for i in range(len(IP)):
        print(IP[i])
        try:
            conn = client.HTTPConnection(str(IP[i]))
            conn.request('POST','/agv/getvitri.php?stt=1')
            response = conn.getresponse()
            if response.status == 200:
                data = response.readline()
                data = data.decode()
                IP_ok = IP[i]
                for t in data.splitlines():
                    code = np.append(code,t.split())
                    return code,i
            conn.close()
        except Exception as e:
            print(' request error: ',e)
            if i >= len(IP)-1:
                sys.exit()
def postClient(IP,data):
    try:
        conn = client.HTTPConnection(str(IP))
        conn.request('POST','/agv/getvitri.php?stt=2&nVitri='+str(data))
        response = conn.getresponse()
        if response.status == 200:
            data = response.readline()
            data = data.decode()
            if data == 'ok':
                conn.close()
                return True
        conn.close()
        return False
    except Exception as e:
        print('request error: ',e)
        cv.destroyAllWindows()
        sys.exit()
if __name__ == "__main__":
#   labels = readLabel()
    hight,width = 480,640
    imgH,imgW   = 240,320
    camera = PiCamera()
    camera.resolution = (width, hight)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(width, hight))
    time.sleep(1)
    imgw = np.ones((imgH,imgW,3),np.uint8)
    add=0;
    IP = readIP()
    labels,add=getClient(IP)
    print(labels)
    word_ = 'Unknow'
    time_=[0,0,0]
    khoa =False
    uid=None
    kernel = np.ones((5,5),np.uint8)
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        img = frame.array
        imgClone = img.copy()
        st,bigger = findContour(imgClone,150,0)
        if st:
            img = cv.drawContours(img,bigger,-1,(255,0,0),15)
            time_[0]=time.time()
            if time.time()-time_[1] > 0.3 and not khoa:
                imgw = warpImg(imgClone,bigger,imgW,imgH)
                khoa,imgw,word_ = checkWord(imgw,labels)
        else:
            time_[1]=time.time()
        if time.time()-time_[0] > 3:
            khoa = False
        if(khoa and word_ != None):
            time_[2]=time.time()
            stt_ok = postClient(IP[add],word_)
            if stt_ok:
                print('send: ',stt_ok)
            else:
                labels,add=getClient(IP)
                stt_ok = postClient(IP[add],word_)
                if stt_ok:
                    break
            word_ = None
        result = stackImages(img,imgw,labels,sizeWork=0.9,size =(int(width//1.2),int(hight//1.2)))
        cv.imshow('result',result)
        key = cv.waitKey(1) & 0xff
        if key in [ord('q'),ord('Q')]:
            break
        rawCapture.truncate(0)
    cv.destroyAllWindows()
    sys.exit()