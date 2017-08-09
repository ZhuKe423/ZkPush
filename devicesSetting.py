# -*- coding: utf-8 -*-

import time
from databaseHandler import DB_Handler,DataBaseHandler
from heartBeatHandler import HeartBeatHandler,SYNC_ATTLOG_SENDING_SERVER
from cmd_defines import CMD_Engine
from connectToServer import ServerHandler

DevicesHandler = {}

DefaultDeviceOptions = {
        'Stamp'         : '82983982' ,
        'OpStamp'       : '9238883',
        'PhotoStamp'    : '9238833',
        'ErrorDelay'    : '60',
        'Delay'         : '30',
        'TransTimes'    : '00:00;14:05',
        'TransInterval' : '1',
        'TransFlag'     : '1111000000',
        'Realtime'      : '1',
        'Encrypt'       : '0',
        'ServerVer'     : '3.4.1 2010 - 06 - 07',
        'ATTLOGStamp'   : '82983982'
}

DefaultUserInfo = {
        'PIN'       : '101010101010',
        'Name'      : '陈',
        'Pri'       : '0' ,   # 权限(14 管理员,0 普通用户)
        'Passwd'    : '123',
        'Card'      : '15895470',              #用户卡号
        'Grp'       : '1',                  #组别(用于门禁)
        'TZ'        : '0001000100000000',   #时段(用于门禁)
}

RECORD_OVER_COUNT = 600

def GetDeviceHandler(sn):
    if sn in DevicesHandler:
        return DevicesHandler[sn]
    else :
        DevicesHandler[sn] = DeviceHandler(sn)
        return DevicesHandler[sn]


def Devices_Common_Process(cmd,value):
    for sn in DevicesHandler:
        DevicesHandler[sn].cmd_process(cmd,value)
    return


SERVER_Handler = ServerHandler(Devices_Common_Process);

class DeviceHandler ():
    sn = ''
    dev_info = {}
    last_record_time = 0
    last_info_time = 0
    options = None
    sync_attlog_records = []

    def __init__(self,sn) :
        self.sn = sn
        self.last_record_time = int('82983982')
        self.last_info_time = int('82983982')
        self.db_handler = DB_Handler;
        self.options = self.db_handler.get_devicesOptions(sn)
        if (self.options == None) :
            self.options = DefaultDeviceOptions
            self.db_handler.update_devicesOptions(self.sn,self.options)
        print(self.options)

        self.cmdEngine = CMD_Engine(sn)
        self.cmdEngine.genCmd_dev_info();
        self.cmdEngine.genCmd_check();
        self.serverhandler = SERVER_Handler
        self.heart_beat = HeartBeatHandler(sn,self.cmdEngine,self.serverhandler)
        self.serverhandler.updateStudents(sn=self.sn)

    def updateInfor(self,info):
        self.dev_info = info
        last_info_time = int(time.time())
        print(self.dev_info)
        print("last_info_time = %d" % last_info_time)
        self.db_handler.update_devicesInfo(self.sn,self.dev_info)

        #if self.dev_info['recordCount'] > RECORD_OVER_COUNT :
            #self.heart_beat.set_record_over_flag(True)
        pass

    def get_deviceOptions_all(self) :
        return self.options

    def interalBeat(self) :
        self.heart_beat.hearbeat()

        #for test
        #self.update_user_infor(DefaultUserInfo)
        #self.cmdEngine.genCmd_query_user(DefaultUserInfo['PIN'])
        today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
        today_s = today+" 00:00:01"
        today_e = today+" 23:59:59"
        #self.cmdEngine.genCmd_query_log(today_s,today_e)

    def add_sync_record(self,record):
        self.sync_attlog_records.append(record)

    def new_record_log(self,record):
        self.last_record_time = int(time.time())
        tmp_time = time.localtime(float(self.last_record_time))
        self.options['Stamp'] = str(self.last_record_time)
        self.options['ATTLOGStamp'] = str(self.last_record_time)
        self.db_handler.update_devicesOptions(self.sn,self.options)
        print("last_record_time = %s" % time.strftime("%Y-%m-%d %H:%M:%S",tmp_time))
        #print(record)
        if record == '':
            print('recoder is NULL')
            return

        if self.heart_beat.is_in_sync_state() :
            print("Sync record : " , record)
            self.add_sync_record(record)
        else :
            print("New record :" , record)
            self.serverhandler.newRecord(record,sn=self.sn)

    def get_cmd_list(self):
        return self.cmdEngine.get_genCmd_lines();

    def process_response(self,responses) :
        tmpcmd = ''
        is_need_saveInfor = False
        dev_info = {}
        cmd_response = {}
        for res_cmd in responses :
            if res_cmd[0:3] == 'ID=' :
                session = res_cmd.split('&')
                cmd_response['cmdIds'] = int(session[0].split('=')[1])
                cmd_response['state'] = int(session[1].split('=')[1])
                cmd_response['cmd'] = session[2].split('=')[1]
                tmpcmd = cmd_response['cmd']
                #print("tmpcmd : ",tmpcmd)
                self.heart_beat.check_sync_attlog(cmd_response,records=self.sync_attlog_records)
                self.cmdEngine.response_cmd_line(cmd_response)
            elif tmpcmd == 'INFO' :
                session = res_cmd.split('=')
                if len(session) < 2 :
                    continue
                dev_info[session[0]] = session[1]
                is_need_saveInfor = True;

        if is_need_saveInfor :
            #print(dev_info)
            self.updateInfor(dev_info)
        pass

    def update_user_infor(self,user):
        self.cmdEngine.genCmd_update_user(user)

    def del_user(self,user):
        self.cmdEngine.genCmd_delet_user(user)

    def cmd_process(self,cmd,value):
        if cmd == 'syncAttLog' :
            self.heart_beat.manual_sync_attLog()
        elif cmd == 'updateUser' :
            print("cmd_process->updateUser ",value)
            for infor in value:
                self.cmdEngine.genCmd_update_user(infor)
        elif cmd == 'deleteUser' :
            print("deleteUser : ",value)
            for infor in value:
                self.cmdEngine.genCmd_delet_user(infor)
        elif cmd == 'clearAll':
            self.cmdEngine.genCmd_clear_dataAll()
        pass