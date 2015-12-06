#!/usr/bin/env python3
# coding=utf-8
#
# Copyright 2015 Kuo Hsuan Hsu
import logging
import os.path

import tornado.web
import tornado.options
from tornado.ioloop import IOLoop
from tornado.options import define, options
from jinja2 import Environment, FileSystemLoader
import momoko

import handler.home


define('debug', default=False, help="server mode")
define('port', default=8080, help="run on given port")
define('cookie_secret', help="encrypt with the secret key")
define('db_host', default="localhost", help="db host")
define('db_port', default=5432, help="db port")
define('db_database', help="db used")
define('db_user', help="db username")
define('db_password', help="db Password")
define('i18n_path', help="i18n file directory")


class Application(tornado.web.Application):
    def __init__(self, ioloop):
        settings = dict(
            debug = options.debug,
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            media_path = os.path.join(os.path.dirname(__file__), "data"),
            xsrf_cookies=True,
            cookie_secret = options.cookie_secret,
            jinja2=Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
                autoescape = True,
                trim_blocks = True),
        )

        handlers = [
            (r"/", handler.home.HomePage),
            (r"/search", handler.home.SearchPage),

            # Debug Mode
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': settings['static_path']}),
            (r'/article/(.*)', tornado.web.StaticFileHandler, {'path': settings['media_path']}),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

        # DB settings
        dsn = 'dbname={} user={} password={} host={} port={}'
        dsn = dsn.format(options.db_database,
                         options.db_user,
                         options.db_password,
                         options.db_host,
                         options.db_port)

        self.db = momoko.Pool(
            dsn=dsn,
            size=1,
            max_size=3,
            ioloop=ioloop,
            setsession=("SET TIME ZONE GMT",),
            raise_connect_errors=False,
        )

        # Have one global memcache controller
        # self.mc = memcache.Client(["127.0.0.1:11211"])


def main():
    # Initialize the application and ioloop instance
    options.parse_config_file('config.py')
    ioloop = IOLoop.instance()
    application = Application(ioloop)

    # Logging settings
    if options.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('server runs in debug mode')
    logging.info("server started on port {0}".format(options.port))

    # This is a one way to run ioloop in sync
    future = application.db.connect()
    ioloop.add_future(future, lambda f: ioloop.stop())
    ioloop.start()

    # Locale settings
    #tornado.locale.load_gettext_translations(options.i18n_path, "z")
    tornado.locale.set_default_locale('zh_TW')

    application.listen(options.port)
    ioloop.start()


if __name__ == "__main__":
    main()
