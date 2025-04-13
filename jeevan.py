import cv2
import serial
import time
import mediapipe as mp

# Set up serial communication (Adjust the COM port for your system)
arduino = serial.Serial('COM3', 9600)
time.sleep(2)  # Wait for the connection

# Initialize Mediapipe Hand Detection
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Button states
light_on = False
fan_on = False

# Button Positions
light_button = (50, 100, 200, 150)  # (x1, y1, x2, y2)
fan_button = (250, 100, 400, 150)   # (x1, y1, x2, y2)

# Timing for debounce
last_light_press = 0
last_fan_press = 0
debounce_time = 0.5  # 500ms

# Send command to Arduino
def send_command(device, state):
    command = f"{device}{state}"
    arduino.write(command.encode())
    print(f"Sent: {command}")

# Check if a point is inside a button area
def is_inside_button(x, y, button):
    x1, y1, x2, y2 = button
    return x1 <= x <= x2 and y1 <= y <= y2

# Open Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 20)

frame_skip = 2  # Process every 2nd frame
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip frames to improve speed

    # Flip the frame to avoid mirror effect
    frame = cv2.flip(frame, 1)

    # Convert to RGB for Mediapipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    fingertip_x, fingertip_y = None, None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_tip = hand_landmarks.landmark[8]
            h, w, _ = frame.shape
            fingertip_x, fingertip_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

            # Draw hand landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Check if fingertip is touching buttons with debounce
    current_time = time.time()

    if fingertip_x is not None and fingertip_y is not None:
        if is_inside_button(fingertip_x, fingertip_y, light_button) and (current_time - last_light_press > debounce_time):
            light_on = not light_on
            send_command('L', '1' if light_on else '0')
            last_light_press = current_time

        elif is_inside_button(fingertip_x, fingertip_y, fan_button) and (current_time - last_fan_press > debounce_time):
            fan_on = not fan_on
            send_command('F', '1' if fan_on else '0')
            last_fan_press = current_time

    # Draw buttons
    cv2.rectangle(frame, (50, 100), (200, 150), (0, 255, 0), -1)  # Light Button
    cv2.rectangle(frame, (250, 100), (400, 150), (0, 0, 255), -1)  # Fan Button

    # Button Labels
    cv2.putText(frame, "Light: " + ("ON" if light_on else "OFF"), (60, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(frame, "Fan: " + ("ON" if fan_on else "OFF"), (270, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    # Show fingertip position (optional)
    if fingertip_x is not None and fingertip_y is not None:
        cv2.circle(frame, (fingertip_x, fingertip_y), 10, (255, 0, 0), -1)

    # Display the frame
    cv2.imshow("Home Automation", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#python d:/jeee/jeevan.py
cap.release()
cv2.destroyAllWindows()
arduino.close()
