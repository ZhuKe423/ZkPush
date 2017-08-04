# -*- coding: utf-8 -*-

#import urllib2
from tornado import curl_httpclient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from databaseHandler import DB_Handler,DataBaseHandler

import urllib,json

Default_URL = {
        'updateStudent' : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/updateStudent',
        'SyncAttLog'    : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/syncRecord',
        'NewRecord'     : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/newRecord',
        'getStudent'    : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/getStudent',
        'GetCmd'        : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/getCommand',
        'sendErrorLogs' : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/',
    }

ClIENT_TOKEN = 'gh_2837e31e28ed'

Default_ServerConnection_Setting = {
        'RaspyNum'                : "DingYi-0001",
        'last_updatestd_st'     : 0,           #服务器传过来的更新时间戳

    }

class ServerHandler() :
    dev_process = ''

    def __init__(self,dev_callback):
        self.url_list = Default_URL;
        self.http_client = CurlAsyncHTTPClient()
        self.stdudents_buf = []
        self.db_handler = DB_Handler
        self.settings = self.db_handler.get_serverConnection_setting(Default_ServerConnection_Setting)
        self.dev_process =dev_callback


    def updateStudents(self,sn):
        self.stdudents_buf = []
        data = {'token':ClIENT_TOKEN,'SN':sn}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        request = HTTPRequest(url=self.url_list['updateStudent'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_updateStudents)
    def resp_updateStudents(self,response):
        if response.error:
            print("Error:", response.error)
        else:
            students = json.loads(response.body)
            if students['timeStamp']  == self.settings['last_updatestd_st'] :
                return;
            self.stdudents_buf = []
            self.settings['last_updatestd_st'] = students['timeStamp']
            self.db_handler.update_serverConnection_setting(self.settings)
            print(students)
            self.stdudents_buf = students['users']

            if self.dev_process == '' :
                return

            if students['op_code'] == 'add' or students['op_code'] == 'change':
                self.dev_process('updateUser',self.stdudents_buf)
            elif students['op_code'] == 'dele' :
                self.dev_process('deleteUser', self.stdudents_buf)
            else :
                print("resp_updateStudents : Error CMD !!!")

    def newRecord(self,record,sn):
        data = {'token':ClIENT_TOKEN,'SN':sn,'record':urllib.parse.urlencode(record).encode('utf-8')}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        print("newRecord data_send2Server : ", data_send)
        request = HTTPRequest(url=self.url_list['NewRecord'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_newRecord)
    def resp_newRecord(self,response):
        if response.error:
            print("Error:", response.error)
        else:
            print("resp_newRecord : ", response.body)

    def syncAttLog(self,records,sn):
        tmpbuf = json.dumps(records)
        data = {'token':ClIENT_TOKEN,'SN':sn,'records':tmpbuf}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        print("syncAttLog data_send2Server : ", data_send)
        request = HTTPRequest(url=self.url_list['SyncAttLog'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_syncAttLog)
    def resp_syncAttLog(self,response):
        if response.error:
            print("Error:", response.error)
            print("Error:", response.body)
        else:
            print("resp_syncAttLog : ", response.body)


    def getServerCmd(self,sn):
        data = {'token':ClIENT_TOKEN,'SN':sn}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        request = HTTPRequest(url=self.url_list['GetCmd'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_getServerCmd)

    def resp_getServerCmd(self,response):
        if response.error:
            print("Error:", response.error)
        else:
            cmds = json.loads(response.body)
            print("resp_getServerCmd :" , cmds)
            for cmd in cmds['cmd_list'] :
                print(cmd)
                if cmd == 'updatestd':
                    self.updateStudents(sn='all_devices')
                elif cmd == 'getErroLog':
                    self.sendErrorLogs(start=cmds[cmd]['s_timeStamp'],end=cmds[cmd]['e_timeStamp'])
                else :
                    if self.dev_process != '' :
                        self.dev_process(cmd,para)

    def sendErrorLogs(self,start,end):
        logs = self.db_handler.get_error_logs(start,end)
        tmpbuf = json.dumps(logs)
        data = {'token': ClIENT_TOKEN,'logs':tmpbuf}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        request = HTTPRequest(url=self.url_list['sendErrorLogs'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_sendErrorLogs)
    def resp_sendErrorLogs(self, response):
        if response.error:
            print("Error:", response.error)
        else:
            print(response.body)


if __name__ == "__main__":

    def devProcess(cmd,value) :
        print('devProcess : ',cmd)
        print(value)
        print("---------------------------------")

    sn = '3637165101475'
    record1 = {
        'PIN': '101010101010',
        'TIME': '2017-08-03 11:30:28',
        'STATUS': 255,
        'VERIFY': '2',
        'WORKCODE': '0',
        'RESERVED1': '0',
        'RESERVED2': '0'
    }
    record2 = {
        'PIN': '101010102020',
        'TIME': '2017-08-03 11:35:28',
        'STATUS': 255,
        'VERIFY': '2',
        'WORKCODE': '0',
        'RESERVED1': '0',
        'RESERVED2': '0'
    }
    SvHd = ServerHandler(devProcess)
    #SvHd.updateStudents()
    #SvHd.newRecord(record1,sn)
    data = []
    data.append(record1)
    data.append(record2)
    SvHd.syncAttLog(records=data,sn=sn)
    #SvHd.getServerCmd(sn)
    #SvHd.updateStudents(sn)
    IOLoop.instance().start()
