"""
TwoChoice-testing
==
+  what it looks like :: two clipart images
+  how to win :: touch one of the two images (which image must be learned by trial-and-error for each problem)
==
As part of monkeys' initial training battery Summer2021
"""


from _modules.pgtools import *


class TCDt(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):

        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'TCDt'
        self.monkey_name = monkey_name
        self.arm_used = arm_used

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name, time.strftime('%Y-%m-%d'), self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')

        self.trial = 0
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])
        self.timeout = int(self.m_params[self.monkey_name]['Timeout'])
        self.clipart = clipart
        self.stim_size = 0

        self.posX = None
        self.posY = None
        self.negX = None
        self.negY = None
        self.posImage = None
        self.negImage = None

        self.set = 0
        self.set_progress = []
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
                      'trial', 'set', 'posImage', 'negImage', 'touch_x',
                      'touch_y', 'pos_x', 'pos_y', 'neg_x', 'neg_y', 'correct'])

        # get which set and stimuli we're on
        with open(os.path.join('_progress', self.monkey_name, 'set-ix.txt'), 'r') as f:
            self.set = int(f.read())

        # if lots of time has elapsed since last 2Choice trial, reset everything
        # #
        with open(os.path.join('_progress', self.monkey_name, 'set-timestamp.txt'), 'r') as f:
            try:
                timestamp = float(f.read())
            except ValueError:
                timestamp = 0

        if (time.time() - timestamp) > (int(self.m_params[self.monkey_name]['2choicereset'])):
            # get new images for new set
            self.posImage = random.choice(list(self.clipart.keys()))
            self.negImage = random.choice(list(self.clipart.keys()))
            while self.posImage == self.negImage:
                self.posImage = random.choice(list(self.clipart.keys()))
                self.negImage = random.choice(list(self.clipart.keys()))
            with open(os.path.join('_progress', self.monkey_name, 'set-pos.txt'), 'w') as f:
                f.write(str(self.posImage))
            with open(os.path.join('_progress', self.monkey_name, 'set-neg.txt'), 'w') as f:
                f.write(str(self.negImage))
            # clear accumulated progress
            with open(self.filepath_to_progress, 'w') as f:
                f.truncate(0)
            self.set_progress = []

        # else load it from disk
        # #
        else:
            with open(os.path.join('_progress', self.monkey_name, 'set-pos.txt'), 'r') as f:
                self.posImage = f.read()
            with open(os.path.join('_progress', self.monkey_name, 'set-neg.txt'), 'r') as f:
                self.negImage = f.read()

            # get accumulated progress
            with open(os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt'), 'r') as f:
                self.set_progress = f.readlines()
            _ = []
            for i in self.set_progress:
                _.append(int(i))
            self.set_progress = _[:]

        # if enough trials have been done to check for criterion, and animal has met criterion
        # #
        trials_to_check_criterion = int(self.m_params[self.monkey_name]['TCDttrials'])
        trials_to_achieve_criterion = int(self.m_params[self.monkey_name]['TCDtcorrect'])
        if len(self.set_progress) >= trials_to_check_criterion and \
                sum(self.set_progress[-trials_to_check_criterion:]) >= trials_to_achieve_criterion:
            # write set advancement
            with open(os.path.join('_progress', self.monkey_name, 'set-ix.txt'), 'w') as f:
                f.write(str(self.set + 1))
                self.set += 1
            # clear accumulated progress
            with open(self.filepath_to_progress, 'w') as f:
                f.truncate(0)
                self.set_progress = []
            # get new images for new set
            self.posImage = random.choice(list(self.clipart.keys()))
            self.negImage = random.choice(list(self.clipart.keys()))
            while self.posImage == self.negImage:
                self.posImage = random.choice(list(self.clipart.keys()))
                self.negImage = random.choice(list(self.clipart.keys()))
            with open(os.path.join('_progress', self.monkey_name, 'set-pos.txt'), 'w') as f:
                f.write(str(self.posImage))
            with open(os.path.join('_progress', self.monkey_name, 'set-neg.txt'), 'w') as f:
                f.write(str(self.negImage))

        self.trial += 1                                                         # iterate trial counter
        self.stim_size = int(self.m_params[self.monkey_name]['2choicesize'])    # get stim_size

        while True:
            if self.g_params['RESTRICT_SCREEN']:
                (self.posX, self.posY) = (random.randint(int(self.g_params['SCREEN_W'] * .15),
                                                         int(self.g_params['SCREEN_W'] * .85) - self.stim_size),
                                          random.randint(int(self.g_params['SCREEN_H'] * .15) + 50,
                                                         self.g_params['SCREEN_H'] - self.stim_size))
                (self.negX, self.negY) = (random.randint(int(self.g_params['SCREEN_W'] * .15),
                                                         int(self.g_params['SCREEN_W'] * .85) - self.stim_size),
                                          random.randint(int(self.g_params['SCREEN_H'] * .15) + 50,
                                                         self.g_params['SCREEN_H'] - self.stim_size))
            else:
                (self.posX, self.posY) = (random.randint(0, (self.g_params['SCREEN_W'] - self.stim_size)),
                                          random.randint(0, (self.g_params['SCREEN_H'] - self.stim_size)))
                (self.negX, self.negY) = (random.randint(0, (self.g_params['SCREEN_W'] - self.stim_size)),
                                          random.randint(0, (self.g_params['SCREEN_H'] - self.stim_size)))
            self.posStim = Stimulus(size=self.stim_size, pos=(self.posX, self.posY), image=self.clipart[self.posImage])
            self.negStim = Stimulus(size=self.stim_size, pos=(self.negX, self.negY), image=self.clipart[self.negImage])

            if self.posStim.rect.colliderect(self.negStim) or math.sqrt((self.posX - self.negX)**2 + (self.posY - self.negY)**2) < 500:
                continue
            else:
                break

    def on_loop(self):
        self.posStim.draw_stimulus(screen=self.screen)
        self.negStim.draw_stimulus(screen=self.screen)

    def on_touch(self, touch_x=None, touch_y=None):
        if self.posStim.rect.contains((touch_x, touch_y, 1, 1)):
            write_ln(self.filepath_to_data, [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used, self.task_name, self.trial, self.set, self.posImage, self.negImage, touch_x, touch_y, self.posX, self.posY, self.negX, self.negY, 1])
            self.set_progress.append(1)
            with open(self.filepath_to_progress, 'a') as f:
                f.writelines(str(1) + '\n')
            self.check_for_progression()
            return 'ITI'

        elif self.negStim.rect.contains((touch_x, touch_y, 1, 1)):
            write_ln(self.filepath_to_data, [self.monkey_name, time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), self.arm_used, self.task_name, self.trial, self.set, self.posImage, self.negImage, touch_x, touch_y, self.posX, self.posY, self.negX, self.negY, 0])
            self.set_progress.append(0)
            with open(self.filepath_to_progress, 'a') as f:
                f.writelines(str(0) + '\n')
            self.check_for_progression()
            return 'timeout'

    def check_for_progression(self):
        """
        Check whether progress amounts to task advancement
        Only progress once per task
        """
        if (not self.progressed) and (self.set > int(self.m_params[self.monkey_name]['TCDtproblems'])):
            filepath_to_task = os.path.join('_progress', self.monkey_name, 'task-ix.txt')
            self.progressed = True
            with open(filepath_to_task, 'r') as f:
                current_task = int(f.read())
            with open(filepath_to_task, 'w') as f:
                f.write(str(current_task + 1))
            with open(self.filepath_to_progress, 'w') as f:
                f.truncate(0)

        # create timestamp for last set that was completed
        with open(os.path.join('_progress', self.monkey_name, 'set-timestamp.txt'), 'w') as f:
            f.write(str(time.time()))


if __name__ == '__main__':
    # TODO :: this. it would be great if programs could stand alone. Should progression still work?

    screen = Screen(fullscreen=True, size=(1024, 768), color=BLACK)

    # LOAD CLIPART
    # #
    load_start = pg.time.get_ticks()
    clipart = {}
    for image in glob.glob(os.path.join('_clipart', '*.jpg')):
        clipart[os.path.basename(image)] = pg.transform.scale(pg.image.load(image), (200, 200))
        pg.draw.rect(screen.fg, Color('black'), (300, 300, 400, 75))
        screen.fg.blit(big_font.render('{} clipart loaded'.format(len(clipart)), False, Color('salmon')), (300, 300))
        pg.display.update((300, 300, 400, 75))
    log('{} clipart loaded in {} seconds'.format(len(clipart), (pg.time.get_ticks() - load_start) / 1000))

    # LOAD PROGRAM PARAMETERS
    # #


    # GAMELOOP
    # #
    done = False
    while not done:
        today = time.strftime('%Y-%m-%d')

        # draw background
        # #
        screen.fg.blit(screen.bg, (0, 0))

