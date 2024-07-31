import cv2
import numpy as np
from pyzbar.pyzbar import decode, ZBarSymbol

def find_qr(imagepath, filename):
    # Load the image using OpenCV
    image_path = imagepath
    image = cv2.imread(image_path)

    # Resize the image to a smaller scale
    scale = 0.3
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    image = cv2.resize(image, (width, height))

    # Convert to grayscale and apply thresholding
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Dilate the thresholded image
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours and get bounding boxes
    bboxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        xmin, ymin, width, height = cv2.boundingRect(cnt)
        extent = area / (width * height)

        # Filter non-rectangular objects and small objects
        if (extent > np.pi / 4) and (area > 100):
            bboxes.append((xmin, ymin, xmin + width, ymin + height))

    # Detect QR codes within the bounding boxes
    qrs = []
    info = set()
    margin = 5  # Margin in pixels
    for xmin, ymin, xmax, ymax in bboxes:
        roi = image[ymin:ymax, xmin:xmax]
        detections = decode(roi, symbols=[ZBarSymbol.QRCODE])
        for barcode in detections:
            info.add(barcode.data)
            # bounding box coordinates
            x, y, w, h = barcode.rect
            qrs.append((max(0, xmin + x - margin), max(0, ymin + y - margin),
                        min(image.shape[1], xmin + x + w + margin),
                        min(image.shape[0], ymin + y + h + margin)))

    # If QR code detected, crop the image to the QR code area
    if qrs:
        xmin, ymin, xmax, ymax = qrs[0]
        qr_cropped_image = image[ymin:ymax, xmin:xmax]
        qr_cropped_image_path = f'.\qrs_img\qr-{filename}'
        cv2.imwrite(qr_cropped_image_path, qr_cropped_image)
        return(qr_cropped_image_path)
    else:
        print(f'QR not detected for {imagepath}')

