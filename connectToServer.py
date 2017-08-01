# -*- coding: utf-8 -*-

#import urllib2
from tornado import curl_httpclient
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
import json

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

    def updateStudents(self):
        data = {'token':ClIENT_TOKEN}
        data_send = json.dumps(data)
        request = HTTPRequest(url=self.url_list['updateStudent'],method='POST', body=data_send,
                              follow_redirects=False,proxy_host='135.251.103.45', proxy_port=8080,
                              connect_timeout=200, request_timeout=600)
        self.http_client.fetch(request, self.print_response)

    def print_response(self,response):
        print(response.body)



SERVER_Handler = ServerHandler();





if __name__ == "__main__":
    SvHd = SERVER_Handler
    SvHd.updateStudents()
    IOLoop.instance().start()
