# -*- coding: utf-8 -*-

#import urllib2
from tornado import curl_httpclient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
import urllib

Default_URL = {
        'updateStudent' : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/updateStudent',
        'SyncAttLog'    : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/syncRecord',
        'NewRecord'     : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/newRecord',
        'getStudent'    : 'http://www.jzk12.com/weiphp30/index.php?s=/addon/DailyTime/DailyTime/getStudent',
        'GetCmd'        : 'http://',
    }

ClIENT_TOKEN = 'gh_2837e31e28ed'

class ServerHandler() :

    def __init__(self):
        self.url_list = Default_URL;
        self.http_client = CurlAsyncHTTPClient()
        self.stdudents_buf = []
    def updateStudents(self,sn,fresh=False):
        if (len(self.stdudents_buf) != 0) and (False == fresh) :
            return;
        self.stdudents_buf = []
        data = {'token':ClIENT_TOKEN,'SN':sn}
        data_send = urllib.parse.urlencode(data)
        request = HTTPRequest(url=self.url_list['updateStudent'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_updateStudents)
    def resp_updateStudents(self,response):
        #if response.error:
        #    print("Error:", response.error)
        #else:
            print("resp_updateStudents : ",response.body)
    def get_updated_students(self):
        return self.stdudents_buf


    def newRecord(self,record,sn):
        data = {'token':ClIENT_TOKEN,'SN':sn,'record':record}
        data_send = urllib.parse.urlencode(data)
        print("data_send : ", data_send)
        request = HTTPRequest(url=self.url_list['NewRecord'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_newRecord)
    def resp_newRecord(self,response):
        #if response.error:
        #    print("Error:", response.error)
        #else:
            print("resp_newRecord : ", response.body)

    def syncAttLog(self,records,sn):
        data = {'token':ClIENT_TOKEN,'SN':sn,'records':records}
        data_send = urllib.parse.urlencode(data)
        request = HTTPRequest(url=self.url_list['SyncAttLog'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_syncAttLog)
    def resp_syncAttLog(self,response):
        #if response.error:
        #    print("Error:", response.error)
        #else:
            print("resp_syncAttLog : ", response.body)


    def getServerCmd(self,sn):
        data = {'token':ClIENT_TOKEN,'SN':sn}
        data_send = urllib.parse.urlencode(data)
        request = HTTPRequest(url=self.url_list['GetCmd'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.resp_getServerCmd)
    def resp_getServerCmd(self,response):
        #if response.error:
        #    print("Error:", response.error)
        #else:
            print("resp_getServerCmd : ", response.body)


SERVER_Handler = ServerHandler();

if __name__ == "__main__":
    sn = '3637165101475'
    record = {
        'PIN': '101010101010',
        'TIME': '2017-08-03 11:30:28',
        'STATUS': 255,
        'VERIFY': '2',
        'WORKCODE': '0',
        'RESERVED1': '0',
        'RESERVED2': '0'
    }

    SvHd = SERVER_Handler
    #SvHd.updateStudents()
    SvHd.newRecord(record,sn)
    IOLoop.instance().start()
