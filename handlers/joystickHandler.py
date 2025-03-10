import win32api
import datetime
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MouseController
from handlers.baseHandler import baseHandler
from enum import Enum

class JOYSTICK_STATE(Enum):
    NON_PREMUTO = 0
    PRESSING = 1
    RELEASING = 2

class JoyStickHandler(baseHandler):
    def __init__(self):
        super().__init__()
        self.joyState = JOYSTICK_STATE.NON_PREMUTO
        self.timeToRelease = None
        self.radius = 100

    def deadzoning(self, val):
        if abs(val) < 10:
            return 0
        return val

    def coordinatePipeline(self, val):
        val = self.deadzoning(val)
        val /= 100
        return val

    def pressKeys(self):
        self.keyboard.press(Key.shift)
        self.mouse.press(Button.middle)
        self.keyboard.press(Key.ctrl_l)

    def releaseKeys(self):
        self.keyboard.release(Key.shift)
        self.mouse.release(Button.middle)
        self.keyboard.release(Key.ctrl_l)

    
        
    def handleMouseMovement(self, xVal, yVal, doPacman):
        squareX = 1000
        squareY = 500
        xmPos,ymPos = win32api.GetCursorPos()
        win32api.ShowCursor(False)

        if (xmPos < squareX - self.squareLato or xmPos > squareX + self.squareLato or 
            ymPos < squareY - self.squareLato or ymPos > squareY + self.squareLato):
            xmPos = squareX
            ymPos = squareY
            win32api.SetCursorPos((xmPos - int(xVal), ymPos + int(yVal)))
        else:
            win32api.SetCursorPos((xmPos - int(xVal), ymPos + int(yVal)))


    def handle(self, dic):
        xVal = dic['XValue']
        yVal = dic['YValue']

        xVal = self.coordinatePipeline(xVal)
        yVal = self.coordinatePipeline(yVal)

        print(self.joyState)

        if self.joyState == JOYSTICK_STATE.NON_PREMUTO:
            if yVal != 0 or xVal != 0:
                self.joyState = JOYSTICK_STATE.PRESSING
                self.pressKeys()
                self.handleMouseMovement(xVal, yVal)
        elif self.joyState == JOYSTICK_STATE.PRESSING:
            if yVal == 0 and xVal == 0:
                self.timeToRelease = datetime.datetime.now() + datetime.timedelta(seconds=0.2)
                self.joyState = JOYSTICK_STATE.RELEASING
            self.handleMouseMovement(xVal, yVal)
        elif self.joyState == JOYSTICK_STATE.RELEASING:
            self.handleMouseMovement(xVal, yVal)
            if yVal != 0 or xVal != 0:
                self.joyState = JOYSTICK_STATE.PRESSING
            else:
                currentTime = datetime.datetime.now()
                if self.timeToRelease != None and self.timeToRelease < currentTime:
                    self.releaseKeys()
                    self.timeToRelease = None
                    self.joyState = JOYSTICK_STATE.NON_PREMUTO