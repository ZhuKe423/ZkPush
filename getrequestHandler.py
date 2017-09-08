# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
from devicesSetting import GetDeviceHandler,DeviceHandler

class GetrequestHandler(RequestHandler):
    def parse_device_info(self,strDeviceInfo,dev_handler):
        info = str(strDeviceInfo).split(',');
        devInfo = {
            'deviceVersion' : info[0],
            'userCount' : int(info[1]),
            'fingerprint' : int(info[2]),
            'recordCount' : int(info[3]),
            'ipAddr' : info[4]
        }
        #dev_handler.updateInfor(devInfo)
        print("getRequestInfor : " , devInfo)

    def get(self, input):
        args = self.request.arguments
        getArgs = {}
        for a in args:
            getArgs[a] = self.get_argument(a)

        sn = ''
        if 'SN' in getArgs:
            sn = self.get_argument('SN')
        else :
            return;

        dev_handler = GetDeviceHandler(sn)

        if 'INFO' in getArgs :
            print("HeartBeatHandler get ###:")
            GetrequestHandler.parse_device_info(self,getArgs['INFO'],dev_handler)
        else :
            dev_handler.interalBeat()
            cmds = []
            dev_handler.get_cmd_list(cmds)
            for cmd in cmds:
                self.write(cmd.encode('gbk'))
                print("sn=%s cmd : %s" % (sn,cmd))
            pass


        # text = self.get_argument('text')
        # width = self.get_argument('width', 40)
        # self.write(textwrap.fill(text, int(width)))

        # self.write('C:126:CLEAR LOG\n')