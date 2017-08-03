
import textwrap
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from devicecmdHandler import DeviceCmdHandler
from cdataHandler import CdataHandler
from getrequestHandler import GetrequestHandler
from tornado.options import define, options
from databaseHandler import DataBaseHandler,DB_Handler
from connectToServer import ServerHandler,SERVER_Handler

define("port", default=8002, help="run on the given port", type=int)


if __name__ == "__main__":
    tornado.options.parse_command_line()

    app = tornado.web.Application(
        handlers=[
            (r"/iclock/cdata?(.*)",CdataHandler),
            (r"/iclock/getrequest?(.*)", GetrequestHandler),
            (r"/iclock/devicecmd?(.*)", DeviceCmdHandler)
        ]
    )
    SvHd = SERVER_Handler
    #SvHd.updateStudents()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()