"""
MTSc
==
+  what it looks like :: clipart
+  how to win :: one clipart is the sample, touching it reveals a sample and other clipart.
     correct response is to touch sample again
==
As part of monkeys' initial training battery Summer2021
"""


from _modules.pgtools import *


class MTSc(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'MTSc'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.clipart = clipart

        self.stim_size = 0
        self.sample = None
        self.match = None
        self.nonmatch = None
        self.num_matches = 0
        self.sample_x = 0
        self.sample_y = 0
        self.pos = {'left': (175, 450), 'right': (625, 450)}
        self.sample_i = None
        self.sample_pos = None
        self.nonmatch_clipart = None
        self.nonmatch_pos = None
        self.progressed = False
        self.on_start_screen = True
        self.recent_pos = []          #to track the recent position of the correct stimuli
        self.last_trial_correct = True

    def new_trial(self):
        """
        Initiates a new trial
        """
        self.num_matches = 1
        self.pos = {'left': (175, 450), 'right': (625, 450)}
        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))

        # if no datafile exists yet, create one with the column headings
        if not os.path.isfile(self.filepath_to_data):
            write_ln(self.filepath_to_data, ['monkey_name', 'date', 'time', 'arm', 'task_name', 'trial',
                                             'sample_image', 'touch_x', 'touch_y', 'correct', 'sample_pos'])

        self.trial += 1                                                         # iterate trial counter
        (self.sample_x, self.sample_y) = (int((self.g_params['SCREEN_W'] - self.stim_size) / 2),
                                          int((self.g_params['SCREEN_H'] - self.stim_size) / 5))

        if self.trial==1 or (self.last_trial_correct and self.m_params[self.monkey_name]['MTSCorrectionTrials']=='TRUE'):
            self.clipart_this_trial = random.choice(list(self.clipart.keys()))      # get name of clipart for this trial
            self.stim_size = int(self.m_params[self.monkey_name]['MTSsize'])        # get stim_size
            self.sample = Stimulus(size=self.stim_size, pos=(self.sample_x, self.sample_y),
                                   image=self.clipart[self.clipart_this_trial])
            if self.recent_pos[-3:] == ['left', 'left', 'left'] and self.m_params[self.monkey_name]['MTSCorrectionTrials']!='TRUE':
                self.sample_pos = 'right'
                self.nonmatch_pos = 'left'
            elif self.recent_pos[-3:] == ['right', 'right', 'right'] and self.m_params[self.monkey_name]['MTSCorrectionTrials']!='TRUE':
                self.sample_pos = 'left'
                self.nonmatch_pos = 'right'
            else:
                keys = list(self.pos.keys())
                random.shuffle(keys)
                self.sample_pos = keys[0]
                self.nonmatch_pos = keys[1]
            self.recent_pos.append(self.sample_pos)
            self.nonmatch_clipart = random.choice(list(self.clipart.keys()))
            while self.nonmatch_clipart == self.clipart_this_trial:
                self.nonmatch_clipart = random.choice(list(self.clipart.keys()))
            self.match = Stimulus(size=self.stim_size, pos=self.pos[self.sample_pos],
                                  image=self.clipart[self.clipart_this_trial])
            self.nonmatch = Stimulus(size=self.stim_size, pos=self.pos[self.nonmatch_pos],
                                     image=self.clipart[self.nonmatch_clipart])
        self.on_start_screen = True

    def on_loop(self):
        if self.on_start_screen:
            self.sample.draw_stimulus(screen=self.screen)
        if not self.on_start_screen:
            self.sample.draw_stimulus(screen=self.screen)
            self.match.draw_stimulus(screen=self.screen)
            self.nonmatch.draw_stimulus(screen=self.screen)

    def on_touch(self, touch_x=None, touch_y=None):
        if self.on_start_screen:
            if self.sample.rect.contains((touch_x, touch_y, 1, 1)):
                self.on_start_screen = False

        else:
            if self.match.rect.contains((touch_x, touch_y, 1, 1)):
                write_ln(self.filepath_to_data,
                         [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                          self.task_name, self.trial, self.clipart_this_trial, touch_x, touch_y, 1, self.sample_pos])
                with open(self.filepath_to_progress, 'a') as f:
                    f.writelines(str(1) + '\n')
                self.last_trial_correct = True
                self.check_for_progression()
                return 'ITI'
            elif self.nonmatch.rect.contains((touch_x, touch_y, 1, 1)):
                write_ln(self.filepath_to_data,
                         [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                          self.task_name, self.trial, self.clipart_this_trial, touch_x, touch_y, 0, self.sample_pos])
                with open(self.filepath_to_progress, 'a') as f:
                    f.writelines(str(0) + '\n')
                self.last_trial_correct = False
                self.check_for_progression()
                return 'timeout'
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
                trials_to_check_criterion = int(self.m_params[self.monkey_name]['MTStrials'])
                trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['MTScriterion'])
                if (len(progress) >= trials_to_check_criterion) and \
                        (sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion):
                    self.progressed = True
                    with open(filepath_to_task, 'r') as f:
                        current_task = int(f.read())
                    with open(filepath_to_task, 'w') as f:
                        f.write(str(current_task + 1))
                    with open(self.filepath_to_progress, 'w') as f:
                        f.truncate(0)
