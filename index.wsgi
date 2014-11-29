#!/usr/bin/env python
#coding:utf-8

import tornado.web
import tornado.wsgi
import sae
import main

app = tornado.wsgi.WSGIApplication(main.URLS, **main.SETTINGS)

application = sae.create_wsgi_app(app)
#application = tornado.web.Application(main.URLS, **main.SETTINGS)