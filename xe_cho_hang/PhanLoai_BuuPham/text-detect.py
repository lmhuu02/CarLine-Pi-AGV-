import cv2
import pytesseract

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
# cap.set(10,70)


while True:
    success, img = cap.read()
    # print(objectInfo)
    cv2.imshow("Frame", img)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        text = pytesseract.image_to_string(img)
        print(text)
        cv2.imshow("Frame", img)
        cv2.waitKey(0)
        break

cv2.destroyAllWindows()