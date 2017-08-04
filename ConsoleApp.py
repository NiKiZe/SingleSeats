#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script requires the following Python modules:
#  pygame   - http://www.pygame.org/
# Win32 users may also need:
#  pywin32  - http://sourceforge.net/projects/pywin32/
#  pip install pypiwin32

import pygame
import win32con
import win32api
from pygame.locals import *

import ArtemisEvents

# """ Main Console runner for Artemis SingleSeat handling """

def click(x,y):
    """ Make the cursor move and click """
    # win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | \
        win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP | \
        win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)

def mousemove(x,y):
     nx = x * 65535 / win32api.GetSystemMetrics(0)
     ny = y * 65535 / win32api.GetSystemMetrics(1)
     win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | \
        win32con.MOUSEEVENTF_MOVE, nx, ny)

def press(VK_CODE):
    """ Press a key on the keyboard """
    win32api.keybd_event(VK_CODE, 0, 0, 0)
    pygame.time.wait(5)
    win32api.keybd_event(VK_CODE, 0, win32con.KEYEVENTF_KEYUP, 0)

def press_s(VK_CODE):
    """ Press shift + a key on the keyboard """
    win32api.keybd_event(0xA0, 0, 0, 0)
    pygame.time.wait(5)
    press(VK_CODE)
    pygame.time.wait(10)
    win32api.keybd_event(0xA0, 0, win32con.KEYEVENTF_KEYUP, 0)

def main():
    """ This is main
    """
    title = 'Artemis SingleSeat Console by NiKiZe, based on Stugos work'
    print(title)
    print("You'll need to run Artemis in Full Screen Windowed")

    event_engine = ArtemisEvents.HandlerTcp()
    event_engine.connect()
    pygame.init()

    # Set the width and height of the screen [width,height]
    screen = pygame.display.set_mode([300, 200])
    pygame.display.set_caption(title)

    # Initialize the joysticks
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in \
        range(pygame.joystick.get_count())]

    for joy in joysticks:
        joy.init()
        print("Joystick name: ", joy.get_name())
        print("Joystick id: ", joy.get_id())
        print("Number of buttons: ", joy.get_numbuttons())
        break
    else:
        print("Sorry, no joysticks were found!")

    #Loop until the user clicks the close button.
    dorun = True
    while dorun:
        pygame.time.wait(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                dorun = False
                ArtemisEvents.Handler.dump_events()
                event_engine.kill()
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                pass
            elif event.type in (pygame.MOUSEMOTION, \
                pygame.MOUSEBUTTONDOWN, \
                pygame.MOUSEBUTTONUP):
                pass
            elif event.type == pygame.ACTIVEEVENT:
                pass
            else:
                print('event type: %r' % event)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()

if __name__ == "__main__":
    main()
