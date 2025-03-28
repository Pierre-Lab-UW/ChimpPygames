


from _modules.pgtools import *

import time



class two_lever_task(object):

    def __init__(self, screen=None, monkey_name=None, g_params=None, m_params=None, arm_used=None, clipart=None):
        # initialising basic parameters
        self.screen = screen
        self.g_params = g_params
        self.m_params = m_params
        self.task_name = 'two_lever_task'
        self.monkey_name = monkey_name
        self.ITI = int(self.m_params[self.monkey_name]['ITI'])

        self.filepath_to_data = os.path.join('_data', '{}-{}-{}-{}.csv'.format(self.monkey_name, system_name,
                                                                               time.strftime('%Y-%m-%d'),
                                                                               self.task_name))
        self.filepath_to_progress = os.path.join('_progress', self.monkey_name, 'progress_to_criterion.txt')
        self.filepath_to_phase = os.path.join('_progress', self.monkey_name, 'TI_phase.txt')

        # task specific paamters
        self.lp = 0  # number of times lever is pressed

        self.lp_dur = 0  # time lever held in the depressed position

        self.closures_proportion =0 # self.lp_dur/timeout period,  #  of lever closures






#| Initials|Schedule|Schedule parameter|Session length|Time out| ITI | Reward #| Reward Delay







def new_trial():

    #trial light on






    # lever light on





def on_loop(self):




def choose_lever(self):

    if self.mode

def measure_time(self):

    # measure time







