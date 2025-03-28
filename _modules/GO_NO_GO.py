from datetime import time

from _modules.pgtools import *

import random
import threading

import os


class GO_NO_GO(object):

    # defined phases here

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        # initialising basic parameters
        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'GO_NO_GO'
        self.monkey_name = monkey_name
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])


        try:
         self.ratio  = int(self.m_params[self.monkey_name]['GNG_Ratio'])

        except:
         print('RATIO:  ' + self.m_params[self.monkey_name]['GNG_Ratio'])

        self.timeout = 5 # set to default
        self.treats_dispensed = 0
        self.time = 0  # start at zero

        self.stop_timer = False

        self.stim_x = 0  # define stimuli position to be at the top of screen
        self.stim_y = 0
        self.progressed = False
        self.stimulus_moving = False

        self.shape_pos_x = 0
        self.shape_pos_y = 0

        width, height = pg.display.get_window_size()

        self.width = width
        self.height = height

        self.shape_pos_x = width / 2
        self.shape_pos_y = height / 2

        print(f"position x{self.shape_pos_x}")
        print(f"position y{self.shape_pos_y}")

        pg.mouse.set_pos((self.shape_pos_x, self.shape_pos_y))

        # define phases, dtermines if this is training, or a trial (2 trainings one  actual trial)
        self.phases = {
            "Phase 1": "Basic Training",
            "Phase 2": "Accelerated Training",
            "Phase 3": "Actual Trial"
        }
        # generate a random number between 1 and 2, (where 0 3 )
        self.trial_mode = random.choice([1, 2])
        self.go_threshold = 5

    # draw shapes on screen
    def on_loop(self):
        # Use the same position for each trial mode

        if self.trial_mode == 1:
            self.region = pg.draw.rect(self.screen.fg, Color('White'),
                                       rect=(0, 0, self.width, 100), width=45)

            self.stimulus = pg.draw.circle(self.screen.fg, color=Color('White'),
                                           center=(self.shape_pos_x, self.shape_pos_y),
                                           radius=15)
            print('stim drawn 1')

        elif self.trial_mode == 2:

            self.region = pg.draw.rect(self.screen.fg, Color('red'),
                                       rect=(0, 0, self.width, 100), width=45)

            self.stimulus = pg.draw.circle(self.screen.fg, color=Color('red'),
                                           center=(self.shape_pos_x, self.shape_pos_y),
                                           radius=15)
            print('stim drawn 2')

        self.on_touch(self)

    def update_time(self):
        if not self.stop_timer:
            self.time += 1
            # Set up the next timer
            threading.Timer(1.0, self.time).start()

    def stop_updating(self):

        self.stop_timer = True

    def new_trial(self):
        # code to ensure data is saved
        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name,
                                                                               time.strftime('%Y-%m-%d'),
                                                                               self.task_name))

        # needto change filename
        self.filepath_to_size = os.path.join('_progress', self.monkey_name, 'TouchTrain-size.txt')
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')

        # self.mode = self.set_mode(self.m_params[self.monkey_name]['mode'])  # will determine how these work later

    # instead of considering a touch in one region, consider it to be a drag in that region
    def on_touch(self, touch_x=None, touch_y=None):
        print('started moving')

        mouse_x, mouse_y = pg.mouse.get_pos()
        print(mouse_x)
        print(mouse_y)
        self.shape_pos_x = mouse_x
        self.shape_pos_y = mouse_y

        # check regions depending on mode

        if self.trial_mode == 1:

            if self.shape_pos_y <= 100:
                return 'ITI'
            elif self.shape_pos_y > 100 and (self.time < self.timeout):
                return 'timeout'

        if self.trial_mode == 2:
            if self.shape_pos_y > 100 and (self.time >= self.timeout):
                return 'ITI'
            elif self.shape_pos_y <= 100:
                return 'timeout'

    def set_mode(self, mode):
        if mode not in self.phases:
            return None
        else:
            print(f"Set mode to {mode}")
            return mode
