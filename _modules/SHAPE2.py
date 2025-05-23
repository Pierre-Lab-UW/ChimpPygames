"""
SHAPE2 aka TOUCHTRAIN2
==
+  what it looks like :: small solid-color square onscreen that moves to a new coord on each new trial
+  how to win :: touching square dispenses reward
==
As part of monkeys' initial training battery Summer2021
"""


from _modules.pgtools import *


class SHAPE2(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'SHAPE2'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_size = os.path.join('_progress', monkey_name, 'TouchTrain-size.txt')
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.stimulus = None
        self.clipart = clipart
        self.clipart_this_trial = None
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

        self.trial += 1                                                         # iterate trial counter
        self.stim_size = int(self.m_params[self.monkey_name]['SHAPE2size'])     # get stim_size
        self.clipart_this_trial = self.clipart[random.choice(list(self.clipart.keys()))]

        if self.g_params['RESTRICT_SCREEN']:
            (self.stim_x, self.stim_y) = (
                                        random.randint(int(self.g_params['SCREEN_W'] * .15), int(self.g_params['SCREEN_W'] * .85) - self.stim_size),
                                        random.randint(int(self.g_params['SCREEN_H'] * .15) + 50, self.g_params['SCREEN_H'] - self.stim_size)
                                         )
        else:
            (self.stim_x, self.stim_y) = (random.randint(0, (self.g_params['SCREEN_W'] - self.stim_size)),
                                          random.randint(0, (self.g_params['SCREEN_H'] - self.stim_size)))

        # to test touch zones
        # pg.draw.circle(screen.fg, Color('chartreuse'), (int(self.stim_x+self.stim_size/2), int(self.stim_y+self.stim_size/2)), int((self.stim_size / 2) + (.30*self.stim_size)), 10)
        # pg.draw.circle(screen.fg, Color('chartreuse'), (int(self.stim_x+self.stim_size/2), int(self.stim_y+self.stim_size/2)), int((self.stim_size / 2) + (.45*self.stim_size)), 10)

    def on_loop(self):
        self.stimulus = pg.draw.rect(self.screen.fg, Color('goldenrod'),
                                     (self.stim_x, self.stim_y, self.stim_size, self.stim_size), 15)
        self.screen.fg.blit(pg.transform.scale(self.clipart_this_trial, (self.stim_size, self.stim_size)), (self.stim_x, self.stim_y))

    def on_touch(self, touch_x=None, touch_y=None):

        # defining zones
        # #
        (stimulus_center_x, stimulus_center_y) = self.stimulus.center
        x_diff = (stimulus_center_x - touch_x) ** 2
        y_diff = (stimulus_center_y - touch_y) ** 2
        distance_from_stimulus = math.sqrt(x_diff + y_diff)
        correct_radius = (self.stim_size / 2) + (.30 * self.stim_size)
        nothing_happens_radius = (self.stim_size / 2) + (.45 * self.stim_size)
        print("Touch X, Y: "+str(touch_x)+","+str(touch_y))
        print("Center: "+str(self.stimulus.center))
        print("Distance from stim: "+str(distance_from_stimulus))
        # if correct touch
        # #
        if distance_from_stimulus < correct_radius:
            write_ln(self.filepath_to_data, [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'),
                                             self.arm_used, self.task_name, self.trial, self.stim_size,
                                             touch_x, touch_y, self.stim_x, self.stim_y, 1])
            with open(self.filepath_to_progress, 'a') as f:
                f.writelines(str(1) + '\n')
            with open(self.filepath_to_size, 'w') as f:
                f.write(str(self.stim_size))
            self.check_for_progression()
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
            with open(self.filepath_to_size, 'w') as f:
                f.write(str(self.stim_size))
            self.check_for_progression()
            return 'timeout'

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
                trials_to_check_criterion = int(self.m_params[self.monkey_name]['SHAPE2trials'])
                trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['SHAPE2criterion'])
                print("Progression status: "+str(len(progress) >= trials_to_check_criterion)+", "+str(sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion))
                print("NumTrials: "+str(len(progress))+", Sum: "+str(sum(progress[-trials_to_check_criterion:])))
                if (len(progress) >= trials_to_check_criterion) and \
                        (sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion):
                    self.progressed = True
                    with open(filepath_to_task, 'r') as f:
                        current_task = int(f.read())
                    with open(filepath_to_task, 'w') as f:
                        f.write(str(current_task + 1))
                    with open(self.filepath_to_progress, 'w') as f:
                        f.truncate(0)
        
