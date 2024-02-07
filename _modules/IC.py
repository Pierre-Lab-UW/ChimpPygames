"""
Inhibitory control
==
+  what it looks like :: a single clipart on left or right of screen. after learning phase, clipart moves to new quadrant on same side
+  how to win :: touch the clipart
==
As part of monkeys' weekly testing battery Summer2022
"""


from _modules.pgtools import *


class IC(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'IC'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')
        self.filepath_to_learning_trials = os.path.join('_progress', self.monkey_name, 'testing_progress', 'IC-learning-trials-remaining-{}week{}.txt'.format(time.strftime('%Y'), time.strftime('%W')))

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.clipart = clipart

        self.stim_size = 0
        self.stim = None
        self.start_x, self.start_y = (int((self.g_params['SCREEN_W'] - self.stim_size) / 2),
                                      int((self.g_params['SCREEN_H'] - self.stim_size) / 2))
        self.clipart_this_problem = None
        self.positions = {}
        self.pos_this_trial = 0
        self.problem = []

        self.learning_trials = 0
        self.learning_trials_ix = 0
        self.delay_this_trial = 0

        self.presentation_start = 0
        self.delay_start = 0
        self.time_on_presentation = 0
        self.learning_trials_this_problem = 5000
        self.choice_start = 0
        self.time_on_choice_screen = 0

        self.x_touches = []
        self.y_touches = []
        self.timestamps = []

        self.progressed = False
        self.on_start_screen = 'start_screen'

    def prep_new_problem(self):
        self.trial = 0
        # read in list of possible numbers of learning trials, remove empty lines
        # #
        with open(self.filepath_to_learning_trials, 'r') as f:
            self.learning_trials = f.readlines()
        without_blank_lines = []
        for i in self.learning_trials:
            if i != ' \n':
                without_blank_lines.append(i)
        self.learning_trials = without_blank_lines[:]

        self.learning_trials_ix = random.randint(0, len(self.learning_trials) - 1)
        self.learning_trials_this_problem = int(self.learning_trials[self.learning_trials_ix].replace('\n', ''))

        self.clipart_this_problem = random.choice(list(self.clipart.keys()))      # get name of clipart for this trial

        # pos
        # #
        left = int(self.g_params['SCREEN_W'] * .2) - 75
        right = int(self.g_params['SCREEN_W'] * .7) - 75
        top = int((self.g_params['SCREEN_H']) * .15) #.15 for SQM adjusted from .2
        bottom = int(self.g_params['SCREEN_H'] * .55) #.55 for SQM adjusted from .7

        self.positions = {
            'topleft': (left, top),
            'bottomleft': (left, bottom),
            'topright': (right, top),
            'bottomright': (right, bottom)
        }

        starting_pos_this_problem = random.choice(list(self.positions.keys()))
        if starting_pos_this_problem == 'topleft':            self.problem = ['topleft']*self.learning_trials_this_problem + ['bottomleft']
        elif starting_pos_this_problem == 'bottomleft':       self.problem = ['bottomleft']*self.learning_trials_this_problem + ['topleft']
        elif starting_pos_this_problem == 'topright':         self.problem = ['topright']*self.learning_trials_this_problem + ['bottomright']
        elif starting_pos_this_problem == 'bottomright':      self.problem = ['bottomright']*self.learning_trials_this_problem + ['topright']

    def new_trial(self):
        """
        Initiates a new trial
        """

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        # if no datafile exists yet, create one with the column headings
        if not os.path.isfile(self.filepath_to_data):
            write_ln(self.filepath_to_data, ['monkey_name', 'date', 'time', 'arm', 'task_name', 'trial', 
                                             'sample_image', 'correct_x', 'correct_y', 'correct_loc',
                                             'set_type',
                                             'touch_x', 'touch_y', 'timestamp', 'choice_latency', 'test_trial', 'correct'])
        
        # if no testing progress folder exists, make one
        # #
        if not os.path.exists(os.path.join('_progress', self.monkey_name, 'testing_progress')):
            os.makedirs(os.path.join('_progress', self.monkey_name, 'testing_progress'))
            
        # if no list of trials to do exists, make one
        # #
        if not os.path.isfile(self.filepath_to_learning_trials):
            ic_weekly_trials = ['3']*25 + ['6']*25 + ['9']*25
            with open(self.filepath_to_learning_trials, 'w') as f:
                for trial in ic_weekly_trials:
                    f.write(trial + '\n')

        if len(self.problem) == 0 or self.trial == len(self.problem):
            self.prep_new_problem()

        self.stim_size = int(self.m_params[self.monkey_name]['ICsize'])         # get stim_size
        self.pos_this_trial = self.positions[self.problem[self.trial]]
        self.stim = Stimulus(size=self.stim_size, pos=self.pos_this_trial, image=self.clipart[self.clipart_this_problem])
        self.trial += 1  # iterate trial counter
        self.presentation_start = pg.time.get_ticks()
        self.x_touches = []
        self.y_touches = []
        self.timestamps = []
        self.on_start_screen = True

    def on_loop(self):
        if self.on_start_screen:
            Stimulus(size=self.stim_size, pos=(self.screen.rect.centerx-(self.stim_size//2), self.screen.rect.centery-(self.stim_size//2)), image=self.clipart[self.clipart_this_problem]).draw_stimulus(screen=self.screen)
        else:
            if self.trial < len(self.problem)-1 or (pg.time.get_ticks()-self.presentation_start) > 400:
                self.stim.draw_stimulus(screen=self.screen)
            else:
                past_stim = Stimulus(size=self.stim_size, pos=self.positions[self.problem[self.trial-2]], image=self.clipart[self.clipart_this_problem])
                past_stim.draw_stimulus(screen=self.screen)

    def on_touch(self, touch_x=None, touch_y=None):
        if self.on_start_screen:
            if math.sqrt((touch_x - self.screen.rect.centerx) ** 2 + (touch_y - self.screen.rect.centery) ** 2) < self.stim_size // 2:
                self.on_start_screen = False
                self.presentation_start = pg.time.get_ticks()
        else:
            self.x_touches.append(str(touch_x))
            self.y_touches.append(str(touch_y))
            self.timestamps.append(str(int(pg.time.get_ticks()-self.presentation_start)))

            flicker_center = (self.pos_this_trial[0] + self.stim_size // 2, self.pos_this_trial[1] + self.stim_size // 2)
            if math.sqrt((touch_x-flicker_center[0])**2 + (touch_y-flicker_center[1])**2) < self.stim_size//2:
                if pg.time.get_ticks() - self.presentation_start > 100 \
                    and math.sqrt((touch_x-flicker_center[0])**2 + (touch_y-flicker_center[1])**2) < self.stim_size//2:
                    self.time_on_choice_screen = pg.time.get_ticks() - self.presentation_start
                    write_ln(self.filepath_to_data,
                             [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                              self.task_name, self.trial, self.clipart_this_problem, flicker_center[0], flicker_center[1], self.problem[self.trial-1],
                              self.learning_trials_this_problem,
                              '-'.join(self.x_touches), '-'.join(self.y_touches), '-'.join(self.timestamps), self.time_on_choice_screen, len(self.problem)==self.trial, 1])
                    if self.trial == len(self.problem):
                        with open(self.filepath_to_progress, 'a') as f:
                            f.writelines(str(1) + '\n')
                        self.check_for_progression()
                    self.on_start_screen = True
                    return 'ITI'

    def check_for_progression(self):
        """
        Check whether progress amounts to task advancement
        Only progress once per task
        """
        with open(self.filepath_to_learning_trials, 'w') as f:
            for line_ix, line in enumerate(self.learning_trials):
                if line_ix != self.learning_trials_ix and line != '':
                    f.write(line)
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
                trials_to_check_criterion = int(self.m_params[self.monkey_name]['ICtrials'])
                trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['ICcriterion'])
                if (len(progress) >= trials_to_check_criterion) and \
                        (sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion):
                    self.progressed = True
                    with open(filepath_to_task, 'r') as f:
                        current_task = int(f.read())
                    with open(filepath_to_task, 'w') as f:
                        f.write(str(current_task + 1))
                    with open(self.filepath_to_progress, 'w') as f:
                        f.truncate(0)
