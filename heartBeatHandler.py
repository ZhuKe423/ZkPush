# -*- coding: utf-8 -*-

import time
from databaseHandler import DB_Handler,DataBaseHandler


Default_HeartBeatSetting = {
        'SN': '',
        'syncToServer_Time' : '23:30:00',
        'heartbeatLos_sec'  : (5 * 60),
        'last_beat_time'    : 82983982,
        'last_getCmd_Server' : 82983982,
        'getServerCmd_inv'   : (10 * 60),
    }

class HeartBeatHandler():
    last_beat_time = 82983982
    last_getCmd_Server = 0
    def __init__(self,sn,cmdEngine) :
        self.record_over_flag = False
        self.db_handler = DB_Handler
        self.settings = Default_HeartBeatSetting
        self.settings['SN'] = sn
        self.settings = self.db_handler.get_heartbeat_setting(self.settings)
        self.last_beat_time = self.settings['last_beat_time']
        self.last_getCmd_Server = self.settings['last_getCmd_Server']
        self.cmdEngine = cmdEngine

    def set_record_over_flag(self,is_over):
        self.record_over_flag = is_over


    def hearbeat(self):
        t_now = int(time.time())
        timestamp = {}
        if (t_now - self.last_beat_time) > self.settings['heartbeatLos_sec'] :
            self.cmdEngine.genCmd_get_new_log();

        if (t_now - self.last_getCmd_Server) > self.settings['getServerCmd_inv'] :
            timestamp['last_getCmd_Server'] = t_now
            #TODO: get command form server

        self.last_beat_time = t_now;
        timestamp['last_beat_time'] = t_now
        self.db_handler.update_heartbeat_time(self.settings['SN'],timestamp)
        print("hearbeat time=%s" % self.last_beat_time)