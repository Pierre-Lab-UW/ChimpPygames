
"""
ACTS
==
+  frontend for all rhesus programs
+  loads monkey data, task parameters from global_params.txt and primate_params.csv
+  loads monkey progress from, and writes monkey progress to, /_progress
+  imports program data from /_modules
+  writes data to /_data
+  logs errors in /errorlogs
+  Summer2021
==
To add in a new program
  1 ::  write or copy new code into _modules
        ::  new code should have class with same name as script, e.g. MTS.py has class MTS().
             name must follow python naming rules - one word, can't start with number, etc
        ::  init new class with g_params, m_params, screen, clipart
        ::  class should have at least two functions: on_loop and on_touch
        ::  new code can import * from _modules.pgtools to have access to general stuff - sounds, data writing, etc
  2 ::  have new code access params from g_params and m_params. add new columns to primate_params.csv accordingly
        ::  m_params varnames taken from first row, so need to follow python naming rules
"""
from _modules.pgtools import *
import _modules as modules


class FrontEnd(object):
    """
    Runs everything monkey testing
    """

    def __init__(self):

        # READ IN GLOBAL PARAMS
        # #
        g_varnames = ['SCREEN_W', 'SCREEN_H', 'CURSOR_VISIBLE', 'RESTRICT_SCREEN',
                       'AUTOSHAPING', 'TIME_TO_AUTOSHAPE', 'STIMULI_COLORS', 'HOST_CONNECTED',
                       'RFID_READER_CONNECTED', 'DRO_DURATION',
                       'REWARD_TYPE', 'REWARD_AMOUNT', 'DEBUG_WINDOW_ON']
        self.g_params = {}
        with open('global_params.txt', 'r') as f:
            raw = f.readlines()
            varname_ix = 0
            for i, value in enumerate(raw):
                if i % 2 == 1:
                    value = value.replace('\n', '').replace('\r', '')
                    self.g_params[g_varnames[varname_ix]] = value
                    varname_ix += 1
        for int_var in ['SCREEN_W', 'SCREEN_H', 'TIME_TO_AUTOSHAPE', 'DRO_DURATION', 'REWARD_AMOUNT']:
            self.g_params[int_var] = int(self.g_params[int_var])
        for bool_var in ['CURSOR_VISIBLE', 'RESTRICT_SCREEN', 'AUTOSHAPING',
                         'HOST_CONNECTED', 'RFID_READER_CONNECTED', 'DEBUG_WINDOW_ON']:
            if self.g_params[bool_var] == 'True' or self.g_params[bool_var] == 'true':
                self.g_params[bool_var] = True
            if self.g_params[bool_var] == 'False' or self.g_params[bool_var] == 'false':
                self.g_params[bool_var] = False
        

        # READ IN MONKEY PARAMS
        # #
        self.m_params = {}
        with open('primate_params.csv', 'r') as f:
            raw = f.readlines()
            for i, line in enumerate(raw):
                if i == 0:
                    varnames = raw[0].replace('\n', '').replace('\r', '').split(',')[1:]
                else:
                    monkey_name = line.replace('\n', '').replace('\r', '').split(',')[0]
                    values = line.replace('\n', '').replace('\r', '').split(',')[1:]
                    self.m_params[monkey_name] = {}
                    for j, varname in enumerate(varnames):
                        self.m_params[monkey_name][varname] = values[j]
        
        # INSTANTIATE READER AND SCREEN OBJECTS
        # #
        if self.g_params['RFID_READER_CONNECTED']:
            import serial
            self.device = serial.Serial('/dev/serial0', 9600, timeout=1)
        self.screen = Screen(fullscreen=True,
                             size=(self.g_params['SCREEN_W'], self.g_params['SCREEN_H']),
                             color=BLACK)
        if not self.g_params['CURSOR_VISIBLE']:
            pg.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
        log('Screen loaded')

        # DRAW DEBUG WINDOW
        # #
        if self.g_params['DEBUG_WINDOW_ON']:
            self.debug_rect = (0, self.g_params['SCREEN_H'] - .05 * self.g_params['SCREEN_H'],
                          self.g_params['SCREEN_W'], .05 * self.g_params['SCREEN_H'])
            self.debug_bg = Color('black')
            self.debug_fg = Color('DarkSlateGray')

        # TO SEND COMMANDS MANUALLY
        # #
        self.getting_command = False
        self.mutable_text = ''
        self.debug_text = ''

    def get_id(self):
        """
        Get code from tag reader
        """
        read = self.device.read(16)  # Tries to read the ISO tag format made of 15 digits
        converted_read = read.decode().replace('\r', '').replace('\n', '').replace('_', '')
        try:
            log('{} :: {} :: unconverted read: {} :: converted read: {} :: int converted: {}'.
                format(time.strftime('%Y-%m-%d'), time.strftime('%H:%M'), read, converted_read, int(converted_read)))
        except:
            pass
        if len(converted_read) > 2:
            try:
                return converted_read
            except:
                return None

    def get_command(self, event=None):
        """
        Interpret keystrokes as text string, send valid string to process_command
        K_RETURN to begin and end string
        """
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                self.getting_command = not self.getting_command
                if not self.getting_command:
                    self.mutable_text = self.debug_text = ''
            elif self.getting_command:
                self.mutable_text += event.unicode
                self.debug_text = self.mutable_text

    def main(self):

        # INIT READER VARS
        # #
        monkey_name = None
        active_monkey = False
        experiment = None
        tag = None
        if not self.g_params['RFID_READER_CONNECTED']:
            tag = 999999999999999

        # LOAD CLIPART
        # #
        load_start = pg.time.get_ticks()
        clipart = {}
        for image in glob.glob(os.path.join('_modules', '_clipart', '*.jpg')):
            clipart[os.path.basename(image)] = pg.transform.scale(pg.image.load(image), (200, 200))
            pg.draw.rect(self.screen.fg, Color('black'), (300, 300, 400, 75))
            self.screen.fg.blit(big_font.render('{} clipart loaded'.format(len(clipart)), False, Color('salmon')),
                                (300, 300))
            pg.display.update((300, 300, 400, 75))
            if len(clipart)>CLIPART_TO_LOAD:   
                break
        log('{} clipart loaded in {} seconds'.format(len(clipart), (pg.time.get_ticks() - load_start) / 1000))

        # LOGGING
        # #
        errorlog_name = '{}-week{}-errorlog.txt'.format(system_name, time.strftime('%W'))
        if not os.path.exists(os.path.join(HOSTROOT, 'errorlogs', errorlog_name)):
            with open(os.path.join(HOSTROOT, 'errorlogs', errorlog_name), 'w') as f:
                f.write('\n ~@~@~@~@~@~@~@~@~ START OF ERRORLOG FOR {0} ~@~@~@~@~@~@~@~@~'.format(TODAY))
        logger = logging.getLogger('')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(os.path.join(HOSTROOT, 'errorlogs', errorlog_name))
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)
        
        log('Loaded global params ::')
        for k, v in self.g_params.items():
            log('{} :: {}'.format(k, v))
        log('Loaded primate params')
        log(self.m_params)

        # MAKE ANY AMERICAN MONKEY CHANGES
        # #
        if self.g_params['STIMULI_COLORS'] != 'normal':
            CORRECT_COLOR = BLUE
            INCORRECT_COLOR = YELLOW



        # PROGRAM TIMING
        # #
        time_since_reset = pg.time.get_ticks()
        time_since_autoshape = pg.time.get_ticks()
        time_to_reset = 60000
        status = 'running'
        clock = pg.time.Clock()
        error_starting_program = False
        done = False

        # GAMELOOP
        # #
        while not done:

            today = time.strftime('%Y-%m-%d')
            week = time.strftime('%W')

            # update logger if week changes
            # #
            errorlog_name = '{}-week{}-errorlog.txt'.format(system_name, time.strftime('%W'))
            if not os.path.exists(os.path.join(HOSTROOT, 'errorlogs', errorlog_name)):
                with open(os.path.join(HOSTROOT, 'errorlogs', errorlog_name), 'w') as f:
                    f.write('\n ~@~@~@~@~@~@~@~@~ START OF ERRORLOG FOR {0} ~@~@~@~@~@~@~@~@~'.format(TODAY))
                    logger = logging.getLogger('')
                    logger.setLevel(logging.DEBUG)
                    fh = logging.FileHandler(os.path.join(HOSTROOT, 'errorlogs', errorlog_name))
                    fh.setLevel(logging.INFO)
                    logger.addHandler(fh)

            # draw background and debug window
            # #
            self.screen.fg.blit(self.screen.bg, (0, 0))
            pg.draw.rect(self.screen.fg, self.debug_bg, self.debug_rect)

            # reset program on inactivity
            # #
            if self.g_params['RFID_READER_CONNECTED'] and (pg.time.get_ticks() - time_since_reset > time_to_reset):
                time_since_reset = pg.time.get_ticks()
                active_monkey = False
                monkey_name = None

            # autoshape if monkeys aren't working and it's daytime
            # #
            needs_shaping = pg.time.get_ticks() - self.g_params['TIME_TO_AUTOSHAPE']*60*1000 > time_since_autoshape
            after_8am = int(time.strftime('%H')) >= 8
            before_4pm = int(time.strftime('%H')) < 16
            if needs_shaping and after_8am and before_4pm:
                active_monkey = False
                monkey_name = None
                autoshape_datafile = os.path.join(HOSTROOT, 'data', 'autoshaping_' + system_name + '.csv')
                write_ln(autoshape_datafile, [today, time.strftime('%H:%M')])
                for i, color in enumerate(['cyan', 'black'] * 2):
                    sound(correct=True, soundplayer='old')
                    self.screen.bg.fill(Color(color))
                    self.screen.fg.blit(self.screen.bg, (0, 0))
                    pg.display.update()
                    time.sleep(.3)
                pellet()
                time_since_reset = pg.time.get_ticks()
                time_since_autoshape = pg.time.get_ticks()
                if not self.g_params['RFID_READER_CONNECTED']:
                    tag = 999999999999999

            # RFID/menu logic
            # #
            # every frame, see which tag is around and which monkey it belongs to
            if self.g_params['RFID_READER_CONNECTED']:
                tag = self.get_id()
                if tag is not None:
                    tag = str(int(tag))
                    monkey_name = None
                    arm_used = None
                    for key in self.m_params.keys():
                        if tag == self.m_params[key]['Left Wrist']:
                            monkey_name = key
                            arm_used = 'L'
                            break
                        elif tag == self.m_params[key]['Right Wrist']:
                            monkey_name = key
                            arm_used = 'R'
                            break
            else:
                for key in self.m_params.keys():
                    if self.mutable_text == key:
                        self.mutable_text = self.debug_text = ''
                        monkey_name = key
                        arm_used = 'NA'
                        break

            # start a program
            # #
            #  if no monkey program is already running but a tag was found,
            #    or if a different tag was read than that of the active monkey,
            #    or if the currently-working monkey has progressed to a new task
            monkey_enters_anew = not active_monkey and monkey_name is not None
            new_monkey_takes_over = monkey_name is not None and monkey_name != active_monkey
            should_progress = experiment.progressed if experiment is not None else False

            if (monkey_enters_anew or new_monkey_takes_over or should_progress) and monkey_name is not None:
                if monkey_enters_anew or new_monkey_takes_over:
                    active_monkey = monkey_name
                try:
                    self.screen.bg.fill(BLACK)
                    self.screen.fg.blit(self.screen.bg, (0, 0))
                    with open(os.path.join('_progress', active_monkey, 'task-ix.txt'), 'r') as f:
                        line = f.readline()
                        task_ix = int(line.replace('\n', '').replace('\r', ''))
                    task_order = self.m_params[active_monkey]['task-order'].split('-')
                    task_to_load = task_order[task_ix]
                    experiment = eval('modules.{}.{}(screen=self.screen, monkey_name=active_monkey, g_params=self.g_params, m_params=self.m_params, arm_used=arm_used, clipart=clipart)'.
                                        format(task_to_load, task_to_load))
                    experiment.new_trial()
                except:
                    log('Error starting program for {}'.format(active_monkey))
                    logging.exception('')
                    experiment = None
                    active_monkey = False
                    error_starting_program = True

            # run any code that should happen on every iteration of the game loop
            # #
            if experiment is not None:
                experiment.on_loop()

            # read touches
            # #
            # if program is running, check and process touches
            # #
            if status not in ['ITI', 'timeout', 'buffer']:
                for event in pg.event.get():
                    check_quit(event=event)
                    self.get_command(event=event)
                    if event.type == MOUSEBUTTONDOWN and experiment is not None:
                        touch_x, touch_y = event.pos
                        time_since_reset = pg.time.get_ticks()
                        time_since_autoshape = pg.time.get_ticks()
                        status = experiment.on_touch(touch_x=touch_x, touch_y=touch_y)
                        if status in ['ITI', 'timeout']:
                            outcome_timer = pg.time.get_ticks()
                        if status in ['ITI']:
                            sounds['correct'].play()
                            for i in range(self.g_params['REWARD_AMOUNT']):
                                if self.g_params['REWARD_TYPE'] != 'pellet':
                                    pellet(time_to_close_relay=1.25)
                                else:
                                    pellet()
                        if status in ['timeout']:
                            sounds['incorrect'].play()
                        pg.event.clear()
                        break
                    
            # on correct touch
            # #
            elif status == 'ITI':
                self.screen.bg.fill(CORRECT_COLOR)
                self.screen.fg.blit(self.screen.bg, (0, 0))
                if pg.time.get_ticks() - outcome_timer > experiment.ITI:
                    status = 'buffer'
                    outcome_timer = pg.time.get_ticks()
            # on incorrect touch
            # #
            elif status == 'timeout':
                self.screen.bg.fill(INCORRECT_COLOR)
                self.screen.fg.blit(self.screen.bg, (0, 0))
                if pg.time.get_ticks() - outcome_timer > experiment.timeout:
                    status = 'buffer'
                    outcome_timer = pg.time.get_ticks()
            # after either correct or incorrect touch
            # #
            elif status == 'buffer':
                self.screen.bg.fill(BUFFER_COLOR)
                self.screen.fg.blit(self.screen.bg, (0, 0))
                for event in pg.event.get([QUIT, KEYDOWN, MOUSEBUTTONDOWN]):
                    check_quit(event=event)
                    if event.type == MOUSEBUTTONDOWN and experiment is not None:
                        outcome_timer = pg.time.get_ticks()
                if pg.time.get_ticks() - outcome_timer > self.g_params['DRO_DURATION']*1000:
                    status = 'running'
                    experiment.new_trial()

            if not active_monkey and status == 'running':
                if not error_starting_program:
                    self.screen.bg.fill(Color('green'))
                elif error_starting_program:
                    self.screen.bg.fill(Color('darkorchid'))
                self.screen.fg.blit(self.screen.bg, (0, 0))

            if not self.g_params['RFID_READER_CONNECTED']:
                tag = None  # reset tag to None to simulate monkey steadily in holster for debugging

            # output things to researcher in debug window
            if self.g_params['DEBUG_WINDOW_ON']:
                pg.draw.rect(self.screen.fg, (0, 0, 0), (0, 0, self.g_params['SCREEN_W'], 50))

                running = random.choice(['going', 'running', 'chugging along', 'doing my best',
                                         'persevering', 'working', 'killing it', 'rolling right along',
                                         'rocking and rolling', '100'])
                if self.g_params['RFID_READER_CONNECTED']:
                    if tag is not None:
                        if len(tag) < 15:
                            self.screen.fg.blit(sm_font.render('RFID ERROR: {}'.format(tag), False, Color('salmon')), (5, 5))
                        else:
                            self.screen.fg.blit(sm_font.render(tag, False, Color('salmon')), (5, 5))
                    else:
                        self.screen.fg.blit(sm_font.render('No tag but still {}'.format(running), False, Color('salmon')), (5, 5))

                    if monkey_name is not None:
                        self.screen.fg.blit(sm_font.render(monkey_name, False, Color('salmon')), (5, 25))
                    else:
                        self.screen.fg.blit(sm_font.render('RFID ERROR: {}'.format(tag), False, Color('salmon')), (5, 25))
                else:
                    self.screen.fg.blit(sm_font.render(self.debug_text, True, Color('salmon')), (5, 5))
            pg.display.update()
            clock.tick(FPS)


# START PROGRAM
# # #
if __name__ == '__main__':

    try:
        frontend = FrontEnd()
        frontend.main()

    except:
        logging.exception('')
        log('')
        sys.exit()
