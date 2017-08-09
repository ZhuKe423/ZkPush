# -*- coding: utf-8 -*-

import time
from databaseHandler import DB_Handler,DataBaseHandler
from connectToServer import ServerHandler
import datetime

Default_HeartBeatSetting = {
        'SN': '',
        'syncAttLog_Time' : '23:00:00',
        'heartbeatLos_sec'  : (5 * 60),
        'last_beat_time'    : 82983982,
        'last_getCmd_Server' : 82983982,
        'getServerCmd_inv'   : (1 * 60 * 60),

    }

SYNC_ATTLOG_NOT_DO          = 0
SYNC_ATTLOG_CMD_SENDING     =  1
SYNC_ATTLOG_CMD_RETURN      =  2
SYNC_ATTLOG_SENDING_SERVER  =  3
SYNC_ATTLOG_SENDED          =  4
SYNC_ATTLOG_DONE            =  5

class HeartBeatHandler():
    last_beat_time = 82983982
    last_getCmd_Server = 0
    sync_cmdId = 0
    today_sync_attLog = SYNC_ATTLOG_NOT_DO
    str_today_date  = ''
    str_today_s     = ''
    str_today_e     = ''
    sync_time_st    = 0
    tomorrow_st     = 0
    
    def __init__(self,sn,cmdEngine,server) :
        self.record_over_flag = False
        self.db_handler = DB_Handler
        self.settings = Default_HeartBeatSetting
        self.settings['SN'] = sn
        self.settings = self.db_handler.get_heartbeat_setting(self.settings)
        self.last_beat_time = self.settings['last_beat_time']
        self.last_getCmd_Server = self.settings['last_getCmd_Server']
        self.cmdEngine = cmdEngine
        self.serverhandler = server
        self.update_info_for_newDay()

    def update_info_for_newDay(self):
        today = datetime.date.today()
        self.str_today_s = format("%s 00:00:05" % today)
        self.str_today_e = format("%s 23:59:59" % today)

        strtmp = format("%s %s" % (today,self.settings['syncAttLog_Time']))
        self.sync_time_st = int(time.mktime(time.strptime(strtmp,"%Y-%m-%d %H:%M:%S")))

        strtmp = format("%s 00:00:01" % (today + datetime.timedelta(days=1)))
        self.tomorrow_st = int(time.mktime(time.strptime(strtmp, "%Y-%m-%d %H:%M:%S")))

        self.today_sync_attLog = SYNC_ATTLOG_NOT_DO
        print("update_dataTime_info")


    def set_record_over_flag(self,is_over):
        self.record_over_flag = is_over

    def is_in_sync_state(self):
        return (self.today_sync_attLog != SYNC_ATTLOG_NOT_DO) and (self.today_sync_attLog != SYNC_ATTLOG_DONE)

    def set_sync_state(self,value):
        self.today_sync_attLog = value

    def manual_sync_attLog(self):
        self.sync_cmdId = self.cmdEngine.genCmd_query_log(self.str_today_s, self.str_today_e)
        self.set_sync_state(SYNC_ATTLOG_CMD_SENDING)
        print('HB manual_sync_attLog :  %s', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

    def hearbeat(self):
        t_now = int(time.time())
        timestamp = {}
        if (t_now - self.last_beat_time) > self.settings['heartbeatLos_sec'] :
            self.cmdEngine.genCmd_get_new_log();

        if (t_now - self.last_getCmd_Server) > self.settings['getServerCmd_inv'] :
            self.settings['last_getCmd_Server'] = t_now
            self.last_getCmd_Server = t_now
            self.serverhandler.getServerCmd(sn=self.settings['SN']);

        if (t_now > self.sync_time_st) and (SYNC_ATTLOG_NOT_DO == self.today_sync_attLog) :
            self.sync_cmdId = self.cmdEngine.genCmd_query_log(self.str_today_s, self.str_today_e)
            self.set_sync_state(SYNC_ATTLOG_CMD_SENDING)
            print('HB trigger_sync_attLog :  %s', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_now)))

        if t_now > self.tomorrow_st :
            self.update_info_for_newDay()

        if self.today_sync_attLog == SYNC_ATTLOG_SENDING_SERVER :
            self.set_sync_state(SYNC_ATTLOG_SENDED)
        if self.today_sync_attLog == SYNC_ATTLOG_SENDED :
            self.cmdEngine.genCmd_clear_attLog()
            self.set_sync_state(SYNC_ATTLOG_DONE)

        self.last_beat_time = t_now
        timestamp['last_beat_time'] = t_now
        self.db_handler.update_heartbeat_time(self.settings['SN'],timestamp)
        print("hearbeat time=%s" % self.last_beat_time)


    def check_sync_attlog(self,response,records):
        if response['cmdIds'] == self.sync_cmdId :
            self.set_sync_state(SYNC_ATTLOG_CMD_RETURN)
            self.serverhandler.syncAttLog(records,sn=self.settings['SN'])
            self.set_sync_state(SYNC_ATTLOG_SENDING_SERVER)
