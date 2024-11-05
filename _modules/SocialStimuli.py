"""
SocialStimuli 
==
+  what it looks like :: 
+  how to win :: 
==

"""
from _modules.pgtools import *
import pygame as pg
import time

class SocialStimuli(object):
    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):
        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'Social_Stimuli_As_Rewards'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')
        self.filepath_to_phase = os.path.join('_progress', self.monkey_name, 'TI_phase.txt')

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.stimulus = None
        self.stim_x = self.g_params['SCREEN_W']/2
        self.stim_y = self.g_params['SCREEN_H']/2
        self.progressed = False 

        #custom parameters(these need to be loaded in)
        self.trialAmt = 6
        self.stim_size = 150
        self.stimTime = 5 #seconds
        #tracking
        self.playingGif = False
        self.timeStartedPlaying  = 0

    def new_trial(self):
        """
        Initiates a new trial
        """
        #how long should circle be shown before failed trial?
        self.trial += 1
        self.playingGif = False
        

        
    def on_loop(self):
        if not self.playingGif:
            self.stimulus = pg.draw.circle(self.screen.bg, Color('green'),
                                        (self.stim_x, self.stim_y), self.stim_size)
        else:
            if time.time() - self.timeStartedPlaying >= self.stimTime:
                self.new_trial()

    def on_touch(self, touch_x=None, touch_y=None):
        if self.playingGif:
            return 'None'
        #if the monkey touched the circle properly
        (stimulus_center_x, stimulus_center_y) = self.stimulus.center
        x_diff = (stimulus_center_x - touch_x) ** 2
        y_diff = (stimulus_center_y - touch_y) ** 2
        distance_from_stimulus = math.sqrt(x_diff + y_diff)
        correct_radius = (self.stim_size / 2) + (.30 * self.stim_size)

        if distance_from_stimulus < correct_radius:
            print("touched stimuli")
            self.screen.refresh("black")
            pg.draw.circle(self.screen.bg, Color('red'),
                                        (self.stim_x, self.stim_y), self.stim_size)
            self.playingGif = True
            #play the gif
            self.timeStartedPlaying = time.time()
            #update progress on this trial
            with open(self.filepath_to_progress, 'a') as f:
                f.writelines(str(1) + '\n')
            #write data to csv
            write_ln(
                    self.filepath_to_data,
                    data=[
                        self.monkey_name,
                        self.trial,
                        int(self.stim_size),
                        "foo",
                        self.stimTime*1000,
                    ],
                )

            self.check_for_progression()

        return 'running'

    def check_for_progression(self):
        #check if we have completed a certain number of trials
        if not self.progressed:
            print("checking for progession")
            filepath_to_task = os.path.join('_progress', self.monkey_name, 'task-ix.txt')
            with open(self.filepath_to_progress, 'r') as f:
                raw_progress = f.readlines()
                # progress = [int(x) for x in progress]
                progress = []
                for line in raw_progress:
                    try:
                        progress.append(int(line))
                    except:
                        pass
            if len(progress) >= self.trialAmt:
                self.progressed = True
                with open(filepath_to_task, 'r') as f:
                    current_task = int(f.read())
                with open(filepath_to_task, 'w') as f:
                    f.write(str(current_task + 1))
                with open(self.filepath_to_progress, 'w') as f:
                    f.truncate(0)