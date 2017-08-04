# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient

class DataBaseHandler () :
    def __init__(self):
        self.client = MongoClient('localhost',3070)
        self.db = self.client.zkpush
        self.col_names = self.db.collection_names(include_system_collections=False)
        print("MongoDB zkpush collections:")
        print(self.col_names)

    def update_devicesInfo(self,sn,info):
        info_data = info
        info_data['SN'] = sn
        self.db.devices.update(
                    {'SN'  : sn},
                    {'$set': info_data},
                    True,   #upsert = True
                    False   # multi = False
                )

    def get_deviceInfo(self,sn):
        data = self.db.devices.find_one({"SN": sn})
        data.pop('_id')
        data.pop('SN')
        return data;

    def update_devicesOptions(self,sn,option):
        option_data = option
        option_data['SN'] = sn
        print("DB:update_devicesOptions", option_data)
        if 'options' in self.db.collection_names(include_system_collections=False):
            self.db.options.update(
                        {'SN'  : sn},
                        {'$set': option_data},
                        True,   #upsert = True
                        False   # multi = False
                    )
        else :
            self.db.options.insert(option_data);

    def get_devicesOptions(self,sn):
        if 'options' in self.db.collection_names(include_system_collections=False):
            data = self.db.options.find_one({"SN": sn})
            print("DB: Option: ",data)
            if data != None :
                data.pop('_id')
                data.pop('SN')
            return data;
        else :
            return None;

    def add_error_log(self,record):
        if 'errlog' not in self.db.collection_names(include_system_collections=False):
            tmp = self.db.errlog
        #record = {'SN':'','type': '', 'content':'','wTime':}
        self.db.errlog.insert(record)

    def get_error_logs(self,start,end):
        logs = []
        if 'errlog' in self.db.collection_names(include_system_collections=False):
            data = self.db.errlog.find({'wTime':{'$lt':end, '$gt':start}})
            for log in data:
                logs.append(log)
            return logs

    def get_heartbeat_setting(self,default):
        if 'heartbeatSetting' in self.db.collection_names(include_system_collections=False):
            data = self.db.heartbeatSetting.find_one({"SN": default['SN']})
            if data == None :
                print("Insert heartbeatSetting setting SN: ", default['SN'])
                self.db.heartbeatSetting.insert(default)
                return default
            else :
                return data
        else :
            print( "Create a New collection heartbeatSetting and insert setting SN: ",default['SN'])
            self.db.heartbeatSetting.insert(default)
            return default

    def update_heartbeat_time(self,sn,timestamp):
        self.db.heartbeatSetting.update(
                    {'SN'  : sn},
                    {'$set': timestamp},
                    True,   #upsert = True
                    False   # multi = False
                )

    def get_serverConnection_setting(self,default):
        if 'serverConSetting' in self.db.collection_names(include_system_collections=False):
            data = self.db.serverConSetting.find_one({"RaspyNum": default['RaspyNum']})
            if data == None :
                print("Insert serverConSetting setting RaspyNum: ", default['RaspyNum'])
                self.db.heartbeatSetting.insert(default)
                return default
            else :
                return data
        else :
            print( "Create a New collection serverConSetting and insert setting RaspyNum: ",default['RaspyNum'])
            self.db.serverConSetting.insert(default)
            return default

    def update_serverConnection_setting(self,data):
        self.db.serverConSetting.update(
                    {'RaspyNum'  : data['RaspyNum']},
                    {'$set': data},
                    True,   #upsert = True
                    False   # multi = False
                )

    def get_all_devices(self,sn):
        data = self.db.devices.find({'SN':sn})
        print("get_all_devices : ",data)
        return data


DB_Handler = DataBaseHandler()


if __name__ == "__main__":
    sn = '3637165101475'
    db_handler = DB_Handler
    data = db_handler.get_all_devices(sn)
    for it in data:
        print("key :",it)
