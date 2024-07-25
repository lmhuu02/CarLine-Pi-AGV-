import cv2 as cv
import tesseract
import numpy as np
import time

cap = cv.VideoCapture(0)
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    d = tesseract.image_to_data(frame)
    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (text, x, y, w, h) = (d['text'][i], d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            # don't show empty text
            if text and text.strip() != "":
                frame = cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                frame = cv.putText(frame, text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

    # Display the resulting frame
    cv.imshow('frame', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()