
import time
import os
import shutil
import subprocess
import ctypes
import win32api
import win32gui
import win32ui
import win32con
import pygetwindow

from PIL import Image
from pywinauto import Application
from pygetwindow import Win32Window

import memory
import emukeyboard

GAME_HEIGHT = 384
GAME_WIDTH = 256
TOPBORDER_SIZE = 1

SAVERAM_LOCATION = "../../Programmes/BizHawk/NDS/SaveRAM/"
SAV_LOCATION = "roms/"
BACKUP_LOCATION = "roms/Backup/Saves/"

SAVENAMES = {
    "Diamant": "Pokemon - Version Diamant (France) (Rev 5).SaveRAM",
    "Perle": "Pokemon - Version Perle (France) (Rev 5).SaveRAM",
    "Platine": "Pokemon - Version Platine (France).SaveRAM"
}

###################################################################################
# Main Emulator class used to setup the emulator to be run with the Python script #
###################################################################################
class Emulator():
    def __init__(self, name, executableName, partialTitle, saveExtension, menuColor):
        self.name = name
        self.executableName = executableName
        self.partialTitle = partialTitle
        self.saveExtension = saveExtension
        self.menuColor = menuColor

        self.mainWindow = None
        self.secondaryWindow = None
        self.luaScriptWindow = None

    def __eq__(self, other):
        return isinstance(other, Emulator) and self.name == other.name
    

    ########################################################################################################
    # Launch Emulator window, position/resize it, and make sure Lua script is running on BizHawk instances #
    ########################################################################################################
    def initEmulator(self, gameName, fullscreen = False):

        # Retrieve emulator window by executable
        emulatorWindowList = self.findEmuWindowByTitle(self.name)
        self.mainWindow = None

        if (emulatorWindowList):
            self.mainWindow = emulatorWindowList[0] # Take first instance

            # Game not launched : don't bother navigating in the menu, close the emulator and relaunch it
            if (self.partialTitle not in self.mainWindow.title or gameName not in self.mainWindow.title):
                self.mainWindow.closeWindow()
                self.mainWindow = None

        # Emulator not open, launch it
        if (not self.mainWindow):
            self.mainWindow = self.launchEmu(gameName)

        # Makes the window take up the whole height and set it to the left of the screen
        self.mainWindow.resizeWindow(fullscreen)
        self.mainWindow.gameName = gameName
        print(self.mainWindow)

        # Run shinybot Lua Script on BizHawk
        if (self == BIZHAWK):
            self.runLuaScript()
    

    ####################################################################
    # Launch Emulator secondary instance window and resize/position it #
    ####################################################################
    def initSecondEmulatorInstance(self, gameName, fullscreen = False):

        # Retrieve emulator window by executable
        emulatorWindowList = self.findEmuWindowByTitle(self.name)

        # There's supposed to be an instance already running
        if (not emulatorWindowList or self.mainWindow not in emulatorWindowList):
            print("No instance running, cannot run a second instance")
            return None
        
        # Only work with initialized instances
        if (self.partialTitle not in self.mainWindow.title):
            print("ROM not launched on first instance")
            return None

        # Only one instance running, launch the second one
        if (len(emulatorWindowList) == 1):
            self.secondaryWindow = self.launchEmu(gameName, self.mainWindow)

        # Already two instances running
        else:
            self.secondaryWindow = emulatorWindowList[1 - emulatorWindowList.index(self.mainWindow)]

            # Game not launched : don't bother navigating in the menu, close the emulator and relaunch it
            if (self.partialTitle not in self.secondaryWindow.title):
                self.secondaryWindow.closeWindow()
                self.secondaryWindow = self.launchEmu(gameName, self.mainWindow)

        # Makes the window take up the whole height and set it to the left of the screen
        self.secondaryWindow.resizeWindow(self, fullscreen, self.mainWindow)
        self.secondaryWindow.gameName = gameName
        print(self.secondaryWindow)


    ######################################################
    # Search Emulator open instances with provided title #
    ######################################################
    def findEmuWindowByTitle(self, windowTitle):
        windowList = []
        windows = [Window(self, window) for window in pygetwindow.getWindowsWithTitle(windowTitle)]

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
                    
                    if (windowExecutableName == self.executableName):
                        windowList.append(window)
            except Exception as e:
                print(f"Error checking window: {e}")
        return windowList


    ####################################################################
    # Wait until the Emulator instance with the provided title is open #
    ####################################################################
    def waitUntilOpen(self, titleWindow, firstInstance = None):

        # Polling for the window to appear
        maxWaitTime = 10  # Max time to wait (in seconds)
        pollInterval = 0.1  # Time between each poll (in seconds)
        elapsedTime = 0

        # Periodically check if the window is open
        while elapsedTime < maxWaitTime:
            windowList = self.findEmuWindowByTitle(titleWindow)

            if windowList:
                # No instance running, return the first one we find
                if (not firstInstance):
                    return windowList[0]
                # Instance already running, return the new one
                elif (len(windowList) == 2):
                    return windowList[1 - windowList.index(firstInstance)]
                    
            time.sleep(pollInterval)
            elapsedTime += pollInterval


    ######################################################################
    # Execute Emulator executable with the provided Pokemon game version #
    ######################################################################
    def launchEmu(self, pokemonGameVersion, firstInstance = None):
        print("Emulator not open, opening it...")

        try:
            process = subprocess.Popen("../../Programmes/" + self.name + "/" + self.executableName + " roms/PokemonVersion" + pokemonGameVersion + ".nds")
        except OSError as e:
            print(f"Error: {e}")
            print("Please run this script as an administrator.")
            exit(1)

        # Wait until emulator window is open
        emuWindow = self.waitUntilOpen(self.name, firstInstance)

        # Wait until ROM finishes loading
        print("ROM launching...")
        time.sleep(2)
        print("Emulator open !")

        return emuWindow
    

    ###########################################################
    # Make sure the Lua Script is running on Bizhawk instance #
    ###########################################################
    def runLuaScript(self):
    
        # Lua Console window
        luaConsoleWindowList = self.findEmuWindowByTitle("Lua Console")

        # Lua Console not open, press L to open it
        if (not luaConsoleWindowList):
            self.mainWindow.activate()
            emukeyboard.pressButton("Lua Console")
            self.luaScriptWindow = self.waitUntilOpen("Lua Console")
        else:
            self.luaScriptWindow = luaConsoleWindowList[0] # Take first instance

        # If Lua script is not running, just restart the console to automatically start the script
        if (not memory.isLuaScriptRunning()):
            self.luaScriptWindow.closeWindow()

            # Give BizHawk focus, then press L again to open the Lua Console
            self.mainWindow.activate()
            emukeyboard.pressButton("Lua Console")
            self.luaScriptWindow = self.waitUntilOpen("Lua Console")

        # Minimize the window after we're done with it
        self.luaScriptWindow.minimize()


    #######################################################################################
    # Import save file of the other Emulator and make it readable by the current Emulator #
    #######################################################################################
    def importSaveFile(self, pokemonGame):
        if (pokemonGame not in SAVENAMES):
            print("Unknown game : " + str(pokemonGame))
            return None
        
        # Retrieve SaveRAM and sav files
        saveRamFile = SAVERAM_LOCATION + SAVENAMES[pokemonGame]
        savFile = SAV_LOCATION + "PokemonVersion" + pokemonGame + ".sav"
        timestamp = time.strftime('%Y%m%d-%H%M%S')

        # Backup both SaveRAM and sav files
        backupFile(saveRamFile, timestamp)
        backupFile(savFile, timestamp)

        # Replace SaveRAM by sav or vice versa
        if (self.saveExtension == "sav"):
            replaceFile(savFile, saveRamFile)
        else:
            replaceFile(saveRamFile, savFile)



###############################################################################
# Custom Window class extending Win32Window and adding an Emulator dependency #
###############################################################################
class Window(Win32Window):
    def __init__(self, emulator: Emulator, window: Win32Window):
        super().__init__(window._hWnd)
        self.parentEmulator = emulator
        self.gameName = None

    def __eq__(self, other):
        return (isinstance(other, Window) or isinstance(other, Win32Window)) and self._hWnd == other._hWnd
    
    def __str__(self):
        return super().__str__() + " running Pokémon Version " + str(self.gameName) + " on " + self.parentEmulator.name
    

    ########################################################
    # Simulate clicking on the window X button to close it #
    ########################################################
    def closeWindow(self):
        win32gui.PostMessage(self._hWnd, win32con.WM_CLOSE, 0, 0)
        time.sleep(0.5)


    ########################################################################
    # Make the window take the whole screen heigth or put it in fullscreen #
    ########################################################################
    def resizeWindow(self, fullscreen, firstInstance = None):

        # Retrieve titlebar, menu and borders size
        titleBarHeight, borderSize, menuHeight = self.retrieveBordersSize()

        # Fullscreen : hide titlebar/menu at the top of the screen and put the app in front of Windows taskbar
        if (fullscreen):
            # Apply a new style to remove the borders and titlebar
            borderlessStyle = win32gui.GetWindowLong(self._hWnd, win32con.GWL_STYLE) & ~win32con.WS_OVERLAPPEDWINDOW
            win32gui.SetWindowLong(self._hWnd, win32con.GWL_STYLE, borderlessStyle)

            # Toggle off menu if present
            if (self.parentEmulator == BIZHAWK and menuHeight > 0):
                self.activate()
                emukeyboard.pressButton("Menu")
                menuHeight = 0

            # Get whole screen height resolution
            screenHeight = ctypes.windll.user32.GetSystemMetrics(1)

            windowHeight = screenHeight # Take the whole screen height
            windowWidth = (int((screenHeight - menuHeight) # Only take game height for ratio calculation
                            * GAME_WIDTH / GAME_HEIGHT)) # Keep original game ratio

            # Move BizHawk window to the top-left of the screen, make it not stay on top
            win32gui.SetWindowPos(self._hWnd, win32con.HWND_TOPMOST, (firstInstance.width - 2 * borderSize if firstInstance else 0), 0, windowWidth, windowHeight, 
                win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)
            
        # Not fullscreen : keep titlebar, menu and taskbar
        else:
            # Apply a new style to restore borders and titlebar
            borderStyle = win32gui.GetWindowLong(self._hWnd, win32con.GWL_STYLE) | win32con.WS_OVERLAPPEDWINDOW
            win32gui.SetWindowLong(self._hWnd, win32con.GWL_STYLE, borderStyle)

            # Toggle menu if absent
            if (self.parentEmulator == BIZHAWK and menuHeight == 0):
                self.activate()
                emukeyboard.pressButton("Menu")

                # Retrieve updated menu size
                menuHeight = self.getMenuHeight(titleBarHeight, borderSize)

            # Get screen height minus the task bar
            screenHeight = getScreenHeightMinusTaskbar()

            windowHeight = (screenHeight # Take the whole screen height minus the taskbar
                            + borderSize # Hide transparent border behind the taskbar
                            + TOPBORDER_SIZE) # Hide the single half-transparent pixel border behind the taskbar

            windowWidth = (int((screenHeight - titleBarHeight - menuHeight) # Only take game height for ratio calculation
                            * GAME_WIDTH / GAME_HEIGHT) # Keep original game ratio
                            + 2 * borderSize) # Add both left/right borders
            
            # Move BizHawk window to the top-left of the screen, make it not stay on top
            win32gui.SetWindowPos(self._hWnd, win32con.HWND_NOTOPMOST, -borderSize + (firstInstance.width - 2 * borderSize if firstInstance else 0), -TOPBORDER_SIZE, windowWidth, windowHeight, 
                win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)


    ######################################################################################
    # Temporarly update the window's size to make borders/titlebar/menu size retrievable #
    ######################################################################################
    def retrieveBordersSize(self):

        # Restore window if minimized
        if self.isMinimized:
            self.restore()
            time.sleep(0.1)

        # Temporarly set window size to 500x100 and add borders to calculate menu size
        borderStyle = win32gui.GetWindowLong(self._hWnd, win32con.GWL_STYLE) | win32con.WS_OVERLAPPEDWINDOW
        win32gui.SetWindowLong(self._hWnd, win32con.GWL_STYLE, borderStyle)
        win32gui.SetWindowPos(self._hWnd, win32con.HWND_NOTOPMOST, 0, 0, 500, 100, 
                win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW)

        # Get titlebar height and borders sizeS by comparing window size to app size
        titleBarHeight, borderSize = self.getBordersSize()

        # Retrieve menu size from screenshot
        menuHeight = self.getMenuHeight(titleBarHeight, borderSize)

        return titleBarHeight, borderSize, menuHeight
    

    ###########################################################
    # Get window's side/top/bottom borders and title bar size #
    ###########################################################
    def getBordersSize(self):
        windowRect = win32gui.GetWindowRect(self._hWnd) # Position of the window including borders
        clientRect = win32gui.GetClientRect(self._hWnd) # Position of the window not including borders

        borderSize = int(((windowRect[2] - windowRect[0]) - clientRect[2]) / 2) # Size of transparent border on each side
        titleBarHeight = ((windowRect[3] - windowRect[1]) - clientRect[3]) - borderSize # Size of top window title bar

        return titleBarHeight, borderSize


    ##########################################################################################
    # Get window's menu heigth by counting the number of pixels with its specific menu color #
    ##########################################################################################
    def getMenuHeight(self, titleBarHeight, borderSize):
        
        screenshot = self.captureWindow()
        height = screenshot.size[1]

        # Iterate on each first pixel until we find a pixel with a different color
        for y in range(height - titleBarHeight):
            firstPixel = screenshot.getpixel((borderSize, y + titleBarHeight))

            # Different color : we reached the end of the menu
            if (firstPixel not in self.parentEmulator.menuColor):
                return y
        
        # Default : menu not present
        return 0


    #####################################################################
    # Capture the content of the window and return it as a PILLOW Image #
    #####################################################################
    def captureWindow(self):
        # Get window dimensions
        left, top, right, bot = win32gui.GetWindowRect(self._hWnd)
        width = right - left
        height = bot - top

        # Create a device context (DC)
        hwndDC = win32gui.GetWindowDC(self._hWnd)
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
        win32gui.ReleaseDC(self._hWnd, hwndDC)
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()

        return screnshot


# Two possible emulators
BIZHAWK = Emulator("BizHawk", "EmuHawk.exe", "Pokemon", "SaveRAM", menuColor = [(240,240,240)])
MELONDS = Emulator("melonDS", "melonDS.exe", "[", "sav", menuColor = [(242,242,242), (255,255,255)])

########################################
# Retrieve screen height minus taskbar #
########################################
def getScreenHeightMinusTaskbar():
    monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))
    work_area = monitor_info.get("Work") 
    return work_area[3]

######################################################
# Save both SaveRAM and sav files in a backup folder #
######################################################
def backupFile(filePath, timestamp):

    # Get the file name and extension
    baseName = os.path.basename(filePath)

    # Only backup existing files
    if os.path.exists(filePath):

        # Create the timestamp and the backup filename
        backupFileName = f"Backup-{timestamp}-{baseName}"
        
        # Construct the full path for the backup
        backupPath = os.path.join(BACKUP_LOCATION, backupFileName)
        
        # Copy the saveram file to the backup directory
        shutil.copy2(filePath, backupPath)
        print(f"Backup created : {backupPath}")
    else:
        print("Save file does not exist : " + baseName)

####################################################################
# Replace old save file by a new save file from the other emulator #
####################################################################
def replaceFile(fileToReplace, fileToKeep):

    # Remove the old save file
    if os.path.exists(fileToReplace):
        os.remove(fileToReplace)
        print(f"Old save file removed : {fileToReplace}")
    
    # Rename old save file to new
    if os.path.exists(fileToKeep):
        shutil.copy2(fileToKeep, fileToReplace)
        print(f"'{fileToKeep}' renamed to '{fileToReplace}'")
    else:
        print("Original save file does not exist : " + fileToKeep)