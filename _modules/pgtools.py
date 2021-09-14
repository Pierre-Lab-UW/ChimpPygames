"""
Helper functions for monkey testing
==
+ connective tissue testing in python
+ i/o mostly

TODO add helpers - play sounds, etc

WW2021
"""

# IMPORTS
# #
import sys, os, random, time, glob, logging, math
# import RPi.GPIO as GPIO
import pygame as pg
from pygame.locals import *


# CONSTANTS
# #
BLACK = (1, 1, 1)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (0, 128, 128)
CORRECT_COLOR = GREEN
INCORRECT_COLOR = RED
BUFFER_COLOR = BLACK

HOSTROOT = ''
TODAY = time.strftime('%Y-%m-%d')
TIME = time.strftime('%H:%M')
FPS = 10
CLIPART_TO_LOAD = 10


# INIT PYGAME
# #
pg.init()
pg.font.init()
sm_font = pg.font.SysFont(None, 32)
big_font = pg.font.SysFont(None, 64)


# SYSTEM NAME
# #
try:
    with open(os.path.join('/home', 'pi', 'Desktop', 'SystemName.txt'), 'r') as f:
        system_name = f.read()
except:
    system_name = TODAY


# LOAD SOUNDS
# #
sounds = {}
for sound in glob.glob(os.path.join('_sounds', '*.wav')):
    sounds[os.path.basename(sound).replace('.wav', '')] = pg.mixer.Sound(sound)
    sounds[os.path.basename(sound).replace('.wav', '')].set_volume(.25)


# SCREEN
# #
class Screen(object):
    def __init__(self, size=None, color=None, fullscreen=False):
        """
        Pygame screen on which to draw stimuli, etc.

        :param size: screen resolution in pixels
        :param col: screen bg color
        :param fullscreen: fullscreen if True, not fullscreen if False
        """
        self.rect = pg.Rect((0, 0), size)
        self.bg = pg.Surface(size)
        self.color = color
        self.bg.fill(self.color)
        if fullscreen:
            self.fg = pg.display.set_mode(size, (NOFRAME and FULLSCREEN))
        else:
            self.fg = pg.display.set_mode(size)

    def refresh(self, color=None):
        self.bg.fill(Color(color))
        self.fg.blit(self.screen.bg, (0, 0))


# STIMULUS
# # # #

class Stimulus(object):

    def __init__(self, size=None, image=None, pos=None):
        self.image = image
        self.size = size
        self.pos = pos
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = pg.Rect(pos+(size, size))

    def draw_stimulus(self, screen=None):
        pg.draw.rect(screen.fg, Color('goldenrod'), (self.pos[0], self.pos[1], self.size, self.size), 15)
        screen.fg.blit(self.image, self.pos)


# FILE IO
# # #
def log(message=None):
    print(message)
    logging.info(message)


def write_ln(filename=None, data="", csv=True):
    """
    Write a list to a file as comma- or tab-delimited. Not passing a list
    results in a blank line.

    :param filename: filepath to datafile
    :param data: list of data to be output
    :param csv: comma-delimited if True, tab-delimited if False
    """
    data = data
    local_filename = None
    if os.path.exists(os.path.join('/home', 'pi', 'Desktop', 'local_files')):
        local_filename = os.path.join('/home', 'pi', 'Desktop', 'local_files', os.path.basename(filename))
    files_to_write = [filename] if local_filename is None else [filename, local_filename]
    for name in files_to_write:
        with open(name, "a+") as data_file:
            if csv:
                data_file.write(", ".join(map(str, data)) + "\n")
            else:
                data_file.write("\t".join(map(str, data)) + "\n")


# HELPERS
# # #
def check_quit(event=None):
    """
    Close program if quit, esc, q pressed
    """
    if event.type == QUIT or (event.type == KEYDOWN and (event.key in (K_ESCAPE, K_q))):
        log('User quit the program')
        raise SystemExit


def pellet(time_to_close_relay=.25):
    """
    Dispense pellets.

    :param num: number of pellets to dispense
    """
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.LOW)

        time.sleep(time_to_close_relay)

        GPIO.output(17, GPIO.HIGH)
        GPIO.cleanup()
    except:
        log('pellet')

if __name__ == "__main__":
    exit()
