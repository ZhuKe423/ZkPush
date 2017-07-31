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
        #record = {'SN':'','type': '', 'content':''}
        self.db.errlog.insert(record)

    def get_heartbeat_setting(self,default):
        if 'heartbeatSetting' in self.db.collection_names(include_system_collections=False):
            data = self.db.heartbeatSetting.find_one({"SN": default['SN']})
            if data == None :
                print("Insert heartbeatSetting setting SN: %s", default['SN'])
                self.db.heartbeatSetting.insert(default)
                return default
            else :
                return data
        else :
            print( "Create a New collection heartbeatSetting and insert setting SN: %s",default['SN'])
            self.db.heartbeatSetting.insert(default)
            return default

    def update_heartbeat_time(self,sn,timestamp):
        self.db.heartbeatSetting.update(
                    {'SN'  : sn},
                    {'$set': timestamp},
                    True,   #upsert = True
                    False   # multi = False
                )

DB_Handler = DataBaseHandler()