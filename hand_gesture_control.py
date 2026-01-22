# Virtual Air Mouse using OpenCV, MediaPipe, and PyAutoGUI
# Author: Python Computer Vision Expert Mode

import cv2
import mediapipe as mp
import pyautogui
import math
import sys

# -------------------- INITIAL SETUP --------------------
pyautogui.FAILSAFE = False
screen_width, screen_height = pyautogui.size()

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# -------------------- CAMERA SETUP --------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ERROR: Cannot open webcam")
    sys.exit()

prev_x, prev_y = 0, 0
smoothening = 7

# -------------------- MAIN LOOP --------------------
while True:
    success, frame = cap.read()
    if not success:
        print("⚠️ Frame not captured")
        break

    # Flip for mirror effect
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm_list = []

            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            # Draw Tony Stark HUD-style landmarks
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=3),
                mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2)
            )

            # -------------------- INDEX FINGER CONTROL --------------------
            index_x, index_y = lm_list[8][1], lm_list[8][2]

            screen_x = screen_width * index_x / w
            screen_y = screen_height * index_y / h

            # Smooth movement
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            pyautogui.moveTo(curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y

            # -------------------- CLICK (PINCH) --------------------
            thumb_x, thumb_y = lm_list[4][1], lm_list[4][2]

            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)

            if distance < 30:
                cv2.circle(frame, (index_x, index_y), 15, (0, 0, 255), -1)
                pyautogui.click()

    # HUD Text
    cv2.putText(frame, "VIRTUAL AIR MOUSE | Press Q to Exit",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 255, 0), 2)

    cv2.imshow("🖐️ Virtual Air Mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -------------------- CLEANUP --------------------
cap.release()
cv2.destroyAllWindows()
