# Pi-License-Plate-Recognizer 🚘
A Python script for automatic gate control using fast-alpr to recognize car license plates in real time, powered by a Raspberry Pi 5.

# Features
- Recognizes specific car license plates via fast-alpr
- Controls a gate automatically based on recognition results
- Integrated with a custom Telegram Bot for notifications and remote actions
- Designed for reliable, 24/7 operation on Raspberry Pi 5

# Available Scripts
| Script         | Description                                              |
|----------------|---------------------------------------------------------|
| fast_current 💯 | Most complete and tested script; 24/7 operation with full Telegram Bot functionality |
| fast_247 🕰️    | Similar to fast_current, but runs without the Telegram Bot |
| fast_notis ✉️  | Like fast_247, but supports notifications without all Telegram actions |
| fast_simple ⚡  | Simple, initial detection and gate signal with camera preview window |

# Telegram Bot 🤖
Effortlessly deploy your own Telegram Bot to receive real-time notifications every time the gate is opened via license plate recognition.

- Commands:
  - /open: Open the gate remotely
  - /status: Receive Raspberry Pi hardware info
  - /reboot: Automatically reboot the pi

Supports both private and group chats for enhanced convenience and flexibility

# Extra Features
Includes a systemd service file for fast_current, enabling automatic startup after Raspberry Pi reboot
