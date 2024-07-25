# Import Thu Vien
import cv2 as cv
from pyzbar import pyzbar
import sys
import requests

# Get danh sach 
def getDiadiem(host):
    r = requests.get(str(host)+'/AGV/getVitri.php?stt=1')
    a= r.text.split(' ')
    a.pop(-1)
    a.pop(-1)
    print(a)

# Dua du lieu len severr
def postSever(host,data): #postSever(host,xe,data):
    stt_ok = requests.get(str(host)+'/AGV/getVitri.php?stt=2&nVitri='+str(data))
    if stt_ok.text=='ok':
        return f'Gui Thanh Cong Kien Hang Toi Dia Diem {data}'
    else:
        return 'Gui khong Thanh Cong'

# ham code chinh
if __name__ == "__main__":

    host = 'http://autospams.click'
    returnn = ''

    cap = cv.VideoCapture(0)

    diadiem = getDiadiem(host)
    print(diadiem)
    while True:
        ret, frame = cap.read()
        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            # Ve line qr
            (x, y, w, h) = barcode.rect
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Du lieu quet duoc
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            # Ghi chu truc tiep ra man hinh -- PB_TN(QR-CODE)
            text = "{} ({})".format(barcodeData, barcodeType)
            cv.putText(frame, text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 2)
            
            # Kiem tra co ton tai khong gui len sever
            if not barcodeData:
                print("Khong tim thay")
            else:
                if returnn != barcodeData : #Kiem tra xe co trung voi ket qua vua quet truoc do khong
                    print(barcodeData)
                    returnn = barcodeData
                    print(postSever(host,returnn))

        cv.imshow('Camera',frame)
        if cv.waitKey(1) == 113:
            break

    cv.destroyAllWindows()
    sys.exit()

#========================Z03=======================================
