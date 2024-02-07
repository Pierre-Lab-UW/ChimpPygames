"""
SpatialT
==
+  what it looks like :: array of six identical clipart, one of which blinks during a presentation phase
+  how to win :: correct response is to touch the spatial location that blinked during the presentation phase
==
As part of monkeys' weekly testing battery Fall2021
"""


from _modules.pgtools import *


class Spatialt(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'Spatialt'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')
        self.filepath_to_delay = os.path.join('_progress', self.monkey_name, 'testing_progress', 'Spatialt-delays-remaining-{}week{}.txt'.format(time.strftime('%Y'), time.strftime('%W')))

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.clipart = clipart

        self.stim_size = 0
        self.start_x, self.start_y = (int((self.g_params['SCREEN_W'] - self.stim_size) / 2),
                                      int((self.g_params['SCREEN_H'] - self.stim_size) / 2))
        self.clipart_this_trial = None
        self.flicker = True
        self.flicker_loc = 0

        self.delay_lengths = 0
        self.delay_ix = 0
        self.delay_this_trial = 0

        self.presentation_start = 0
        self.delay_start = 0
        self.time_on_presentation = 0
        self.delay_duration = 5000
        self.choice_start = 0
        self.time_on_choice_screen = 0

        self.pos = 0
        self.progressed = False
        self.stage = 'presentation_screen'

    def new_trial(self):
        """
        Initiates a new trial
        """
        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        # if no datafile exists yet, create one with the column headings
        if not os.path.isfile(self.filepath_to_data):
            write_ln(self.filepath_to_data, ['monkey_name', 'date', 'time', 'arm', 'task_name', 'trial',
                                             'sample_image', 'correct_x', 'correct_y',
                                             'presentation_latency', 'delay_duration', 'choice_latency',
                                             'touch_x', 'touch_y', 'correct'])
        
        # if no testing progress folder exists, make one
        # #
        if not os.path.exists(os.path.join('_progress', self.monkey_name, 'testing_progress')):
            os.makedirs(os.path.join('_progress', self.monkey_name, 'testing_progress'))
            
        # if no list of trials to do exists, make one
        # #
        if not os.path.isfile(self.filepath_to_delay):
            spatialt_weekly_trials = ['0']*100 + ['10']*10 + ['15']*10 + ['30']*10
            with open(self.filepath_to_delay, 'w') as f:
                for trial in spatialt_weekly_trials:
                    f.write(trial + '\n')


        # read in list of possible delay durations, remove empty lines
        # #
        with open(self.filepath_to_delay, 'r') as f:
            self.delay_lengths = f.readlines()
        without_blank_lines = []
        for i in self.delay_lengths:
            if i != ' \n':
                without_blank_lines.append(i)
        self.delay_lengths = without_blank_lines[:]

        self.delay_ix = random.randint(0, len(self.delay_lengths) - 1)
        self.delay_duration = int(self.delay_lengths[self.delay_ix].replace('\n', '')) * 1000

        self.trial += 1                                                         # iterate trial counter
        self.stim_size = int(self.m_params[self.monkey_name]['Spatialtsize'])    # get stim_size
        self.clipart_this_trial = random.choice(list(self.clipart.keys()))      # get name of clipart for this trial
        x_start = int(self.g_params['SCREEN_W'] // 4.5)
        x_buffer = int(self.stim_size * .9)
        y_start = int((self.g_params['SCREEN_H'] - self.stim_size)) // 3
        y_buffer = int(self.stim_size * .8)
        self.pos = [(x, y) for x in [x_start, (x_start + self.stim_size + x_buffer)]
                           for y in [y_start, (y_start + self.stim_size + y_buffer)]]
        self.flicker_loc = random.choice(self.pos)
        self.presentation_start = pg.time.get_ticks()
        self.sample = []
        for pos in self.pos:
            self.sample.append(Stimulus(size=self.stim_size, pos=pos, image=self.clipart[self.clipart_this_trial]))
        self.stage = 'presentation_screen'

    def presentation_screen(self):
        for sample in self.sample:
            sample.draw_stimulus(screen=self.screen)
        time_since_presentation_start = int((pg.time.get_ticks() - self.presentation_start) // 1000)
        if time_since_presentation_start % 2 == 0:
            self.flicker = False
        else:
            self.flicker = True
        x = self.flicker_loc[0]
        y = self.flicker_loc[1]
        if self.flicker:
            pg.draw.rect(self.screen.fg, BLACK, (x, y, self.stim_size, self.stim_size))

    def on_loop(self):
        if self.stage == 'presentation_screen':
            self.presentation_screen()
        elif self.stage == 'delay_screen':
            if pg.time.get_ticks() - self.delay_start > self.delay_duration:
                self.stage = 'choice_screen'
                self.choice_start = pg.time.get_ticks()
        elif self.stage == 'choice_screen':
            for sample in self.sample:
                sample.draw_stimulus(screen=self.screen)

    def on_touch(self, touch_x=None, touch_y=None):
        flicker_center = self.flicker_loc[0] + self.stim_size // 2, self.flicker_loc[1] + self.stim_size // 2
        if self.stage == 'presentation_screen':
            if math.sqrt((touch_x-flicker_center[0])**2 + (touch_y-flicker_center[1])**2) < self.stim_size//2:
                if self.delay_duration > 0:
                    self.stage = 'delay_screen'
                    self.delay_start = pg.time.get_ticks()
                    self.time_on_presentation = pg.time.get_ticks() - self.presentation_start
                else:
                    self.stage = 'choice_screen'
                    self.choice_start = pg.time.get_ticks()
        elif self.stage == 'choice_screen':
            if pg.time.get_ticks() - self.choice_start > 250 \
                and math.sqrt((touch_x-flicker_center[0])**2 + (touch_y-flicker_center[1])**2) < self.stim_size//2:
                self.time_on_choice_screen = pg.time.get_ticks() - self.choice_start
                write_ln(self.filepath_to_data,
                         [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                          self.task_name, self.trial, self.clipart_this_trial, flicker_center[0], flicker_center[1],
                          self.time_on_presentation, self.delay_duration, self.time_on_choice_screen,
                          touch_x, touch_y, 1])
                with open(self.filepath_to_progress, 'a') as f:
                    f.writelines(str(1) + '\n')
                self.check_for_progression()
                return 'ITI'
            elif math.sqrt((touch_x-flicker_center[0])**2 + (touch_y-flicker_center[1])**2) > self.stim_size//2:
                if self.screen.fg.get_at((touch_x, touch_y)) != BLACK:
                    self.time_on_choice_screen = pg.time.get_ticks() - self.choice_start
                    write_ln(self.filepath_to_data,
                             [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                              self.task_name, self.trial, self.clipart_this_trial, flicker_center[0], flicker_center[1],
                              self.time_on_presentation, self.delay_duration, self.time_on_choice_screen,
                              touch_x, touch_y, 0])
                    with open(self.filepath_to_progress, 'a') as f:
                        f.writelines(str(0) + '\n')
                    self.check_for_progression()
                    return 'timeout'

    def check_for_progression(self):
        """
        Check whether progress amounts to task advancement
        Only progress once per task
        """
        with open(self.filepath_to_delay, 'w') as f:
            for line_ix, line in enumerate(self.delay_lengths):
                if line_ix != self.delay_ix and line != '':
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
                trials_to_check_criterion = int(self.m_params[self.monkey_name]['Spatialttrials'])
                trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['Spatialtcriterion'])
                if (len(progress) >= trials_to_check_criterion) and \
                        (sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion):
                    self.progressed = True
                    with open(filepath_to_task, 'r') as f:
                        current_task = int(f.read())
                    with open(filepath_to_task, 'w') as f:
                        f.write(str(current_task + 1))
                    with open(self.filepath_to_progress, 'w') as f:
                        f.truncate(0)
