"""
CSST
==
+  what it looks like :: array of three clipart in 9 locations. clipart follow shape and color rules
+  how to win :: one rule reinforced at a time, respond according to the active rule
==
As part of monkeys' expanded test battery Spring2023
"""


from _modules.pgtools import *
import itertools

class CSST(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'CSST'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_trial = os.path.join('_progress', self.monkey_name, 'trial_number.txt')
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')
        self.filepath_to_rs = os.path.join('_progress', self.monkey_name, 'CSTTrs.txt')
        self.filepath_to_rule = os.path.join('_progress', self.monkey_name, 'CSTTrule.txt')
        self.filepath_to_lastrule = os.path.join('_progress', self.monkey_name, 'CSTTlastrule.txt')

        self.trial = 0
        self.trial_start = 0
        self.rs = None

        self.colors = ['gold', 'blue', 'pink']
        self.shapes = ['circle', 'triangle', 'splash']
        self.rule = None
        self.lastrule = None

        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.clipart = clipart

        self.stim_size = 150        # get stim_size
        self.grid = {}
        self.progressed = False

    def clear_grid(self):
        xstart = 170
        ystart = 80
        wbuff = 120
        hbuff = 70
        self.grid = {}
        for i, row in enumerate(['u', 'm', 'b']):
            for j, col in enumerate(['l', 'm', 'r']):
                x = xstart + (self.stim_size+wbuff)*j
                y = ystart + (self.stim_size+hbuff)*i
                self.grid[row+col] = {'coords': (x, y)}

    def trialio(self, operation=None):
        if not os.path.isfile(self.filepath_to_trial):
            with open(self.filepath_to_trial, 'w+') as f:
                f.write('0')   # init trial file if there is none
        elif operation == 'reset':
            with open(self.filepath_to_trial, 'w+') as f:
                self.trial = 0
                f.write('0')
        elif operation == 'read':
            with open(self.filepath_to_trial, 'r+') as f:
                self.trial = int(f.read())
        elif operation == 'write':
            with open(self.filepath_to_trial, 'w+') as f:
                f.write(str(self.trial))

    def ruleio(self, operation=None):
        if not os.path.exists(self.filepath_to_rule):
            with open(self.filepath_to_rule, 'w') as f:
                self.rule = random.choice(self.colors+self.shapes)
                f.write(self.rule)
        if not os.path.exists(self.filepath_to_lastrule):
            with open(self.filepath_to_lastrule, 'w') as f:
                f.write('')
        if operation == 'read':
            with open(self.filepath_to_rule, 'r') as f:
                self.rule = f.read()
            with open(self.filepath_to_lastrule, 'r') as f:
                self.lastrule = f.read()
        elif operation == 'reset':
            with open(self.filepath_to_rule, 'w') as f:
                self.lastrule = self.rule
                self.rule = random.choice(self.colors+self.shapes)
                while self.rule == self.lastrule:
                    self.rule = random.choice(self.colors + self.shapes)
                f.write(self.rule)
                with open(self.filepath_to_lastrule, 'w') as f:
                    f.write(self.lastrule)

    def generate_stim(self):
        stim_this_trial = []
        tcolors = self.colors[:]
        tshapes = self.shapes[:]
        for i in range(3):
            color = tcolors.pop(random.randint(0, 2 - i))
            shape = tshapes.pop(random.randint(0, 2 - i))
            prospective_stim = color + '___' + shape
            stim_this_trial.append(prospective_stim)
        return stim_this_trial

    def new_trial(self):
        """
        Initiates a new trial
        """
        self.trialio('read')
        self.clear_grid()

        # if no datafile exists yet, create one with the column headings
        if not os.path.isfile(self.filepath_to_data):
            header = [
                'monkey_name', 'date', 'time', 'arm', 'task_name', 'rule_session', 'trial', 'rule',
                'color_touched', 'shape_touched', 'latency', 'touch_x', 'touch_y', 'correct'
            ]
            write_ln(self.filepath_to_data, header)

        if not os.path.exists(self.filepath_to_rs):
            with open(self.filepath_to_rs, 'w') as f:
                f.write('1')
        with open(self.filepath_to_rs, 'r') as f:
            self.rs = int(f.read())
            if self.rs==0:
                self.rs==1

        self.ruleio('read')
        if self.trial==0:
            if self.rule in self.colors and self.lastrule in self.shapes:
                forbidden = self.rule + '___' + self.lastrule
            elif self.rule in self.shapes and self.lastrule in self.colors:
                forbidden = self.lastrule + '___' + self.rule
            else:
                forbidden = None
        else:
            forbidden = None

        stim_this_trial = self.generate_stim()
        while forbidden in stim_this_trial:
            log('ponderous contingency')
            stim_this_trial = self.generate_stim()

        cells = list(self.grid.keys())
        random.shuffle(cells)
        for i, clipart in enumerate(stim_this_trial):
            key = cells[i]
            pos = self.grid[key]['coords']
            stim = Stimulus(
                size=self.stim_size,
                pos=pos,
                image=self.clipart[clipart+'.jpg']
            )
            self.grid[key]['stim'] = stim
            self.grid[key]['clipart'] = clipart

        self.trial += 1                                                         # iterate trial counter
        self.trial_start = pg.time.get_ticks()

    def on_loop(self):
        for cell in self.grid.keys():
            if 'stim' in self.grid[cell].keys():
                self.grid[cell]['stim'].draw_stimulus(screen=self.screen)
        # if random.random()>.9:            self.new_trial()    # to see grid locations

    def on_touch(self, touch_x=None, touch_y=None):
        for cell in self.grid.keys():
            if 'stim' in self.grid[cell].keys():
                if self.grid[cell]['stim'].rect.contains((touch_x, touch_y, 1, 1)):
                    self.trialio('write')
                    color_touched, shape_touched = self.grid[cell]['clipart'].split('___')
                    latency = pg.time.get_ticks()-self.trial_start
                    if self.rule == color_touched or self.rule == shape_touched:
                        data = [
                            self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                            self.task_name, self.rs, self.trial, self.rule,
                            color_touched, shape_touched, latency, touch_x, touch_y, 1
                        ]
                        write_ln(self.filepath_to_data, data)
                        with open(self.filepath_to_progress, 'a') as f:
                            f.writelines(str(1) + '\n')
                        self.check_for_progression()
                        return 'ITI'
                    else:
                        data = [
                            self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used,
                            self.task_name, self.rs, self.trial, self.rule,
                            color_touched, shape_touched, latency, touch_x, touch_y, 0
                        ]
                        write_ln(self.filepath_to_data, data)
                        with open(self.filepath_to_progress, 'a') as f:
                            f.writelines(str(0) + '\n')
                        self.check_for_progression()
                        return 'timeout'
        return 'running'

    def check_for_progression(self):
        """
        Check whether progress amounts to new rule session or new task
        Only progress once per task
        """
        if not self.progressed:
            filepath_to_task = os.path.join('_progress', self.monkey_name, 'task-ix.txt')
            with open(self.filepath_to_progress, 'r') as f:
                raw_progress = f.readlines()
                progress = []
                for line in raw_progress:
                    try:
                        progress.append(int(line))
                    except:
                        pass   # ignore anything in raw_progress that can't be parsed as int
                trials_to_check_criterion = int(self.m_params[self.monkey_name]['CSSTtrials'])
                trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['CSSTcriterion'])
                if (len(progress) >= trials_to_check_criterion):
                    with open(self.filepath_to_rs, 'w') as f:
                        f.write(str(self.rs + 1))
                        self.rs = self.rs + 1
                    self.trialio('reset')
                    with open(self.filepath_to_progress, 'w') as f:
                        f.truncate(0)
                    if (sum(progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion):
                        self.ruleio('reset')
            if self.rs > int(self.m_params[self.monkey_name]['CSSTsessionsperweek']):
                self.progressed = True
                with open(self.filepath_to_rs, 'w') as f:
                    f.write('0')
                with open(filepath_to_task, 'r') as f:
                    current_task = int(f.read())
                with open(filepath_to_task, 'w') as f:
                    f.write(str(current_task + 1))
                with open(self.filepath_to_progress, 'w') as f:
                    f.truncate(0)
