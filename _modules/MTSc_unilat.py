"""
MTSc_unilat
==
+  what it looks like :: clipart
+  how to win :: one clipart is the sample, touching it reveals a sample and other clipart.
     correct response is to touch sample again (match and non match are presented near middle of screen in top and
     bottom, rather than left/right orientation). Includes a correction procedure, if they get it wrong they get the
     same pair of stimuli in the same locations until they get it correct.
==
As part of monkeys' initial training battery
"""


from _modules.pgtools import *


class MTSc_unilat(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'MTSc_unilat'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')
        self.filepath_to_side = os.path.join('_progress', self.monkey_name, 'side_tracking.txt')

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
        self.pos = {'top': (512, 100), 'bottom': (512, 472)}
        self.sample_i = None
        self.sample_pos = None
        self.nonmatch_clipart = None
        self.nonmatch_pos = None
        self.progressed = False
        self.on_start_screen = True
        self.recent_pos = []          # to track the recent position of the correct stimuli
        self.last_trial_correct = True

    def new_trial(self):
        """
        Initiates a new trial
        """
        self.num_matches = 1
        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))

        # if no datafile exists yet, create one with the column headings
        if not os.path.isfile(self.filepath_to_data):
            write_ln(self.filepath_to_data, ['monkey_name', 'date', 'time', 'arm', 'task_name', 'trial',
                                             'sample_image', 'touch_x', 'touch_y', 'correct', 'sample_pos'])

        self.trial += 1                                                         # iterate trial counter
        (self.sample_x, self.sample_y) = (200, 300)

        self.pos = {'top': (512, 100), 'bottom': (512, 472)}

        if self.trial==1 or (self.last_trial_correct): # and self.m_params[self.monkey_name]['MTSCorrectionTrials']=='TRUE'):
            self.clipart_this_trial = random.choice(list(self.clipart.keys()))      # get name of clipart for this trial
            self.stim_size = int(self.m_params[self.monkey_name]['MTS_unilatsize'])        # get stim_size
            self.sample = Stimulus(size=self.stim_size, pos=(self.sample_x, self.sample_y),
                                   image=self.clipart[self.clipart_this_trial])
            if len(set(self.recent_pos)) == 1:# and self.m_params[self.monkey_name]['MTSCorrectionTrials']!='TRUE':
                nonduplicate = list(self.pos.keys())
                nonduplicate.remove(self.recent_pos[0])
                self.sample_pos = nonduplicate[0]
                self.nonmatch_pos = self.recent_pos[0]
            else:
                keys = list(self.pos.keys())
                random.shuffle(keys)
                self.sample_pos = keys[0]
                self.nonmatch_pos = keys[1]
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

    def manage_recent_pos(self):
        # with open(self.filepath_to_side, 'a') as f:
        #      f.writelines(self.sample_pos + '\n')
        with open(self.filepath_to_side, 'r') as f:
            self.recent_pos = f.readlines()[-3:]
            self.recent_pos = [pos.strip('\n') for pos in self.recent_pos]
        print(self.recent_pos)

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
                with open(self.filepath_to_side, 'a') as f:
                    f.writelines(self.sample_pos + '\n')
                self.manage_recent_pos()
                return 'ITI'
            elif self.nonmatch.rect.contains((touch_x, touch_y, 1, 1)):
                write_ln(self.filepath_to_data,
                         [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                          self.task_name, self.trial, self.clipart_this_trial, touch_x, touch_y, 0, self.sample_pos])
                with open(self.filepath_to_progress, 'a') as f:
                    f.writelines(str(0) + '\n')
                self.last_trial_correct = False
                self.check_for_progression()
                # with open(self.filepath_to_side, 'a') as f:
                #     f.writelines(self.sample_pos + '\n')
                self.manage_recent_pos()
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
                    with open(self.filepath_to_side, 'w') as f:
                        f.truncate(0)