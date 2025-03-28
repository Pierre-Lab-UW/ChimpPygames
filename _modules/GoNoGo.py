"""
GoNoGo
==
+  what it looks like :: Each trial is wither a go or no go. 
+  how to win :: Touch during go, do not touch during no go
==
"""


from _modules.pgtools import *
import random

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

        #params for go nogo
        self.ratio = 0.7 #ratio of go tasks to no go tasks
        self.sides_num = 4
        self.go_time = 10 #time for go trial to expire in seconds
        self.width = 50

        #state variables for go-nogo
        self.cur = 0#0 for no go, 1 for go
        self.stims = []
        self.cur_time = None

    def new_trial(self):
        #calculate if go or no go task, draw red or green accordingly
        self.trial += 1
        self.state = 0
        val = 0 #random.uniform(0.00, 1.00)
        if val <= self.ratio:
            self.cur = 1
            color = GREEN
        else:
            self.cur = 0
            color = RED
        for i in range(4):
            self.stims.append(0)
        coords = [(0, 0), (0, 0), (self.g_params['SCREEN_W'] - self.width, 0), (0, self.g_params['SCREEN_H'] - self.width)]
        sizes = [(self.g_params['SCREEN_H'], self.width), (self.width, self.g_params['SCREEN_W']), (self.width, self.g_params['SCREEN_H']), (self.g_params['SCREEN_W'], self.width)]
        
        for i in range(4):
            self.stims[i] = pg.draw.rect(
                self.screen.bg,
                color,
                (
                    coords[i],
                    sizes[i],
                ),
            )


    def on_loop(self):
        #check for timing parameters for switch,(also check for mouse ) if no touch during go task, fail, if no touch during no go task, pass
        mouse_pos = pg.mouse.get_pos()
        for rect in self.stims:
            if rect.collidepoint(mouse_pos):
                pass
            
        

    def on_touch(self, touch_x=None, touch_y=None):
        #if go task, pass, otherwise fail
        return 'running'
        
    def check_for_progression(self):
        #check for num trials
        pass