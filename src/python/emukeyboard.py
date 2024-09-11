import ctypes
from utils import waitFrames
from joypad import FRAMES_RELEASE_TIME

# Define necessary structures and functions from the Windows API
PUL = ctypes.POINTER(ctypes.c_ulong)

# Convert Joypad inputs to Windows keycode presses
KEYCODE_DICT = {
    "Up": 0x48,       # Up Arrow key
    "Left": 0x4B,     # Left Arrow key
    "Right": 0x4D,    # Right Arrow key
    "Down": 0x50,     # Down Arrow key
    "X": 0x1F,        # S key
    "Y": 0x1E,        # Q key
    "A": 0x2D,        # X key
    "B": 0x2C,        # W key
    "Start": 0x1C,    # Enter key
    "Select": 0x39,   # Right Shift key
    "L": 0x10,        # A key
    "R": 0x11,        # Z key
    "Menu": 0x29,     # ² key
    "Lua Console": 0x26 # L key
}

# Classes needed for Windows API
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Function to simulate key press
def pressKey(hexKeyCode):

    # Convert joypad presses to keycode
    if (isinstance(hexKeyCode, str)):
        hexKeyCode = KEYCODE_DICT[hexKeyCode]

    # Check if it's an extended key (E0 prefix) and set the flag
    flags = 0x0008  # KEYEVENTF_SCANCODE
    if hexKeyCode in (0x4D, 0x48, 0x50, 0x4B):  # Extended keys like Page Down, Arrows, etc.
        flags |= 0x0001  # KEYEVENTF_EXTENDEDKEY

    # Call Windows API to simulate a press
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Function to simulate key release
def releaseKey(hexKeyCode):

    # Convert joypad presses to keycode
    if (isinstance(hexKeyCode, str)):
        hexKeyCode = KEYCODE_DICT[hexKeyCode]

    # Check if it's an extended key (E0 prefix) and set the flag
    flags = 0x0008 | 0x0002  # KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP
    if hexKeyCode in (0x4D, 0x48, 0x50, 0x4B):  # Extended keys like Page Down, Arrows, etc.
        flags |= 0x0001  # KEYEVENTF_EXTENDEDKEY

    # Call Windows API to simulate a release
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def pressButton(button):
    print(button)

    # Press the button for 5 frames
    pressKey(button)
    waitFrames(5)

    # Release the button for 5 frames
    releaseKey(button)
    waitFrames(5)

# Press every button in order
def pressButtons(*buttons):
    for button in buttons:
        pressButton(button)

# Press the button for the provided number of frames
def holdButton(button, numberOfFrames):
    pressKey(button)
    waitFrames(numberOfFrames)
    releaseKey(button)