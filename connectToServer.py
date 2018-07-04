# -*- coding: utf-8 -*-

#import urllib2
from tornado import curl_httpclient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from databaseHandler import DB_Handler,DataBaseHandler
import time
import urllib,json

Default_URL = {
        'updateStudent' : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/updateStudent',
        'SyncAttLog'    : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/syncRecord',
        'NewRecord'     : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/newRecord',
        'getStudent'    : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/getStudent',
        'GetCmd'        : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/getCommand',
        'sendErrorLogs' : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/',
    }

#PROXY_HOST = '135.251.103.45'
#PROXY_PORT = 8080
ClIENT_TOKEN = 'gh_2837e31e28ed'

Default_ServerConnection_Setting = {
        'RaspyNum'              : "DingYi-0001",
        'last_updatestd_st'     : 0,           #服务器传过来的更新时间戳

    }

class ServerHandler() :
    dev_process = ''

    def __init__(self,dev_callback):
        self.url_list = Default_URL;
        self.http_client = CurlAsyncHTTPClient()
        self.stdudents_update_buf = []
        self.stdudents_dele_buf = []
        self.db_handler = DB_Handler
        self.settings = self.db_handler.get_serverConnection_setting(Default_ServerConnection_Setting)
        self.dev_process =dev_callback


    def updateStudents(self,sn,lasTime = 0,isForce = False):
        data = {'token':ClIENT_TOKEN,'SN':sn,'timeStamp':lasTime}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        #request = HTTPRequest(url=self.url_list['updateStudent'],method='POST', body=data_send,
        #                     follow_redirects=False,proxy_host=PROXY_HOST, proxy_port=PROXY_PORT,
        #                     connect_timeout=200, request_timeout=600)
        request = HTTPRequest(url=self.url_list['updateStudent'], method='POST', body=data_send,
                            follow_redirects = False,connect_timeout = 200, request_timeout = 600)
        if isForce :
            self.http_client.fetch(request, self.resp_forceUpdateStudents)
        else :
            self.http_client.fetch(request, self.resp_updateStudents)

    def resp_updateStudents(self,response):
        if response.error:
            print("Error resp_updateStudents:", response.error)
            record = {'SN': 'XXXXXX', 'type': 'HTTP_RESP_UpdateStu', 'content': response.error, 'wTime': time.time()}
            self.db_handler.add_error_log(record)
        else:
            #print("resp_updateStudents: ",response.body)
            students = json.loads(response.body.decode('gbk'))
            if ('timeStamp' not in students) :
                #print("resp_updateStuednets : invalid  response.body:",students)
                return;

            self.stdudents_update_buf = []
            self.stdudents_dele_buf = []
            self.settings['last_updatestd_st'] = students['timeStamp']
            self.db_handler.update_serverConnection_setting(self.settings)
            #print("resp_updateStudents",students)

            if self.dev_process == '' :
                return

            if 'users' in students :
                self.stdudents_update_buf = {'timeStamp': students['timeStamp'], 'users':students['users']}
                self.dev_process('updateUser',self.stdudents_update_buf)

            if 'dele_users' in students :
                self.stdudents_dele_buf = {'timeStamp': students['timeStamp'], 'users':students['dele_users']}
                self.dev_process('deleteUser', self.stdudents_dele_buf)
            #print("resp_updateStudents : END !!!")

    def resp_forceUpdateStudents(self,response):
        if response.error:
            #print("Error resp_forceUpdateStudents: ", response.error)
            record = {'SN': 'XXXXXX', 'type': 'HTTP_RESP_ForceUpdateStu', 'content': response.error, 'wTime': time.time()}
            self.db_handler.add_error_log(record)
        else:
            students = json.loads(response.body.decode('gbk'))
            if 'users' in students :
                #print(students['users'])
                self.stdudents_update_buf = {'timeStamp': students['timeStamp'], 'users':students['users']}
                self.dev_process('updateUser',value = self.stdudents_update_buf,sn=students['SN'])


    def newRecord(self,record,sn):
        data = {'token':ClIENT_TOKEN,'SN':sn,'record':urllib.parse.urlencode(record).encode('utf-8')}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        #print("newRecord data_send2Server : ", data_send)
        #request = HTTPRequest(url=self.url_list['NewRecord'],method='POST', body=data_send,
        #                      follow_redirects=False,proxy_host=PROXY_HOST, proxy_port=PROXY_PORT,
        #                      connect_timeout=200, request_timeout=600)
        request = HTTPRequest(url=self.url_list['NewRecord'],method='POST', body=data_send,
                              follow_redirects=False,connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_newRecord)
    def resp_newRecord(self,response):
        if response.error:
            #print("Error resp_newRecord:", response.error)
            record = {'SN': 'XXXXXX', 'type': 'HTTP_RESP_NewRecord', 'content': response.error, 'wTime': time.time()}
            self.db_handler.add_error_log(record)
        else:
            #print("resp_newRecord : ", response.body)
            return

    def syncAttLog(self,records,sn):
        tmpbuf = json.dumps(records)
        data = {'token':ClIENT_TOKEN,'SN':sn,'records':tmpbuf}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        #print("syncAttLog data_send2Server : ", data_send," ,records len = %d" % len(records))
        #request = HTTPRequest(url=self.url_list['SyncAttLog'],method='POST', body=data_send,
        #                      follow_redirects=False,proxy_host=PROXY_HOST, proxy_port=PROXY_PORT,
        #                      connect_timeout=200, request_timeout=600)
        request = HTTPRequest(url=self.url_list['SyncAttLog'],method='POST', body=data_send,
                              follow_redirects=False,connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_syncAttLog)
    def resp_syncAttLog(self,response):
        if response.error:
            #print("Error resp_syncAttLog:", response.error)
            #print("Error resp_syncAttLog:", response.body)
            record = {'SN': 'XXXXXX', 'type': 'HTTP_RESP_SyncAttLog', 'content': response.error, 'wTime': time.time()}
            self.db_handler.add_error_log(record)
        else:
            #print("resp_syncAttLog : ", response.body)
            data = json.loads(response.body.decode('utf-8'))
            self.dev_process('respSyncAttLog', value='', sn=data['SN'])

    def getServerCmd(self,sn):
        data = {'token':ClIENT_TOKEN,'SN':sn}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        #request = HTTPRequest(url=self.url_list['GetCmd'],method='POST', body=data_send,
        #                      follow_redirects=False,proxy_host=PROXY_HOST, proxy_port=PROXY_PORT,
        #                      connect_timeout=200, request_timeout=600)
        request = HTTPRequest(url=self.url_list['GetCmd'],method='POST', body=data_send,
                            follow_redirects=False,connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_getServerCmd)

    def resp_getServerCmd(self,response):
        if response.error:
            #print("Error resp_getServerCmd:", response.error)
            #print("Error resp_getServerCmd body:", response.body)
            # record = {'SN':'','type': '', 'content':'','wTime':}
            record = {'SN':'XXXXXX','type':'HTTP_RESP_GetServerCmd','content':response.error,'wTime':time.time()}
            self.db_handler.add_error_log(record)
        else:
            #print("resp_getServerCmd",str(response.body))

            data = json.loads(response.body.decode('utf-8'))
            #print("resp_getServerCmd :" , data)
            if 'cmd_list' in data :
                cmds = data['cmd_list']
                for cmd in cmds:
                    #print(cmd)
                    if cmd == 'updatestd':
                        self.updateStudents(sn='all_devices')
                    elif cmd == 'getErroLog':
                        self.sendErrorLogs(start=cmds[cmd]['s_timeStamp'],end=cmds[cmd]['e_timeStamp'])
                    else :
                        if self.dev_process != '' :
                            #print("resp_getServerCmd: value :",cmds[cmd])
                            value = cmds[cmd]
                            self.dev_process(cmd,value)


    def sendErrorLogs(self,start,end):
        logs = self.db_handler.get_error_logs(start,end)
        tmpbuf = json.dumps(logs)
        data = {'token': ClIENT_TOKEN,'logs':tmpbuf}
        data_send = urllib.parse.urlencode(data).encode('utf-8')
        #request = HTTPRequest(url=self.url_list['sendErrorLogs'],method='POST', body=data_send,
        #                      follow_redirects=False,proxy_host=PROXY_HOST, proxy_port=PROXY_PORT,
        #                      connect_timeout=200, request_timeout=600)
        request = HTTPRequest(url=self.url_list['sendErrorLogs'],method='POST', body=data_send,
                              follow_redirects=False,connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_sendErrorLogs)
    def resp_sendErrorLogs(self, response):
        if response.error:
            #print("Error resp_sendErrorLogs:", response.error)
            record = {'SN': 'XXXXXX', 'type': 'HTTP_RESP_SendErrorLogs', 'content': response.error, 'wTime': time.time()}
            self.db_handler.add_error_log(record)
        else:
            print(response.body)


if __name__ == "__main__":

    def devProcess(cmd,value) :
        #print('devProcess : ',cmd)
        #print(value)
        #print("---------------------------------")
        pass
    
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
    #SvHd.syncAttLog(records=data,sn=sn)
    #SvHd.getServerCmd(sn)
    SvHd.updateStudents(sn)
    IOLoop.instance().start()
