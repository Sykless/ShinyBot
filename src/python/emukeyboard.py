import ctypes
from utils import waitFrames
from joypad import FRAMES_RELEASE_TIME

# Define necessary structures and functions from the Windows API
PUL = ctypes.POINTER(ctypes.c_ulong)

# Convert Joypad inputs to Windows keycode presses
KEYCODE_DICT = {
    "Up": 0x26,       # Up Arrow key
    "Left": 0x25,     # Left Arrow key
    "Right": 0x27,    # Right Arrow key
    "Down": 0x28,     # Down Arrow key
    "X": 0x1F,        # S key
    "Y": 0x10,        # Q key
    "A": 0x2D,        # X key
    "B": 0x11,        # W key
    "Start": 0x0D,    # Enter key
    "Select": 0xA1,   # Right Shift key
    "L": 0x1E,        # A key
    "R": 0x2C,        # Z key
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

    # Call Windows API to simulate a press
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

# Function to simulate key release
def releaseKey(hexKeyCode):

    # Convert joypad presses to keycode
    if (isinstance(hexKeyCode, str)):
        hexKeyCode = KEYCODE_DICT[hexKeyCode]

    # Call Windows API to simulate a release
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def pressButton(button):
    
    # Press the button for 5 frames
    pressKey(button)
    waitFrames(5)

    # Release the button for 5 frames
    releaseKey(button)
    waitFrames(5)

