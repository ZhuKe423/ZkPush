# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
from devicesSetting import GetDeviceHandler,DeviceHandler

class CdataHandler(RequestHandler):
    def process_options(self,type,dev_handler):
        if type == 'all' :
            for (k,v) in dev_handler.get_deviceOptions_all().items() :
                self.write( format("%s=%s\n" % (k,v)))
        else :
            pass


    def process_talbes(self,table,content,dev_handler):
        if table == 'ATTLOG':
            tmp_list = content.split('\n')
            #print(tmp_list)
            for tmp_data in tmp_list:
                if tmp_data != '' :
                    it_data = tmp_data.split('\t')
                    data = {
                        'PIN' : it_data[0],
                        'TIME' : it_data[1],
                        'STATUS': int(it_data[2]),
                        'VERIFY' : it_data[3],
                        'WORKCODE' : it_data[4],
                        'RESERVED1': it_data[5],
                        'RESERVED2': it_data[6],
                    }
                    dev_handler.new_record_log(data)
                else :
                    dev_handler.new_record_log('')

        elif table == 'OPERLOG' :
            if content[0:4] == 'USER':
                tmp_data = content.split('\t')
                for it in tmp_data :
                    session = it.split('=')
                    data[session[0]] = session[1]
                #data['Name'] = unicode(data['Name'], 'utf8')
                #print(data)
        else :
            pass


    def get(self, input):
        args = self.request.arguments
        getArgs = {}
        for a in args:
            getArgs[a] = self.get_argument(a)

        self.set_header('Content-Type', 'text/plain; charset="utf-8"')
        self.set_header("cache-control", "private, max-age=0")
        sn = ''
        if 'SN' in getArgs :
            sn = self.get_argument('SN')
            line1 = 'GET OPTION FROM: ' + sn + '\n'
            self.write(line1)
        else :
            return

        dev_handler = GetDeviceHandler(sn)
        if 'options' in getArgs :
            CdataHandler.process_options(self,getArgs['options'],dev_handler)
        if 'table' in getArgs :
            CdataHandler.process_talbes(self,getArgs['table'],dev_handler)


    def post(self, post):
        #print(self.request.body)
        content = str(self.request.body,encoding = "gbk")
        args = self.request.arguments
        getArgs = {}
        for a in args:
            getArgs[a] = self.get_argument(a)

        #print(getArgs)
        sn = ''
        if 'SN' in getArgs :
            sn = self.get_argument('SN')
        else :
            return

        dev_handler = GetDeviceHandler(sn)
        #print('The checking in records data: ', content, '\n')

        if 'table' in getArgs :
            CdataHandler.process_talbes(self,getArgs['table'],content,dev_handler)

        self.write('OK')
