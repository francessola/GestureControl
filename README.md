# GestureControl

GestureControl is a real-time computer vision application that allows users to control their computer using hand gestures captured through a webcam.

The application provides two control modes:

- **Cursor Mode:** Move the mouse cursor with your index finger and perform clicks using a pinch gesture.
- **Presentation Mode:** Navigate presentation slides using hand gestures without touching the keyboard.

## Features

- Real-time hand tracking using a webcam
- Hand gesture recognition based on 21 hand landmarks
- Cursor movement controlled by index-finger position
- Pinch-to-click interaction with click debouncing
- Cursor smoothing and dead-zone filtering for more stable movement
- Gesture-based presentation navigation
- Toggle gesture to enable or disable controls
- Separate Cursor and Presentation modes
- Visual hand landmarks and gesture/status feedback
- Mode selection interface built with Tkinter

## Gestures

| Gesture | Action | Mode |
| --- | --- | --- |
| ☝️ Index finger | Next slide | Presentation |
| ✌️ Index + middle fingers | Previous slide | Presentation |
| 🖐️ Open hand | Toggle controls ON/OFF | Both |
| 🤏 Thumb + index pinch | Mouse click | Cursor |

## Controls

- Select either **Cursor Mode** or **Presentation Mode** when the application starts.
- Use the **open-hand gesture** to enable or disable gesture controls.
- Press **q** while the GestureControl camera window is active to exit the application.

## How It Works

GestureControl processes each webcam frame through a real-time computer vision pipeline:

1. OpenCV captures frames from the webcam.
2. MediaPipe Hand Landmarker detects a hand and returns 21 normalized hand landmarks.
3. GestureControl analyzes the positions of those landmarks to recognize predefined hand gestures.
4. In Cursor Mode, the index-finger position is mapped to screen coordinates to control the cursor.
5. The distance between the thumb and index finger is used to detect pinch clicks.
6. In Presentation Mode, recognized gestures are translated into keyboard actions for slide navigation.
7. PyAutoGUI performs the corresponding mouse or keyboard action.

## Tech Stack

- **Python** - Core application logic
- **OpenCV** - Webcam capture and real-time frame processing
- **MediaPipe** - Hand landmark detection
- **PyAutoGUI** - Mouse and keyboard control
- **Tkinter** - Mode selection interface

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/francessola/GestureControl.git
cd GestureControl
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

On Windows:

```bash
.venv\Scripts\activate
```

### 4. Install the dependencies

```bash
pip install -r requirements.txt
```

### 5. Run GestureControl

```bash
python main.py
```