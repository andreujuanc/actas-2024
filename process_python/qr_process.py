import cv2
from pyzbar.pyzbar import decode

def do(qr_path):
    # Load the QR code image using OpenCV
    qr_image = cv2.imread(qr_path)

    # Decode the QR code
    decoded_objects = decode(qr_image)

    # Extract information from the decoded QR code
    qr_info = []
    for obj in decoded_objects:
        qr_info.append(obj.data.decode('utf-8'))

    # Return the decoded information
    return(qr_info[0])
