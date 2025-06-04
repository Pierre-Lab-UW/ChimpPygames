
"""
ACTS
==
+  frontend for all programs
+  loads primate data, task parameters from global_params.txt and primate_params.csv
+  loads primate progress from, and writes monkey progress to, /_progress
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
        ::  new code can import * from _modules.pgtools to have access to general stuff - #sounds, data writing, etc
  2 ::  have new code access params from g_params and m_params. add new columns to primate_params.csv accordingly
        ::  m_params varnames taken from first row, so need to follow python naming rules
"""
import subprocess
from _modules.pgtools import *
import _modules as modules
import io
import os

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: 
        return False
    return False

if not is_raspberrypi():
    from color_based_detection import *

class FrontEnd(object):
    """
    Runs everything primate testing
    """

    def __init__(self):

        # READ IN GLOBAL PARAMS
        # #
        g_varnames = ['SCREEN_W', 'SCREEN_H', 'CURSOR_VISIBLE', 'RESTRICT_SCREEN',
                       'AUTOSHAPING', 'TIME_TO_AUTOSHAPE', 'STIMULI_COLORS', 'HOST_CONNECTED',
                       'RFID_READER_CONNECTED', 'DRO_DURATION',
                       'REWARD_TYPE', 'REWARD_AMOUNT', 'DEBUG_WINDOW_ON', 'TIME_TO_RESET', 'DO_NOT_DISTURB']
        self.g_params = {}
        with open('global_params.txt', 'r') as f:
            raw = f.readlines()
            varname_ix = 0
            for i, value in enumerate(raw):
                if i % 2 == 1:
                    value = value.replace('\n', '').replace('\r', '')
                    self.g_params[g_varnames[varname_ix]] = value
                    varname_ix += 1
        for int_var in ['SCREEN_W', 'SCREEN_H', 'TIME_TO_AUTOSHAPE', 'DRO_DURATION', 'REWARD_AMOUNT', 'TIME_TO_RESET']:
            self.g_params[int_var] = int(self.g_params[int_var])
        for bool_var in ['CURSOR_VISIBLE', 'RESTRICT_SCREEN', 'AUTOSHAPING',
                         'HOST_CONNECTED', 'RFID_READER_CONNECTED', 'DEBUG_WINDOW_ON', 'DO_NOT_DISTURB']:
            if self.g_params[bool_var] == 'True' or self.g_params[bool_var] == 'true':
                self.g_params[bool_var] = True
            if self.g_params[bool_var] == 'False' or self.g_params[bool_var] == 'false':
                self.g_params[bool_var] = False

        self.m_params = {}

        # READ IN AUTOSHAPE PARAMS
        # #
        self.a_params = {}
        with open('autoshaping.csv', 'r') as f:
            raw = f.readlines()
            for i, line in enumerate(raw):
                system = line.replace('\n', '').replace('\r', '').split(',')[0]
                time_to_autoshape = line.replace('\n', '').replace('\r', '').split(',')[2]
                self.a_params[system] = time_to_autoshape
        try:
            self.a_params[system_name]   # tests whether system_name in autoshape params
        except:
            log('system name [{}] not in autoshaping.csv'.format(system_name))   # log error if not

        self.device = None
        self.screen = Screen(fullscreen=True,
                             size=(self.g_params['SCREEN_W'], self.g_params['SCREEN_H']),
                             color=BLACK)
        if not self.g_params['CURSOR_VISIBLE']:
            pg.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))

        # DRAW DEBUG WINDOW
        # #
        # if self.g_params['DEBUG_WINDOW_ON']:
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
        try:
            converted_read = read.decode().replace('\r', '').replace('\n', '').replace('_', '')
            try:
                log('{} :: {} :: unconverted read: {} :: converted read: {} :: int converted: {}'.
                    format(time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S'), read, converted_read, int(converted_read)))
            except:
                pass
            if len(converted_read) > 2:
                try:
                    return converted_read
                except:
                    return None
        except:
            return 'read_error'

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

    def determine_task_order(self, active_monkey=None):
        """
        task order depends on whether an animal is trained or not
          + if animal is not trained, they use the default task-order
          + if animal is trained, derive task order from week #
        """
        if self.m_params[active_monkey]['Testing'] != '1':
            task_order = self.m_params[active_monkey]['task-order'].split('-')
        else:
            week_ix = 6 - (int(time.strftime('%W')) % 6)
            task_order = self.m_params[active_monkey]['TestOrder{}'.format(week_ix)].split('-')
        return task_order

    def autoshape(self, time_since_autoshape=None, today=None, week=None, correct_color='cyan'):
        """
        Autoshape if animals aren't working and it's daytime
        """
        try:
            time_to_autoshape = int(self.a_params[system_name]) * 60 * 1000
        except:
            #Error: Param not being loaded: Original val was 60*60*1000c
            time_to_autoshape = 10 * 1000   # if system_name isn't in a_params
        needs_shaping = pg.time.get_ticks() - time_to_autoshape > time_since_autoshape
        after_8am = int(time.strftime('%H')) >= 8
        before_4pm = int(time.strftime('%H')) < 16
        if needs_shaping and after_8am and before_4pm:
            log("Autoshaping now...")
            autoshape_datafile = os.path.join(HOSTROOT, '_data', 'autoshaping_' + system_name + '_week' + week + '.csv')
            write_ln(autoshape_datafile, [today, time.strftime('%H:%M:%S')])
            for i, color in enumerate([(0,255,255), (1, 1, 1)] * 2):
                self.screen.bg.fill(color)
                self.screen.fg.blit(self.screen.bg, (0, 0))
                pg.display.update()
                time.sleep(.3)
            #Error: Correct sound unable to be loaded
            #sounds['correct'].play()
            #pellet()
            return True
        return False

    def give_out_freebies(self, freebies=None, active_monkey=None):
        if active_monkey not in freebies.keys():
            freebies[active_monkey] = pg.time.get_ticks()
            for i, color in enumerate([CORRECT_COLOR, (1, 1, 1)] * 2):
                self.screen.bg.fill(color)
                self.screen.fg.blit(self.screen.bg, (0, 0))
                pg.display.update()
                time.sleep(.3)
            sounds['correct'].play()
            pellet()
        if pg.time.get_ticks() - freebies[active_monkey] > self.g_params['TIME_TO_AUTOSHAPE']:
            for i, color in enumerate([CORRECT_COLOR, (1, 1, 1)] * 2):
                self.screen.bg.fill(color)
                self.screen.fg.blit(self.screen.bg, (0, 0))
                pg.display.update()
                time.sleep(.3)
            sounds['correct'].play()
            pellet()
            freebies[active_monkey] = pg.time.get_ticks()
        return freebies

    def feedback_color(self, x=None, y=None, w=None, h=None, sq_color=None, msg=None, msg_color=None):
        if self.g_params['STIMULI_COLORS'] != 'normal':
            self.screen.bg.fill(BLACK)
            self.screen.fg.blit(self.screen.bg, (0, 0))
            pg.draw.rect(self.screen.fg, sq_color, (x, y, w, h))
            self.screen.fg.blit(giant_font.render(msg, False, msg_color), (x + 5, y + 25))
        else:
            self.screen.bg.fill(sq_color)
            self.screen.fg.blit(self.screen.bg, (0, 0))

    def decide_whether_program_is_on(self, overnight=None, overweekend=None):
        
        current_day = time.strftime('%A')
        current_hr = int(time.strftime('%H'))
        if overnight:
            # "Do Not Disturb" mode - for SQM overnight
            after_7am = current_hr >= 7
            before_7pm = current_hr < 19
            if not (after_7am and before_7pm):
                return False
        if overweekend:
            # turn off for rhesus weekends
            if current_day in ['Saturday', 'Sunday']:
                return False
            elif current_day == 'Friday' and current_hr >= 19:
                return False
            elif current_day == 'Monday' and current_hr < 7:
                return False
        return True

    def weekly_progress_reset(self):
        """
        ONCE WEEKLY, RESET PROGRESS OF TRAINED MONKEYS
        """
        
        weekly_reset_filename = os.path.join('_progress', '_weekly-reset',
                                             'trained_monkey_progress_reset_{}week{}'.format(time.strftime('%Y'),
                                                                                             time.strftime('%W')))
        try:
            if not os.path.exists(weekly_reset_filename):
                for monkey in self.m_params.keys():
                    if self.m_params[monkey]['Testing'] == '1':
                        with open(os.path.join('_progress', monkey, 'task-ix.txt'), 'w') as f:
                            f.write('0')
                        with open(os.path.join('_progress', monkey, 'set-ix.txt'), 'w') as f:
                            f.write('0')
                        with open(os.path.join('_progress', monkey, 'progress_to_criterion.txt'), 'w') as f:
                            f.truncate(0)
                os.makedirs(weekly_reset_filename)
        except:
            log(message='error during weekly reset')

    def import_primate_params(self):
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
        log(message='loaded primate params')
        
    def main(self):

        # INIT READER VARS
        # #
        monkey_name = None
        active_monkey = False
        experiment = None
        tag = None
        if not self.g_params['RFID_READER_CONNECTED']:
            tag = 999999999999999

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
        log('^&^&^&^&^&^    PROGRAM STARTED {} {}    ^&^&^&^&^&^'.format(time.strftime('%Y-%m-%d'), time.strftime('%H:%M:%S')))

        # LOAD CLIPART
        # #
        load_start = pg.time.get_ticks()
        clipart = {}
        for image in glob.glob(os.path.join('_modules', '_clipart', '*.jpg')):
            clipart[os.path.basename(image)] = pg.transform.scale(pg.image.load(image), (200, 200))
            pg.draw.rect(self.screen.fg, Color('black'), (300, 300, 400, 75))
            self.screen.fg.blit(big_font.render('{} clipart loaded'.format(len(clipart)), False, Color('salmon')), (300, 300))
            pg.display.update((300, 300, 400, 75))
            if len(clipart)>CLIPART_TO_LOAD:   
                break
        log('{} clipart loaded in {} seconds'.format(len(clipart), (pg.time.get_ticks() - load_start) / 1000))

        # LOAD BOSS CLIPART
        # #
        # load_start = pg.time.get_ticks()
        # ww_clipart = {}
        # for image in glob.glob(os.path.join('_modules', '_ww-clipart', '_BOSS', '*.jpg')):
        #     ww_clipart[os.path.basename(image)] = pg.transform.scale(pg.image.load(image), (200, 200))
        #     pg.draw.rect(self.screen.fg, Color('black'), (300, 300, 400, 75))
        #     self.screen.fg.blit(big_font.render('{} BOSS_clipart loaded'.format(len(ww_clipart)), False, Color('salmon')), (300, 300))
        #     pg.display.update((300, 300, 400, 75))
        #     if len(ww_clipart) > CLIPART_TO_LOAD:
        #         break
        # log('{} ww_clipart loaded in {} seconds'.format(len(ww_clipart), (pg.time.get_ticks() - load_start) / 1000))
        #
        # # LOAD SIMPLE CLIPART  ##ADDED THIS 1Aug2022 MMM
        # # #
        # load_start = pg.time.get_ticks()
        # basicshapes_clipart = {}
        # for image in glob.glob(os.path.join('_modules', '_basicshapes', '*.jpg')):
        #     basicshapes_clipart[os.path.basename(image)] = pg.transform.scale(pg.image.load(image), (200, 200))
        #     pg.draw.rect(self.screen.fg, Color('black'), (300, 300, 400, 75))
        #     self.screen.fg.blit(big_font.render('{} basicshapes_clipart loaded'.format(len(basicshapes_clipart)), False, Color('salmon')), (300, 300))
        #     pg.display.update((300, 300, 400, 75))
        #     if len(basicshapes_clipart) > CLIPART_TO_LOAD:
        #         break
        # log('{} basicshapes_clipart loaded in {} seconds'.format(len(basicshapes_clipart), (pg.time.get_ticks() - load_start) / 1000))

        log('loaded global params ::')
        for k, v in self.g_params.items():
            log('{} :: {}'.format(k, v))
        self.import_primate_params()

        # LOAD READER #comment out for running in Pycharm
        # #
        if self.g_params['RFID_READER_CONNECTED']:
            import serial
            self.device = serial.Serial('/dev/serial0', 9600, timeout=0)
        else:
            run()
            log("INFO: Running camera on seperate thread.")
        # MAKE ANY AMERICAN MONKEY CHANGES
        # #
        if self.g_params['STIMULI_COLORS'] == 'normal':
            CORRECT_COLOR = BLUE
            INCORRECT_COLOR = RED
        else:
            CORRECT_COLOR = BLACK
            INCORRECT_COLOR = BLACK

        # FEEDBACK
        # #
        reward_tracker = {}    # TRACK NUMBER OF REWARDS DISPENSED
        trial_tracker = {}     # TRACK NUMBER OF TRIALS COMPLETED
        freebies = {}          # TRACK SHAPING FREEBIES FOR MONKEYS THAT GET SHAPING FREEBIES

        # PROGRAM TIMING
        # #
        time_since_reset = pg.time.get_ticks()
        time_since_autoshape = pg.time.get_ticks()
        time_to_reset = self.g_params['TIME_TO_RESET']
        status = 'running'
        clock = pg.time.Clock()
        today = time.strftime('%Y-%m-%d')
        need_to_import_params = False
        done = False
                
        # GAMELOOP
        # #
        while not done:
            #program_on = self.decide_whether_program_is_on(overnight=self.g_params['DO_NOT_DISTURB'],
                                                           #overweekend=True)
            program_on = True
            self.weekly_progress_reset()
                
            # once daily, reload primate params when it becomes 3AM
            # #
            if need_to_import_params and time.strftime('%H') == '03':
                need_to_import_params = False
                self.import_primate_params()
            elif time.strftime('%H') != '03':
                need_to_import_params = True
                        
            if not program_on:
                for event in pg.event.get():
                    check_quit(event=event)
                self.screen.bg.fill(BLACK)
                self.screen.fg.blit(self.screen.bg, (0, 0))
                pg.display.update()
                clock.tick(FPS)
            else:
                # if day has changed, reset trackers
                # #
                if today != time.strftime('%Y-%m-%d'):
                    today = time.strftime('%Y-%m-%d')
                    reward_tracker = {}
                    trial_tracker = {}

                # update logger if week changes
                # #
                week = time.strftime('%W')
                errorlog_name = '{}-week{}-errorlog.txt'.format(system_name, week)
                if not os.path.exists(os.path.join(HOSTROOT, 'errorlogs', errorlog_name)):
                    with open(os.path.join(HOSTROOT, 'errorlogs', errorlog_name), 'w') as f:
                        f.write('\n ~@~@~@~@~@~@~@~@~ START OF ERRORLOG FOR {0} ~@~@~@~@~@~@~@~@~'.format(TODAY))
                        logger = logging.getLogger('')
                        logger.handlers = []
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
                # only reset when reader connected since it otherwise wouldn't know when to 
                #   turn back on
                if time_to_reset > 0 and self.g_params['RFID_READER_CONNECTED'] and (pg.time.get_ticks() - time_since_reset > time_to_reset):
                    time_since_reset = pg.time.get_ticks()
                    active_monkey = False
                    monkey_name = None
                    experiment = None
                    status = 'running'

                # attempt autoshape
                # #
                autoshaped = self.autoshape(time_since_autoshape=time_since_autoshape, today=today, week=week, correct_color=CORRECT_COLOR)
                if autoshaped:
                    print("reseting experiment")
                    if not self.g_params['RFID_READER_CONNECTED']:
                        tag = 999999999999999
                    active_monkey = False
                    monkey_name = None
                    experiment = None
                    time_since_reset = pg.time.get_ticks()
                    time_since_autoshape = pg.time.get_ticks()
                    status = 'running'

                # RFID/menu logic
                # #
                # every frame, see which tag is around and which monkey it belongs to
                if self.g_params['RFID_READER_CONNECTED']:
                    tag = self.get_id()
                    if tag is not None and tag != 'read_error':
                        try:
                            tag = str(int(tag))
                        except:
                            tag = 'read_error'
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
                    elif tag == 'read_error':
                        status = 'read_error'
                else:
                    monkey_name = state_color.max_color
                    self.screen.fg.blit(sm_font.render(monkey_name, True, Color('white')), (256, 115))
                    #log("Color: "+str(state_color.max_color))
                    #log("Monkey Name:"+str(monkey_name))
                # get any typed input
                # #
                for key in self.m_params.keys():
                    if self.mutable_text == key:
                        self.mutable_text = self.debug_text = ''
                        monkey_name = key
                        arm_used = 'NA'
                        break
                    if self.mutable_text in ['p17', 'p27']:
                        pellet(time_to_close_relay=20, channel=int(self.mutable_text[-2:]))
                        self.mutable_text = self.debug_text = ''

                # start a program...
                #  if no monkey program is already running but a tag was found,
                #    or if a different tag was read than that of the active monkey,
                #    or if the currently-working monkey has progressed to a new task
                # #
                monkey_enters_anew = not active_monkey and monkey_name is not None
                new_monkey_takes_over = monkey_name is not None and monkey_name != active_monkey
                should_progress = experiment.progressed if experiment is not None else False
                if (monkey_enters_anew or new_monkey_takes_over or should_progress) and monkey_name is not None:
                    log(self.m_params)
                    if monkey_enters_anew or new_monkey_takes_over:
                        active_monkey = monkey_name
                    try:
                        if 'Machine' in self.m_params[active_monkey].keys():
                            permitted_machines = self.m_params[active_monkey]['Machine'].split('-')
                        else:
                            permitted_machines = 'all'
                        if system_name in permitted_machines or 'all' in permitted_machines:
                            # if self.m_params[active_monkey][''] == '1':
                            #     freebies = self.give_out_freebies(freebies=freebies, active_monkey=active_monkey)
                            self.screen.bg.fill(BLACK)
                            self.screen.fg.blit(self.screen.bg, (0, 0))
                            with open(os.path.join('_progress', active_monkey, 'task-ix.txt'), 'r') as f:
                                line = f.readline()
                                task_ix = int(line.replace('\n', '').replace('\r', ''))
                            task_order = self.determine_task_order(active_monkey=active_monkey)
                            task_to_load = task_order[task_ix]
                            log("Task index: "+str(task_ix))
                            log("Task to load: "+str(task_to_load))
                            if task_to_load[:2] == 'ww':
                                experiment = eval('modules.{}.{}(screen=self.screen, monkey_name=active_monkey, g_params=self.g_params, m_params=self.m_params, arm_used=None, clipart=ww_clipart)'.format(task_to_load, task_to_load))
                            elif task_to_load[:9] == 'MTSsimple': #attempting to add in basic shape clipart only for MTSsimple module MMM 1Aug2022
                                experiment = eval('modules.{}.{}(screen=self.screen, monkey_name=active_monkey, g_params=self.g_params, m_params=self.m_params, arm_used=None, clipart=basicshapes_clipart)'.format(task_to_load, task_to_load))
                            else:
                                experiment = eval('modules.{}.{}(screen=self.screen, monkey_name=active_monkey, g_params=self.g_params, m_params=self.m_params, arm_used=None, clipart=clipart)'.format(task_to_load, task_to_load))
                            status = 'running'
                            experiment.new_trial()
                        else:
                            log('{} is not allowed on machine {}'.format(active_monkey, self.m_params[active_monkey]['Machine']))
                            experiment = None
                            active_monkey = False
                            status = 'error_loading_program'
                    except:
                        log('Error starting program for {}'.format(active_monkey))
                        logging.exception('')
                        experiment = None
                        active_monkey = False
                        status = 'error_loading_program'

                # if monkey has reward or trial cap and exceeds it today, throw error
                # #
                if active_monkey:
                    flags = 0
                    if self.m_params[active_monkey]['Daily Reward Cap'] != '0':
                        if active_monkey in reward_tracker.keys():
                            if reward_tracker[active_monkey] >= int(self.m_params[active_monkey]['Daily Reward Cap']):
                                log('{} has had too many rewards today'.format(active_monkey))
                                flags += 1   # flagged for having too many rewards
                    if self.m_params[active_monkey]['Daily Trial Cap'] != '0':
                        if active_monkey in trial_tracker.keys():
                            if trial_tracker[active_monkey] >= int(self.m_params[active_monkey]['Daily Trial Cap']):
                                log('{} has done too many trials today'.format(active_monkey))
                                flags += 1    # flagged for having too many trials
                    # if monkey has flags, ignore them
                    if flags > 0:
                        experiment = None
                        active_monkey = False
                        monkey_name = None
                        status = 'error_loading_program' 

                # run any code that should happen on every iteration of the game loop
                # #
                if experiment is not None:
                    experiment.on_loop()
                            
                # read touches
                # #
                #   if program is running, check and process touches
                # #
                if status not in ['wwITI', 'ITI', 'wwtimeout', 'timeout', 'buffer', 'error_loading_program', 'read_error']:
                    for event in pg.event.get():
                        check_quit(event=event)
                        self.get_command(event=event)
                        if event.type == MOUSEBUTTONDOWN and experiment is not None:
                            touch_x, touch_y = event.pos
                            time_since_reset = pg.time.get_ticks()
                            time_since_autoshape = pg.time.get_ticks()
                            status = experiment.on_touch(touch_x=touch_x, touch_y=touch_y)
                            if status in ['ITI', 'timeout', 'wwITI', 'wwtimeout']:
                                outcome_timer = pg.time.get_ticks()
                                if active_monkey:
                                    if self.m_params[active_monkey]['Daily Trial Cap'] != '0':
                                        if active_monkey in trial_tracker.keys():
                                            trial_tracker[active_monkey] += 1  # iterate trial cap
                                        else:
                                            trial_tracker[active_monkey] = 1   # init trial cap
                            if status in ['ITI']:
                                sounds['correct'].play()
                                self.feedback_color(x=0, y=200, w=768, h=768,
                                                    sq_color=CORRECT_COLOR,
                                                    msg='GOOD!!!!', msg_color=(0, 255, 255))
                                pg.display.update()
                                time_to_sleep = 0 if self.g_params['STIMULI_COLORS'] == 'normal' else .6
                                time.sleep(time_to_sleep)    # attempting this, changed from .3
                                
                                # if monkey has daily reward cap, track progress towards it
                                if active_monkey:
                                    if self.m_params[active_monkey]['Daily Reward Cap'] != '0' or \
                                        self.m_params[active_monkey]['Daily Reward Cap2'] != '0':
                                        if active_monkey in reward_tracker.keys():
                                            reward_tracker[active_monkey] += 1  # iterate reward cap
                                        else:
                                            reward_tracker[active_monkey] = 1   # init reward cap
                                
                                    if self.g_params['STIMULI_COLORS'] == 'normal':
                                        channel = 17
                                    else:
                                        if self.m_params[active_monkey]['Daily Reward Cap2'] == '0':
                                            channel = 17
                                        else:
                                            if reward_tracker[active_monkey] <= int(self.m_params[active_monkey]['Daily Reward Cap2']):
                                                channel = 17
                                                log('channel set to {}'.formt(channel))
                                            else:
                                                channel = 27
                                            log('used channel {}'.format(channel))
                                
                                for i in range(int(self.g_params['REWARD_AMOUNT'])):
                                    if self.g_params['REWARD_TYPE'] != 'pellet':
                                        pellet(time_to_close_relay=1.25, channel=channel)    # liquid reward
                                    else:
                                        pellet()                            # solid reward

                            if status in ['wwITI']:
                                # if monkey has daily reward cap, track progress towards it
                                if active_monkey:
                                    if self.m_params[active_monkey]['Daily Reward Cap'] != '0' or \
                                            self.m_params[active_monkey]['Daily Reward Cap2'] != '0':
                                        if active_monkey in reward_tracker.keys():
                                            reward_tracker[active_monkey] += 1  # iterate reward cap
                                        else:
                                            reward_tracker[active_monkey] = 1  # init reward cap
                                self.screen.bg.fill(BLACK)
                                self.screen.fg.blit(self.screen.bg, (0, 0))
                                pg.draw.lines(self.screen.fg, Color('olivedrab'), True, [(79,455),(221,751),(119,689),(897,179),(725,724),(516,149),(661,187),(230,534),(312,496),(914,405),(339,449),(34,750),(70,615),(308,539),(404,753),(231,694),(938,172),(842,365),(429,745),(223,288),(107,404),(636,176),(626,682),(514,15),(364,687)],10)
                                pg.display.update()
                                sounds['correct'].play()
                                for i in range(int(self.g_params['REWARD_AMOUNT'])):
                                    if self.g_params['REWARD_TYPE'] != 'pellet':
                                        pellet(time_to_close_relay=2.5, channel=17)    # liquid reward
                                    else:
                                        pellet()                            # solid reward

                            if status in ['timeout']:
                                pg.display.update()
                                sounds['incorrect'].play()
                                self.feedback_color(x=450, y=200, w=768, h=768,
                                                    sq_color=INCORRECT_COLOR,
                                                    msg='X', msg_color=(255, 0, 0))
                                pg.display.update()

                            if status in ['wwtimeout']:
                                self.screen.bg.fill(BLACK)
                                self.screen.fg.blit(self.screen.bg, (0, 0))
                                pg.draw.lines(self.screen.fg, Color('tomato'), True, [(79,455),(221,751),(119,689),(897,179),(725,724),(516,149),(661,187),(230,534),(312,496),(914,405),(339,449),(34,750),(70,615),(308,539),(404,753),(231,694),(938,172),(842,365),(429,745),(223,288),(107,404),(636,176),(626,682),(514,15),(364,687)],10)
                                pg.display.update()
                                sounds['incorrect'].play()

                            pg.event.clear()
                            break
                        
                # on correct touch
                # #
                elif status == 'ITI':
                    self.feedback_color(x=0, y=200, w=768, h=768,
                                        sq_color=CORRECT_COLOR,
                                        msg='GOOD!!!!', msg_color=(0, 255, 255))
                    if pg.time.get_ticks() - outcome_timer > experiment.ITI:
                        status = 'buffer'
                        outcome_timer = pg.time.get_ticks()
                elif status == 'wwITI':
                    self.screen.bg.fill(BLACK)
                    self.screen.fg.blit(self.screen.bg, (0, 0))
                    pg.draw.lines(self.screen.fg, Color('olivedrab'), True, [(79,455),(221,751),(119,689),(897,179),(725,724),(516,149),(661,187),(230,534),(312,496),(914,405),(339,449),(34,750),(70,615),(308,539),(404,753),(231,694),(938,172),(842,365),(429,745),(223,288),(107,404),(636,176),(626,682),(514,15),(364,687)],10)
                    if pg.time.get_ticks() - outcome_timer > experiment.ITI:
                        status = 'buffer'
                        outcome_timer = pg.time.get_ticks()

                # on incorrect touch
                # #
                elif status == 'timeout':
                    self.feedback_color(x=450, y=200, w=768, h=768,
                                        sq_color=INCORRECT_COLOR,
                                        msg='X', msg_color=(255, 0, 0))
                    if pg.time.get_ticks() - outcome_timer > experiment.timeout:
                        status = 'buffer'
                        outcome_timer = pg.time.get_ticks()
                elif status == 'wwtimeout':
                    self.screen.bg.fill(BLACK)
                    self.screen.fg.blit(self.screen.bg, (0, 0))
                    pg.draw.lines(self.screen.fg, Color('tomato'), True, [(79,455),(221,751),(119,689),(897,179),(725,724),(516,149),(661,187),(230,534),(312,496),(914,405),(339,449),(34,750),(70,615),(308,539),(404,753),(231,694),(938,172),(842,365),(429,745),(223,288),(107,404),(636,176),(626,682),(514,15),(364,687)],10)
                    if pg.time.get_ticks() - outcome_timer > experiment.timeout:
                        status = 'buffer'
                        outcome_timer = pg.time.get_ticks()

                # after either correct or incorrect touch
                # #
                elif status == 'buffer':
                    self.screen.bg.fill(BUFFER_COLOR)
                    self.screen.fg.blit(self.screen.bg, (0, 0))
                    for event in pg.event.get([QUIT, KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]):
                        check_quit(event=event)
                        if event.type in [MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION] and experiment is not None:
                            outcome_timer = pg.time.get_ticks()
                            #pg.event.clear()
                            #break
                        #pg.event.clear()
                        #break
                    if pg.time.get_ticks() - outcome_timer > self.g_params['DRO_DURATION']*1000:
                        status = 'running'
                        pg.event.clear()
                        experiment.new_trial()
                
                # if finished monkey tried to load a program
                # #
                if status == 'error_loading_program' or status == 'read_error':
                    for event in pg.event.get():
                        check_quit(event=event)
                        self.get_command(event=event)
                    if status == 'error_loading_program':
                        self.screen.bg.fill(Color('darkorchid'))
                    elif status == 'read_error':
                        self.screen.bg.fill(Color('gold'))
                    self.screen.fg.blit(self.screen.bg, (0, 0))

                # if frontend is running and looking for input/quit, but no task is loaded
                # #
                if not active_monkey and status == 'running':
                    for event in pg.event.get([QUIT, KEYDOWN]):
                        check_quit(event=event)
                        self.get_command(event=event)
                    self.screen.bg.fill(Color('green'))
                    self.screen.fg.blit(self.screen.bg, (0, 0))

                if not self.g_params['RFID_READER_CONNECTED']:
                    tag = None  # reset tag to None to simulate monkey steadily in holster for debugging

                # output things to researcher in debug window
                # #
                if not self.g_params['DEBUG_WINDOW_ON'] and status == 'buffer':
                    pass
                else:
                    pg.draw.rect(self.screen.fg, (0, 0, 0), (0, 0, self.g_params['SCREEN_W'], 50))

                    if self.g_params['RFID_READER_CONNECTED']:
                        if tag is not None:
                            if len(tag) < 15:
                                self.screen.fg.blit(sm_font.render('RFID ERROR: {}'.format(tag), False, Color('salmon')), (5, 5))
                            else:
                                self.screen.fg.blit(sm_font.render(tag, False, Color('salmon')), (5, 5))
                        else:
                            self.screen.fg.blit(sm_font.render('{} at {} FPS'.format(random.choice(['running', 'going', 'rolling', 'moving', 'succeeding']), str(int(clock.get_fps()))), False, Color('salmon')), (5, 5))

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
