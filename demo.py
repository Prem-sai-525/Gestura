import cv2
import mediapipe as mp
import pyautogui
import time
from collections import deque

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Timing
GESTURE_COOLDOWN = 0.7  # seconds to wait after any gesture
last_gesture_time = 0

# Finger tips
FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

# Stability durations
HOLD_DURATION_PLAY = 0.2
HOLD_DURATION_FORWARD = 0.3
HOLD_DURATION_VOLUME = 0.3
HOLD_DURATION_WAVE = 0.5  # for intentional gestures

# Gesture state to track hold start
gesture_state = {
    "play": None,
    "pause": None,
    "forward": None,
    "backward": None,
    "volume_up": None,
    "volume_down": None,
    "mute": None
}

# Wrist history for wave detection
wrist_history = deque(maxlen=15)  # last 15 frames

# Helper functions
def fingers_up(landmarks, hand_label):
    """
    Returns a list of finger states [Thumb, Index, Middle, Ring, Pinky].
    hand_label: 'Left' or 'Right'
    """
    if hand_label == 'Right':
        thumb = landmarks[FINGER_TIPS[0]].x < landmarks[FINGER_TIPS[0]-1].x
    else:  # Left hand
        thumb = landmarks[FINGER_TIPS[0]].x > landmarks[FINGER_TIPS[0]-1].x

    others = [landmarks[tip].y < landmarks[tip-2].y for tip in FINGER_TIPS[1:]]
    return [thumb] + others

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7,
                    max_num_hands=2) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        now = time.time()
        h, w, _ = frame.shape

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_label = hand_handedness.classification[0].label  # 'Left' or 'Right'
                fingers = fingers_up(hand_landmarks.landmark, hand_label)

                # Only allow gestures if global cooldown passed
                if now - last_gesture_time > GESTURE_COOLDOWN:

                    # --- PLAY / PAUSE ---
                    if fingers == [0,1,0,0,1]:  # 🤘 Play
                        if gesture_state.get("play") is None:
                            gesture_state["play"] = now
                        elif now - gesture_state["play"] > HOLD_DURATION_PLAY:
                            pyautogui.press('space')
                            last_gesture_time = now
                            cv2.putText(frame,"Play 🤘",(50,100),
                                        cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
                            gesture_state["play"] = None
                    else:
                        gesture_state["play"] = None

                    if fingers == [1,1,0,0,1]:  # 🤟 Pause
                        if gesture_state.get("pause") is None:
                            gesture_state["pause"] = now
                        elif now - gesture_state["pause"] > HOLD_DURATION_PLAY:
                            pyautogui.press('space')
                            last_gesture_time = now
                            cv2.putText(frame,"Pause 🤟",(50,100),
                                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                            gesture_state["pause"] = None
                    else:
                        gesture_state["pause"] = None

                    # --- FORWARD / BACKWARD ---
                    if fingers == [1,0,0,0,0]:
                        thumb_tip = hand_landmarks.landmark[4]
                        x_px = int(thumb_tip.x * w)
                        if x_px > w // 2:  # Right side
                            if gesture_state.get("forward") is None:
                                gesture_state["forward"] = now
                            elif now - gesture_state["forward"] > HOLD_DURATION_FORWARD:
                                pyautogui.press('right')
                                last_gesture_time = now
                                cv2.putText(frame,"Forward",(50,150),
                                            cv2.FONT_HERSHEY_SIMPLEX,1,(0,200,0),2)
                                gesture_state["forward"] = None
                        else:  # Left side
                            if gesture_state.get("backward") is None:
                                gesture_state["backward"] = now
                            elif now - gesture_state["backward"] > HOLD_DURATION_FORWARD:
                                pyautogui.press('left')
                                last_gesture_time = now
                                cv2.putText(frame,"Backward",(50,150),
                                            cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,200),2)
                                gesture_state["backward"] = None
                    else:
                        gesture_state["forward"] = None
                        gesture_state["backward"] = None

                    # --- VOLUME UP 🖖 ---
                    if fingers == [1,1,1,0,1]:  # 🖖(RING FINGER) Vulcan salute
                        if gesture_state.get("volume_up") is None:
                            gesture_state["volume_up"] = now
                        elif now - gesture_state["volume_up"] > HOLD_DURATION_VOLUME:
                            pyautogui.press('volumeup')
                            last_gesture_time = now
                            cv2.putText(frame,"Volume Up 🖖",(50,50),
                                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                            gesture_state["volume_up"] = None
                    else:
                        gesture_state["volume_up"] = None

                    # --- VOLUME DOWN 🤞 ---
                    if fingers == [0,1,1,0,0]:  # 🤞
                        if gesture_state.get("volume_down") is None:
                            gesture_state["volume_down"] = now
                        elif now - gesture_state["volume_down"] > HOLD_DURATION_VOLUME:
                            pyautogui.press('volumedown')
                            last_gesture_time = now
                            cv2.putText(frame,"Volume Down 🤞",(50,50),
                                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                            gesture_state["volume_down"] = None
                    else:
                        gesture_state["volume_down"] = None

                    # --- MUTE/UNMUTE 🤙 ---
                    wrist = hand_landmarks.landmark[0]
                    wrist_history.append(wrist.x)
                    if fingers == [1,0,0,0,1]:  # Thumb + pinky extended
                        if len(wrist_history) >= wrist_history.maxlen:
                            x_positions = list(wrist_history)
                            changes = sum((x_positions[i]-x_positions[i-1])*(x_positions[i+1]-x_positions[i])<0 for i in range(1,len(x_positions)-1))
                            if changes >= 2:  # intentional wave
                                if gesture_state.get("mute") is None:
                                    gesture_state["mute"] = now
                                elif now - gesture_state["mute"] > HOLD_DURATION_WAVE:
                                    pyautogui.press('volumemute')
                                    last_gesture_time = now
                                    cv2.putText(frame,"Mute/Unmute 🤙",(50,200),
                                                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
                                    gesture_state["mute"] = None
                    else:
                        gesture_state["mute"] = None
                        wrist_history.clear()

        cv2.imshow("Gesture Media Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()