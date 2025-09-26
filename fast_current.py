import cv2
import psutil
import os
from fast_alpr import ALPR
from gpiozero import LED
from time import sleep, time
from telegram import Bot
from datetime import datetime
from telegram.ext import Updater, CommandHandler

#Setup telegram bot
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = 123456789  # replace with your chat ID
bot = Bot(token=BOT_TOKEN)

# Relay on GPIO17, active_low=True since most relay boards are active LOW
relay = LED(17, active_high=False)

# Initialize ALPR once
alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)

# Allowed license plates
allowed_plates = {"AB12CD", "44GV20", "XYZ789"}

# RTSP camera stream
rtsp_url = "rtsp://username:password@ip_address/stream1"

# Cooldown time in seconds (3 minutes)
trigger_cooldown = 180  
last_trigger_time = 0

frame_skip = 5  # only run ALPR every 5th frame
frame_count = 0

def send_message(text: str):
    """Send a Telegram message safely (no crash on errors)."""
    bot.send_message(chat_id=CHAT_ID, text=text)

def pi_status():
    cpu_freq = f"{psutil.cpu_freq().current:.0f} MHz" 
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    temps = psutil.sensors_temperatures()
    temp = temps['rp1_adc'][0].current if 'rp1_adc' in temps else None

    status_msg = (
        f"💻 Raspberry Pi Status:\n"
        f"⚙️ CPU: {cpu_freq}\n"
        f"💾 RAM: {mem.percent}%\n"
        f"💿 Disk: {disk.percent}%\n"
    )
    if temp:
        status_msg += f"🌡️ Temp: {temp:.1f} C\n"
    return status_msg

def open_camera():
    """Try to open RTSP camera, retry until success"""
    cap = None
    while cap is None or not cap.isOpened():
        print("Trying to connect to camera...")
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            send_message("🔺 Camera not available, retrying every 5s...")
            print("Camera not available, retrying in 5s...")
            sleep(5)
        else:
            send_message("🟢 Camera connected")
            print("Camera connected")
    return cap

# Actions
def start(update, context):
    update.message.reply_text("🤖 Bot is running. Use /open to open the gate, /status for Pi stats.")

def open_gate(update, context):
    relay.on()
    sleep(1)
    update.message.reply_text("🔓 Gate opening...")
    relay.off()

def status(update, context):
    update.message.reply_text(pi_status())

def reboot_pi(update, context): 
    update.message.reply_text("🔄 Rebooting Raspberry Pi...")
    # Give Telegram a chance to send the reply before reboot
    os.system("sudo reboot now")
    
#send message whenever raspberry pi restarts
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
send_message(f"🔌 Raspberry Pi restarted at {timestamp}")

#opens camera
cap = open_camera()

# bot actions
updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("open", open_gate))
dp.add_handler(CommandHandler("status", status))
dp.add_handler(CommandHandler("reboot", reboot_pi))

updater.start_polling()

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

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    send_message(f"🚗 Gate opened for plate {plate_text} at {timestamp}")

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        send_message(f"❌ Script crashed at {timestamp}\nError: {e}") #message telegram when theres an unexpected crash
        sleep(2)  # prevent crash loops

cap.release()
