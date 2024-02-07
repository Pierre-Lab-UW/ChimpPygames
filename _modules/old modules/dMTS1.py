"""
dMTS
==
+  what it looks like :: clipart
+  how to win :: one clipart is the sample, touching it reveals a sample and other clipart.
     correct response is to touch sample again
==
3 MTS trials, then one DMTS trial with 1 second delay. Progress to criterion based on success of DMTS trial
"""


from _modules.pgtools import *


class dMTS1(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'dMTS1'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.clipart = clipart
        self.delay = 1000
        self.trial_style = (['no_delay'] * 3) + ['delay']
        self.trial_style_i = -1

        self.stim_size = 0
        self.sample = None
        self.match = None
        self.nonmatch = None
        self.num_matches = 0
        self.sample_x = 0
        self.sample_y = 0
        self.pos = {'left': (150, 450), 'right': (650, 450)}
        self.sample_i = None
        self.sample_pos = None
        self.nonmatch_clipart = None
        self.nonmatch_pos = None
        self.progressed = False
        self.on_start_screen = True
        self.on_delay_screen = False
        self.delay_timer = 0
        self.recent_pos = []  # to track the recent position of the correct stimuli

    def new_trial(self):
        """
        Initiates a new trial
        """
        self.on_start_screen = True
        self.num_matches = 1
        self.pos = {'left': (150, 450), 'right': (650, 450)}
        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))

        self.trial_style_i += 1   # move to the next trial style (MTS or DMTS). reset to beginning of styles if needed
        if self.trial_style_i >= len(self.trial_style):
            self.trial_style_i = 0

        # if no datafile exists yet, create one with the column headings
        if not os.path.isfile(self.filepath_to_data):
            write_ln(self.filepath_to_data, ['monkey_name', 'date', 'time', 'arm', 'task_name', 'trial',
                                             'trial_style', 'sample_image', 'sample_pos',
                                             'touch_x', 'touch_y', 'correct'])

        self.trial += 1                                                         # iterate trial counter
        self.stim_size = int(self.m_params[self.monkey_name]['dMTSsize'])     # get stim_size
        self.clipart_this_trial = random.choice(list(self.clipart.keys()))      # get name of clipart for this trial
        (self.sample_x, self.sample_y) = (int((self.g_params['SCREEN_W'] - self.stim_size) / 2),
                                          int((self.g_params['SCREEN_H'] - self.stim_size) / 5))
        self.sample = Stimulus(size=self.stim_size, pos=(self.sample_x, self.sample_y),
                               image=self.clipart[self.clipart_this_trial])

    def on_loop(self):
        if self.on_start_screen:
            self.sample.draw_stimulus(screen=self.screen)
        elif self.on_delay_screen:
            self.screen.bg.fill(BLACK)
            self.screen.fg.blit(self.screen.bg, (0, 0))
            pg.event.clear()
            if pg.time.get_ticks() - self.delay_timer > self.delay:
                self.on_delay_screen = False
        else:
            if not self.trial_style[self.trial_style_i] == 'delay':
                self.sample.draw_stimulus(screen=self.screen)
            self.match.draw_stimulus(screen=self.screen)
            self.nonmatch.draw_stimulus(screen=self.screen)

    def on_touch(self, touch_x=None, touch_y=None):
        # start screen
        # #
        if self.on_start_screen:
            if self.sample.rect.contains((touch_x, touch_y, 1, 1)):
                self.on_start_screen = False
                if self.recent_pos[-3:] == ['left', 'left', 'left']:
                    self.sample_pos = 'right'
                    self.nonmatch_pos = 'left'
                    log('sample {} next trial!'.format(self.sample_pos))
                elif self.recent_pos[-3:] == ['right', 'right', 'right']:
                    self.sample_pos = 'left'
                    self.nonmatch_pos = 'right'
                    log('sample {} next trial!'.format(self.sample_pos))
                else:
                    keys = list(self.pos.keys())
                    random.shuffle(keys)
                    self.sample_pos = keys[0]
                    self.nonmatch_pos = keys[1]
                self.recent_pos.append(self.sample_pos)
                #log(str(self.recent_pos[-3:]))
                self.nonmatch_clipart = random.choice(list(self.clipart.keys()))
                while self.nonmatch_clipart == self.clipart_this_trial:
                    self.nonmatch_clipart = random.choice(list(self.clipart.keys()))
                self.match = Stimulus(size=self.stim_size, pos=self.pos[self.sample_pos], image=self.clipart[self.clipart_this_trial])
                self.nonmatch = Stimulus(size=self.stim_size, pos=self.pos[self.nonmatch_pos], image=self.clipart[self.nonmatch_clipart])
                if self.trial_style[self.trial_style_i] == 'delay':
                    self.delay_timer = pg.time.get_ticks()
                    self.on_delay_screen = True
        # match screen
        # #
        else:
            # correct touch
            # #
            if self.match.rect.contains((touch_x, touch_y, 1, 1)):
                write_ln(self.filepath_to_data,
                         [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                          self.task_name, self.trial, self.trial_style[self.trial_style_i],
                          self.clipart_this_trial, self.sample_pos, touch_x, touch_y, 1])
                if self.trial_style[self.trial_style_i] == 'delay':
                    with open(self.filepath_to_progress, 'a') as f:
                        f.writelines(str(1) + '\n')
                self.check_for_progression()
                return 'ITI'
            # incorrect touch
            # #
            elif self.nonmatch.rect.contains((touch_x, touch_y, 1, 1)):
                write_ln(self.filepath_to_data,
                         [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                          self.task_name, self.trial, self.trial_style[self.trial_style_i],
                          self.clipart_this_trial, self.sample_pos, touch_x, touch_y, 0])
                if self.trial_style[self.trial_style_i] == 'delay':
                    with open(self.filepath_to_progress, 'a') as f:
                        f.writelines(str(0) + '\n')
                self.check_for_progression()
                return 'timeout'
            # touched sample, do nothing
            # #
            elif self.sample.rect.contains((touch_x, touch_y, 1, 1)):
                return 'running'

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
                trials_to_check_criterion = int(self.m_params[self.monkey_name]['dMTStrials'])
                trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['dMTScriterion'])
                if (len(progress) >= trials_to_check_criterion) and \
                        (sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion):
                    self.progressed = True
                    with open(filepath_to_task, 'r') as f:
                        current_task = int(f.read())
                    with open(filepath_to_task, 'w') as f:
                        f.write(str(current_task + 1))
                    with open(self.filepath_to_progress, 'w') as f:
                        f.truncate(0)
