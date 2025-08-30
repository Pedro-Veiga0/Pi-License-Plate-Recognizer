import cv2
from fast_alpr import ALPR
from gpiozero import LED
from time import sleep, time

# Relay on GPIO17, active_low=True since most relay boards are active LOW
relay = LED(17, active_high=False)

# Initialize ALPR once
alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)

# Allowed license plates (you can add as many as needed)
allowed_plates = {"AB12CD", "44GV20", "XYZ789"}

# Open your RTSP stream
rtsp_url = "rtsp://username:password@ip_address/stream1"
cap = cv2.VideoCapture(rtsp_url)

# Cooldown time in seconds (3 minutes)
trigger_cooldown = 180  
last_trigger_time = 0

frame_skip = 5  # only run ALPR every 5th frame
frame_count = 0

def open_camera():
    """Try to open RTSP camera, retry until success"""
    cap = None
    while cap is None or not cap.isOpened():
        print("Trying to connect to camera...")
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            print("Camera not available, retrying in 5s...")
            sleep(5)
        else:
            print("Camera connected")
    return cap

cap = open_camera()

while True:
    try:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame, reconnecting...")
            cap.release()
            cap = open_camera()
            continue

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue  # skip this frame

        alpr_results = alpr.predict(frame)

        if alpr_results:
            for result in alpr_results:
                plate_text = result.ocr.text.strip()
                confidence = result.ocr.confidence
                print(f"Detected Plate: {plate_text}, Confidence: {confidence:.2f}")

                if (
                    plate_text in allowed_plates
                    and confidence > 0.98
                    and time() - last_trigger_time > trigger_cooldown
                ):
                    print(f" Allowed plate {plate_text} detected - Opening gate.")
                    relay.on()   # Close relay (simulate button press)
                    sleep(1)     # Hold relay for 1 second
                    relay.off()  # Release relay

                    last_trigger_time = time()

    except Exception as e:
        print(f"Unexpected error: {e}")
        sleep(2)  # prevent crash loops

cap.release()