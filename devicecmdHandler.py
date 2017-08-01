# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
from devicesSetting import GetDeviceHandler,DeviceHandler
import json
class DeviceCmdHandler(RequestHandler):
    def post(self, post):
        content = str(self.request.body,encoding = "utf-8")
        print("Device CMD Response:")
        #print(content)
        lines = content.split('\n')
        print('The device command post data: ', lines)
        args = self.request.arguments
        getArgs = {}
        for a in args:
            getArgs[a] = self.get_argument(a)
        print(getArgs)
        sn = ''
        if 'SN' in getArgs :
            sn = self.get_argument('SN')
        else :
            return
        print("DeviceCmdHandler:: in processing!!!")
        dev_handler = GetDeviceHandler(sn)
        dev_handler.process_response(lines)

        self.write('OK')