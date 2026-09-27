import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import HandLandmarksConnections
import pyautogui
import math
import tkinter as tk

# ********************* MEDIAPIPE SETUP **************************

model_path = "models/hand_landmarker.task"
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)
print("Hand detector loaded successfully")

# ************************* GESTURE RECOGNITION *********************

def recognize_gesture(hand, handedness):
    index_up = hand[8].y < hand[6].y
    middle_up = hand[12].y < hand[10].y
    ring_up = hand[16].y < hand[14].y
    pinky_up = hand[20].y < hand[18].y

    if handedness == "Right":
        thumb_extended = hand[4].x > hand[3].x
    else:
        thumb_extended = hand[4].x < hand[3].x

    if (
        not thumb_extended
        and index_up
        and not middle_up
        and not ring_up
        and not pinky_up
    ):
        return "Next"

    elif (
        not thumb_extended
        and index_up
        and middle_up
        and not ring_up
        and not pinky_up
    ):
        return "Previous"

    elif (
        thumb_extended
        and index_up
        and middle_up
        and ring_up
        and pinky_up
    ):
        return "Toggle"

    else:
        return "Unknown"

# ********************* MODE SELECTION UI **********************

def choose_mode():
    selected_mode = None

    def select_cursor_mode():
        nonlocal selected_mode
        selected_mode = "cursor"
        print("Cursor mode selected")
        root.destroy()

    def select_presentation_mode():
        nonlocal selected_mode
        selected_mode = "presentation"
        print("Presentation mode selected")
        root.destroy()

    # UI generation
    root = tk.Tk()
    root.title("GestureControl")
    root.geometry("550x450")

    # UI text
    subtitle_label = tk.Label(root, text="Choose a control mode:", font=("Roboto", 14))
    subtitle_label.pack()

    # Cursor section
    cursor_frame = tk.Frame(root)
    cursor_frame.pack(pady=(20,5))

    # Presentation section
    presentation_frame = tk.Frame(root)
    presentation_frame.pack(pady=5)

    # Widgets
    cursor_button = tk.Button(
        cursor_frame, text="Cursor Mode", 
        font=("Roboto", 14),
        width=20,
        height=2,
        command=select_cursor_mode)
    cursor_button.pack()

    cursor_description = tk.Label(cursor_frame, text="Move the cursor and pinch to click", font=("Roboto", 10))
    cursor_description.pack(pady=5)

    presentation_button = tk.Button(
        presentation_frame, 
        text="Presentation Mode", 
        font=("Roboto", 14),
        width=20,
        height=2,
        command=select_presentation_mode)
    presentation_button.pack()

    presentation_description = tk.Label(presentation_frame, text="Control presentation slides with hand gestures", font=("Roboto", 10))
    presentation_description.pack(pady=5)

    root.mainloop()

    return selected_mode

current_mode = choose_mode()

if current_mode is None:
    print("No mode selected. Exiting GestureControl.")
    exit()

# ******************* CAMERA SETUP ****************************

camera = cv2.VideoCapture(0)    # 0 connects to computer webcam

if not camera.isOpened():
    print("Error: Could not open camera.")
else:
    print("Camera opened successfully!")

# ************************* HAND VISUALIZATION ******************

def draw_hand(frame, hand):
    height, width, _ = frame.shape

    # Draw landmarks
    for landmark in hand:
        x_pixel = int(landmark.x * width)
        y_pixel = int(landmark.y * height)

        cv2.circle(frame, (x_pixel, y_pixel), 5, (0, 255, 0), -1)

    # Draw connections
    for connection in HandLandmarksConnections.HAND_CONNECTIONS:
        start = hand[connection.start]
        end = hand[connection.end]

        start_x = int(start.x * width)
        start_y = int(start.y * height)

        end_x = int(end.x * width)
        end_y = int(end.y * height)

        cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

# ********************** MAIN LOOP ***************************

last_gesture = "Unknown"
gesture_frames = 0

controls_enabled = False
pinch_active = False
cursor_frozen = False

x_min = 0.15
x_max = 0.85
y_min = 0.15
y_max = 0.85

screen_margin = 10

click_threshold = 0.04
click_release_threshold = 0.06
freeze_threshold = 0.08
unfreeze_threshold = 0.10

screen_width, screen_height = pyautogui.size()

# Smoothing setup
smooth_x = screen_width // 2
smooth_y = screen_height // 2
smoothing = 0.50
dead_zone = 8


print(f"Screen: {screen_width} x {screen_height}")

while True:
    success, frame = camera.read()
    if not success:
        break

    # Convert OpenCV BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Convert image to MediaPipe format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Detect hands
    result = detector.detect(mp_image)

# ********************** HAND ANALYSIS ************************

    if result.hand_landmarks:
        hand = result.hand_landmarks[0]
        handedness = result.handedness[0][0].category_name

        # Cursor landmarks
        index_tip = hand[8]
        thumb_tip = hand[4]

        # Convert index position to active-area coordinates
        normalized_x = (index_tip.x - x_min) / (x_max - x_min)
        normalized_y = (index_tip.y - y_min) / (y_max - y_min)

        # Keep values between 0 and 1
        normalized_x = max(0, min(1, normalized_x))
        normalized_y = max(0, min(1, normalized_y))

        # Convert normalized coordinates to screen coordinates 
        mouse_x = int(screen_margin + (1 - normalized_x) * (screen_width - 2 * screen_margin))
        mouse_y = int(screen_margin + normalized_y * (screen_height - 2 * screen_margin))


        # Calculate distance between index and thumb
        pinch_distance = math.hypot(index_tip.x - thumb_tip.x,
                                    index_tip.y - thumb_tip.y)

        # Freeze cursor when fingers start getting close
        if pinch_distance < freeze_threshold:
            cursor_frozen = True
        elif pinch_distance > unfreeze_threshold:
            cursor_frozen = False

        # Apply dead zone and smoothing only when cursor is not frozen
        if not cursor_frozen:
            if abs(mouse_x - smooth_x) > dead_zone:
                smooth_x = smooth_x + (mouse_x - smooth_x) * smoothing
        
            if abs(mouse_y - smooth_y) > dead_zone:
                smooth_y = smooth_y + (mouse_y - smooth_y) * smoothing

        # Move cursor only in Cursor Mode
        if current_mode == "cursor" and controls_enabled and not cursor_frozen:
            pyautogui.moveTo(int(smooth_x), int(smooth_y))

        # Detect pinch click
        if (
            current_mode == "cursor"
            and controls_enabled
            and not pinch_active
            and pinch_distance <= click_threshold
            ):

            print("PINCH DETECTED - CLICK")
            pyautogui.click()
            pinch_active = True

        elif pinch_distance > click_release_threshold:
            pinch_active = False

# ***************** GESTURE RECOGNITION ***********************

        gesture = recognize_gesture(hand, handedness)

# **************** GESTURE STABILITY *************************

        if gesture == last_gesture:
            gesture_frames += 1
        else:
            gesture_frames = 1
            last_gesture = gesture

    # Confirm gesture after 5 consecutive frames 
        if gesture_frames == 5 and gesture != "Unknown":
            print("Confirmed: ", gesture)

            if (
                current_mode == "presentation"
                and gesture == "Next"
                and controls_enabled
                ):
                pyautogui.press("right")

            elif (
                current_mode == "presentation"
                and gesture == "Previous"
                and controls_enabled
                ):
                pyautogui.press("left")

            elif gesture == "Toggle":
                controls_enabled = not controls_enabled
                print("Controls enabled:", controls_enabled)

# ************************ DRAW HAND **************************

        draw_hand(frame, hand)

# *************************** NO HAND DETECTED *********************

    else:
        last_gesture = "Unknown"
        gesture_frames = 0
        gesture = "Unknown"
        pinch_active = False
        cursor_frozen = False

# *********************** DISPLAY FRAME ************************

    if controls_enabled:
        status = "ON"
    else:
        status = "OFF"

    cv2.putText(frame, "Controls: " + status, (20,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Gesture: " + gesture, (20,80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Mode: " + current_mode.title(), (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("GestureControl", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ********************* CLEANUP ****************************

camera.release()    # Release camera
cv2.destroyAllWindows()     # Close OpenCV windows

