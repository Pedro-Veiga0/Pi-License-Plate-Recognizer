import cv2
from fast_alpr import ALPR
from gpiozero import OutputDevice
from time import sleep

# Initialize ALPR
alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)

# Initialize relay pin (change to your GPIO pin number)
relay_pin_number = 17
relay = OutputDevice(relay_pin_number)

# Allowed license plates (you can add as many as needed)
allowed_plates = {"AB12CD", "44GV20", "XYZ789"}

# Open your RTSP stream
rtsp_url = "rtsp://username:password@ip_address/stream1"
cap = cv2.VideoCapture(rtsp_url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    alpr_results = alpr.predict(frame)

    if alpr_results:
        for result in alpr_results:
            plate_text = result.ocr.text
            confidence = result.ocr.confidence
            print(f"Detected Plate: {plate_text}, Confidence: {confidence:.2f}")

            # Check if the recognized plate is in your allowed list with a confidence threshold
            if plate_text in allowed_plates and confidence > 0.95:
                print(f"Allowed plate {plate_text} detected - Opening gate.")
                relay.on()         # Activate relay (relay closes circuit)
                sleep(1)         # Keep relay on for 1 second
                relay.off()        # Deactivate relay

    cv2.imshow("ALPR Gate Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()