# Gestura
Gesture-Based Media Control (Python, OpenCV, Mediapipe) Developed a real-time hand-gesture system to control media playback and volume using a webcam. Implemented multiple gestures with stability checks and intentional wave detection for precise actions..

#Purpose

This Python script uses computer vision and hand gestures to control media playback and volume on a computer. It leverages Mediapipe for hand tracking, OpenCV for video capture and visualization, and PyAutoGUI for simulating keyboard/mouse actions.

#Key Libraries

OpenCV (cv2) – Captures video from the webcam and displays frames with annotations.

Mediapipe (mediapipe) – Detects hand landmarks (fingers, wrist, etc.) in real-time.

PyAutoGUI (pyautogui) – Sends system-level input commands like key presses (space, volume control).

Collections (deque) – Keeps a short history of wrist positions to detect waving gestures.

Time (time) – Implements cooldown and hold durations for gestures.



#Gesture Detection Logic

The script checks the state of fingers and performs actions if:

The gesture is recognized.

The gesture is held long enough (HOLD_DURATION_*).

The global cooldown has passed (GESTURE_COOLDOWN).

Implemented Gestures:

Gesture	Fingers	Action
Play	🤘 [0,1,0,0,1] (Index + Pinky)	Press space
Pause	🤟 [1,1,0,0,1] (Thumb + Index + Pinky)	Press space
Forward	[1,0,0,0,0] (Thumb only) on right side	Press right arrow
Backward	[1,0,0,0,0] (Thumb only) on left side	Press left arrow
Volume Up	🖖 [1,1,1,0,1] (Vulcan salute)	Press volumeup
Volume Down	🤞 [0,1,1,0,0] (Index + Middle)	Press volumedown
Mute/Unmute	🤙 [1,0,0,0,1] (Thumb + Pinky) with waving motion	Press volumemute


Summary

This code effectively turns your webcam into a gesture-based remote control for media applications. It recognizes multiple gestures for controlling playback, navigation, volume, and mute, and includes safeguards like cooldowns, hold durations, and intentional wave detection to avoid accidental inputs.
