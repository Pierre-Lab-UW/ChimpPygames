"""
GoNoGo
==
+  what it looks like :: Each trial is wither a go or no go. 
+  how to win :: Touch during go, do not touch during no go
==
"""


from _modules.pgtools import *


class GoNoGo(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'GoNoGo'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_size = os.path.join('_progress', monkey_name, 'TouchTrain-size.txt')
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.stimulus = None
        self.stim_size = 0
        self.stim_x = 0
        self.stim_y = 0
        self.lengthDecrease = 10
        self.heightDecrease = 10
        self.progressed = False

    def new_trial(self):
        #calculate if go or no go task, draw red or green accordingly
        pass

    def on_loop(self):
        #check for timing parameter, if no touch during go task, fail, if no touch during no go task, pass
        pass

    def on_touch(self, touch_x=None, touch_y=None):
        #if go task, pass, otherwise fail
        pass

    def check_for_progression(self):
        #check for num trials
        pass