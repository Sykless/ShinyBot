

import time
import subprocess
import ctypes
import win32api
import win32gui
import win32ui
import win32con
import pygetwindow as gw

from PIL import Image
from pywinauto import Application

import memory
import emukeyboard

GAME_HEIGHT = 384
GAME_WIDTH = 256
TOPBORDER_SIZE = 1
MENU_COLOR = (240,240,240)

class Emulator():
    def __init__(self, name, executableName, partialTitle, menuColor):
        self.name = name
        self.executableName = executableName
        self.partialTitle = partialTitle
        self.menuColor = menuColor

    def __eq__(self, other):
        return isinstance(other, Emulator) and self.name == other.name


BIZHAWK = Emulator("BizHawk", "EmuHawk.exe", "Pokemon", "SaveRAM", [(240,240,240)])
MELONDS = Emulator("melonDS", "melonDS.exe", "[", "sav", [(242,242,242), (255,255,255)])

def initEmulator(emulator, gameName, fullscreen = False):

    # Retrieve emulator window by executable
    emulatorWindowList = findWindowByExecutable(emulator.name, emulator.executableName)
    emulatorWindow = None

    if (emulatorWindowList):
        emulatorWindow = emulatorWindowList[0] # Take first instance

        # Game not launched : don't bother navigating in the menu, close the emulator and relaunch it
        if (emulator.partialTitle not in emulatorWindow.title):
            closeWindow(emulatorWindow)
            emulatorWindow = None

    # Emulator not open, launch it
    if (not emulatorWindow):
        emulatorWindow = launchEmu(emulator, gameName)

    # Makes the window take up the whole height and set it to the left of the screen
    resizeWindow(emulator, emulatorWindow, fullscreen)
    print(emulatorWindow)

    # Run shinybot Lua Script on BizHawk
    if (emulator == BIZHAWK):
        runLuaScript(emulatorWindow)

    return emulatorWindow


def initSecondEmulatorInstance(emulator, gameName, firstInstance, fullscreen = False):

    # Retrieve emulator window by executable
    emulatorWindowList = findWindowByExecutable(emulator.name, emulator.executableName)

    # There's supposed to be an instance already running
    if (not emulatorWindowList or firstInstance not in emulatorWindowList):
        print("No instance running, cannot run a second instance")
        return None
    
    # Only work with initialized instances
    if (emulator.partialTitle not in firstInstance.title):
        print("ROM not launched on first instance")
        return None

    # Only one instance running, launch the second one
    if (len(emulatorWindowList) == 1):
        secondInstance = launchEmu(emulator, gameName, firstInstance)

    # Already two instances running
    else:
        secondInstance = emulatorWindowList[1 - emulatorWindowList.index(firstInstance)]

        # Game not launched : don't bother navigating in the menu, close the emulator and relaunch it
        if (emulator.partialTitle not in secondInstance.title):
            closeWindow(secondInstance)
            secondInstance = launchEmu(emulator, gameName, firstInstance)

    # Makes the window take up the whole height and set it to the left of the screen
    resizeWindow(emulator, secondInstance, fullscreen, firstInstance)
    print(secondInstance)


def waitUntilOpen(titleWindow, executableName, firstInstance = None):

    # Polling for the window to appear
    maxWaitTime = 10  # Max time to wait (in seconds)
    pollInterval = 0.1  # Time between each poll (in seconds)
    elapsedTime = 0

    # Periodically check if the window is open
    while elapsedTime < maxWaitTime:
        windowList = findWindowByExecutable(titleWindow, executableName)

        if windowList:
            # No instance running, return the first one we find
            if (not firstInstance):
                return windowList[0]
            # Instance already running, return the new one
            elif (len(windowList) == 2):
                return windowList[1 - windowList.index(firstInstance)]
                
        time.sleep(pollInterval)
        elapsedTime += pollInterval


def launchEmu(emulator, pokemonGameVersion, firstInstance = None):
    print("Emulator not open, opening it...")

    try:
        process = subprocess.Popen("../../Programmes/" + emulator.name + "/" + emulator.executableName + " roms/PokemonVersion" + pokemonGameVersion + ".nds")
    except OSError as e:
        print(f"Error: {e}")
        print("Please run this script as an administrator.")
        exit(1)

    # Wait until emulator window is open
    emuWindow = waitUntilOpen(emulator.name, emulator.executableName, firstInstance)

    # Wait until ROM finishes loading
    print("ROM launching...")
    time.sleep(2)
    print("Emulator open !")

    return emuWindow


def retrieveBordersSize(emulator, window):

    # Unique Windows identifier
    hwnd = window._hWnd

    # Restore window if minimized
    if window.isMinimized:
        window.restore()
        time.sleep(0.1)

    # Temporarly set window size to 500x100 and add borders to calculate menu size
    borderStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE) | win32con.WS_OVERLAPPEDWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, borderStyle)
    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 500, 100, 
            win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)

    # Get titlebar height and borders sizeS by comparing window size to app size
    titleBarHeight, borderSize = getBordersSize(hwnd)

    # Retrieve menu size from screenshot
    screenshot = captureWindow(hwnd)
    menuHeight = getMenuHeight(screenshot, titleBarHeight, borderSize, emulator.menuColor)

    return titleBarHeight, borderSize, menuHeight


def resizeWindow(emulator, window, fullscreen, firstInstance = None):

    # Retrieve titlebar, menu and borders size
    titleBarHeight, borderSize, menuHeight = retrieveBordersSize(emulator, window)
    hwnd = window._hWnd

    # Fullscreen : hide titlebar/menu at the top of the screen and put the app in front of Windows taskbar
    if (fullscreen):
        # Apply a new style to remove the borders and titlebar
        borderlessStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE) & ~win32con.WS_OVERLAPPEDWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, borderlessStyle)

        # Toggle off menu if present
        if (emulator == BIZHAWK and menuHeight > 0):
            window.activate()
            emukeyboard.pressButton("Menu")
            menuHeight = 0

        # Get whole screen height resolution
        screenHeight = ctypes.windll.user32.GetSystemMetrics(1)

        windowHeight = screenHeight # Take the whole screen height
        windowWidth = (int((screenHeight - menuHeight) # Only take game height for ratio calculation
                        * GAME_WIDTH / GAME_HEIGHT)) # Keep original game ratio

        # Move BizHawk window to the top-left of the screen, make it not stay on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, (firstInstance.width - 2 * borderSize if firstInstance else 0), 0, windowWidth, windowHeight, 
            win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)
        
    # Not fullscreen : keep titlebar, menu and taskbar
    else:
        # Apply a new style to restore borders and titlebar
        borderStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE) | win32con.WS_OVERLAPPEDWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, borderStyle)

        # Toggle menu if absent
        if (emulator == BIZHAWK and menuHeight == 0):
            window.activate()
            emukeyboard.pressButton("Menu")

            # Retrieve updated menu size
            screenshot = captureWindow(hwnd)
            menuHeight = getMenuHeight(screenshot, titleBarHeight, borderSize, emulator.menuColor)

        # Get screen height minus the task bar
        screenHeight = getScreenHeightMinusTaskbar()

        windowHeight = (screenHeight # Take the whole screen height minus the taskbar
                        + borderSize # Hide transparent border behind the taskbar
                        + TOPBORDER_SIZE) # Hide the single half-transparent pixel border behind the taskbar

        windowWidth = (int((screenHeight - titleBarHeight - menuHeight) # Only take game height for ratio calculation
                        * GAME_WIDTH / GAME_HEIGHT) # Keep original game ratio
                        + 2 * borderSize) # Add both left/right borders
        
        # Move BizHawk window to the top-left of the screen, make it not stay on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, -borderSize + (firstInstance.width - 2 * borderSize if firstInstance else 0), -TOPBORDER_SIZE, windowWidth, windowHeight, 
            win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)
        

def runLuaScript(bizhawkWindow):
    
    # Lua Console window
    luaConsoleWindowList = findWindowByExecutable("Lua Console", BIZHAWK.executableName)

    # Lua Console not open, press L to open it
    if (not luaConsoleWindowList):
        bizhawkWindow.activate()
        emukeyboard.pressButton("Lua Console")
        luaConsoleWindow = waitUntilOpen("Lua Console", BIZHAWK.executableName)
    else:
        luaConsoleWindow = luaConsoleWindowList[0] # Take first instance

    # Check if script is already running
    luaScriptRunning = memory.isLuaScriptRunning()

    # If script is not running, just restart the console to automatically start the script
    if (not luaScriptRunning):
        closeWindow(luaConsoleWindow)

        # Give BizHawk focus, then press L again to open the Lua Console
        bizhawkWindow.activate()
        emukeyboard.pressButton("Lua Console")
        luaConsoleWindow = waitUntilOpen("Lua Console", BIZHAWK.executableName)

    # Minimize the window after we're done with it
    luaConsoleWindow.minimize()


def findWindowByExecutable(windowTitle, executableName):
    windowList = []
    windows = gw.getWindowsWithTitle(windowTitle)

    # Iterate on every window containing a specific string in their title
    for window in windows:
        try:
            # Retrieve PID from the window HWND (unique identifier)
            app = Application(backend = 'uia').connect(handle = window._hWnd)
            processId = app.process
            
            # Use tasklist command to get the executable name from PID
            command = f'tasklist /fi "PID eq {processId}" /fo csv /nh'
            output = subprocess.check_output(command, shell = True).decode("latin-1")
            
            # Extract the executable name from the output
            lines = output.splitlines()
            if lines:
                # Split the CSV line to retrieve executable name and strip any extra quotes
                windowExecutableName = lines[0].split(',')[0].strip('"')
                
                if windowExecutableName == executableName:
                    windowList.append(window)
        except Exception as e:
            print(f"Error checking window: {e}")
    return windowList

def getScreenHeightMinusTaskbar():
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))
    work_area = monitor_info.get("Work") # Retrieve screen height minus taskbar
    return work_area[3]

def getBordersSize(hwnd):
    windowRect = win32gui.GetWindowRect(hwnd) # Position of the window including borders
    clientRect = win32gui.GetClientRect(hwnd) # Position of the window not including borders

    borderSize = int(((windowRect[2] - windowRect[0]) - clientRect[2]) / 2) # Size of transparent border on each side
    titleBarHeight = ((windowRect[3] - windowRect[1]) - clientRect[3]) - borderSize # Size of top window title bar

    return titleBarHeight, borderSize

def getMenuHeight(screenshot, titleBarHeight, borderSize, menuColor):
    height = screenshot.size[1]

    # Iterate on each first pixel until we find a pixel with a different color
    for y in range(height - titleBarHeight):
        firstPixel = screenshot.getpixel((borderSize, y + titleBarHeight))

        # Different color : we reached the end of the menu
        if (firstPixel not in menuColor):
            return y
    
    # Default : menu not present
    return 0

def closeWindow(window):
    win32gui.PostMessage(window._hWnd, win32con.WM_CLOSE, 0, 0)
    time.sleep(0.5)

def captureWindow(hwnd):
    # Get window dimensions
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top

    # Create a device context (DC)
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Create a bitmap object from DC and window dimensions
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # BitBlt (copy) the window content to the bitmap
    saveDC.BitBlt((0,0), (width, height), mfcDC, (0,0), win32con.SRCCOPY)

    # Convert the bitmap to an actual image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    screnshot = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    # Clean up
    win32gui.ReleaseDC(hwnd, hwndDC)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()

    return screnshot