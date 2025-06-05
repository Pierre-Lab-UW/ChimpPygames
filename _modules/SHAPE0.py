f"""
SHAPE0
==
+  what it looks like :: solid-color square onscreen
+  how to win :: touching square dispenses reward

+  multiple correct responses in a row decrements square size
+  multiple incorrect responses in a row increments square size

TODO :: playtest synergy with frontend

CHANGELOG:
10/09/2023 -- modified from SHAPE1 to prevent stim size increment/decrement and task advancement, for use in testing machines with fish
            - stim size will still be pulled from TouchTrain-size.txt in relevant "_progress" folder (max stim size = 768)
02/05/2024 -- no changes to script. minor update to header comments.
"""


from _modules.pgtools import *


class SHAPE0(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'SHAPE0'
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
        """
        Initiates a new trial, draws stimulus
        """
        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        # if no datafile exists yet, create one with the column headings
        if not os.path.isfile(self.filepath_to_data):
            write_ln(self.filepath_to_data,
                     ['monkey_name', 'date', 'time', 'arm', 'task_name',
                      'trial', 'stim_size', 'touch_x', 'touch_y', 'stim_x', 'stim_y', 'correct'])

        self.trial += 1   # iterate trial counter
        # get stim_size
        with open(self.filepath_to_size, 'r') as f:
            #logging the next 5 lines in there errorlog to try to find an error that's crashing the sqm systems 21Oct22
            line = f.readline()
            log(self.monkey_name)
            log(self.filepath_to_size)
            log(line)
            log(self.stim_size)
            self.stim_size = 800
            self.stim_x, self.stim_y = (0,0)
        # to test touch zones
        #pg.draw.circle(screen.fg, Color('chartreuse'), (int(self.stim_x+self.stim_size/2), int(self.stim_y+self.stim_size/2)), int((self.stim_size / 2) + (.30*self.stim_size)), 10)
        #pg.draw.circle(screen.fg, Color('chartreuse'), (int(self.stim_x+self.stim_size/2), int(self.stim_y+self.stim_size/2)), int((self.stim_size / 2) + (.45*self.stim_size)), 10)

    def on_loop(self):
        if self.g_params['STIMULI_COLORS'] != 'normal':
            color = BLUE
        else:
            color = GREEN
        self.stimulus = pg.draw.rect(self.screen.fg, color, (self.stim_x, self.stim_y, self.stim_size, self.stim_size))

    def on_touch(self, touch_x=None, touch_y=None):

        # defining zones
        # #
        (stimulus_center_x, stimulus_center_y) = self.stimulus.center
        x_diff = (stimulus_center_x - touch_x) ** 2
        y_diff = (stimulus_center_y - touch_y) ** 2
        distance_from_stimulus = math.sqrt(x_diff + y_diff)
        correct_radius = (self.stim_size / 2) + (.30 * self.stim_size)
        nothing_happens_radius = (self.stim_size / 2) + (.45 * self.stim_size)

        # if correct touch
        # #
        
        if distance_from_stimulus < correct_radius:
            write_ln(self.filepath_to_data, [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'),
                                             self.arm_used, self.task_name, self.trial, self.stim_size,
                                             touch_x, touch_y, self.stim_x, self.stim_y, 1])
            with open(self.filepath_to_progress, 'a') as f:
                f.writelines(str(1) + '\n')
            '''
            decrement_progress, increment_progress = self.check_for_progression()
            if self.stim_size > 200 and sum(decrement_progress) == int(self.m_params[self.monkey_name]['SHAPE1_to_decrement']):
                self.stim_size -= self.lengthDecrease
            '''
        
            return 'ITI'
        # if mediocre touch
        # #
        elif distance_from_stimulus < nothing_happens_radius:
            return 'running'
        # if incorrect touch
        # #
        else:
            write_ln(self.filepath_to_data, [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'),
                                             self.arm_used, self.task_name, self.trial, self.stim_size,
                                             touch_x, touch_y, self.stim_x, self.stim_y, 0])
            with open(self.filepath_to_progress, 'a') as f:
                f.writelines(str(0) + '\n')
            '''
            decrement_progress, increment_progress = self.check_for_progression()
            if self.stim_size < self.g_params['SCREEN_W'] and \
                    sum(increment_progress) == int(self.m_params[self.monkey_name]['SHAPE1_to_increment']):
                self.stim_size += self.lengthDecrease
            '''
            with open(self.filepath_to_size, 'w') as f:
                f.write(str(self.stim_size))
            return 'timeout'
    '''
    def check_for_progression(self):
        """
        Check whether progress amounts to task advancement
        Only progress once per task
        """
        if not self.progressed:
            filepath_to_task = os.path.join('_progress', self.monkey_name, 'task-ix.txt')
            with open(self.filepath_to_progress, 'r') as f:
                raw_progress = f.readlines()
                # progress = [int(x) for x in progress]
                progress = []
                for line in raw_progress:
                    try:
                        progress.append(int(line))
                    except:
                        pass   # ignore anything in raw_progress that can't be parsed as int
                trials_to_check_criterion = int(self.m_params[self.monkey_name]['SHAPE1trials'])
                trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['SHAPE1criterion'])
                if (len(progress) >= trials_to_check_criterion) and \
                        (sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion):
                    self.progressed = True
                    with open(filepath_to_task, 'r') as f:
                        current_task = int(f.read())
                    with open(filepath_to_task, 'w') as f:
                        f.write(str(current_task + 1))
                    with open(self.filepath_to_progress, 'w') as f:
                        f.truncate(0)
            return progress[-int(self.m_params[self.monkey_name]['SHAPE1_to_decrement']):], \
                   progress[-int(self.m_params[self.monkey_name]['SHAPE1_to_increment']):]
        else:
            return 0, 0
    '''