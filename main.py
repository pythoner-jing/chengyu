#!/usr/bin/env python
#coding:utf-8

import tornado.web
import torndb
import os
import sys
import hashlib
import lxml
import time
from lxml import etree

from tornado.options import define, options

if "SERVER_SOFTWARE" in os.environ:
	from sae.const import (MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
	DEBUG = False
else:
	MYSQL_HOST = "localhost"
	MYSQL_PORT = 3306
	MYSQL_USER = "root"
	MYSQL_PASS = ""
	MYSQL_DB = "chengyu"
	DEBUG = True
	import tornado.ioloop

define("port", default = 8888)
define("token", default = "britten")

DB = torndb.Connection(
	"%s:%s" % (MYSQL_HOST, str(MYSQL_PORT)),
	MYSQL_DB,
	MYSQL_USER,
	MYSQL_PASS,
	max_idle_time = 5,
)

class TestHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("index.html")

	def post(self):
		args = self.request.arguments
		word = args.get("word", [""])[0].strip()
		query_sql = "SELECT meaning FROM Chengyu WHERE word=%s"
		rs = DB.query(query_sql, word)
		try:
			meaning = rs[0]["meaning"]
		except Exception, e:
			meaning = u"找不到释义"
		self.write(meaning)

class WXHandler(tornado.web.RequestHandler):
	def get(self):
		args = self.request.arguments
		signature = args.get("signature")[0]
		timestamp = args.get("timestamp")[0]
		nonce = args.get("nonce")[0]
		echostr = args.get("echostr")[0]

		token = options.token
		array = [token, timestamp, nonce]
		array.sort()
		sha1 = hashlib.sha1()
		map(sha1.update, array)
		hashcode = sha1.hexdigest()

		if hashcode == signature:
			self.write(echostr)

		reply_data = dict(
			to_user = from_user,
			from_user = to_user,
			content = content,
			create_time = int(time.time()),
		)

		return self.render("reply.xml", **reply_data)

	def post(self):
		raw_data = self.request.body
		xml = etree.fromstring(raw_data)
		content = xml.find("Content").text
		msg_type = xml.find("MsgType").text
		from_user = xml.find("FromUserName").text
		to_user = xml.find("ToUserName").text

		query_sql = "SELECT meaning FROM Chengyu WHERE word=%s"
		rs = DB.query(query_sql, content.strip())
		try:
			meaning = rs[0]["meaning"]
		except Exception, e:
			meaning = u"找不到释义"

		reply_data = dict(
			to_user = from_user,
			from_user = to_user,
			content = meaning,
			create_time = int(time.time()),
		)
		return self.render("reply.xml", **reply_data)

URLS = [
	(r"^/$", TestHandler),
	(r"^/wx$", WXHandler),
]

SETTINGS = dict(
	template_path = os.path.join(os.path.dirname(__file__), "template"),
	static_path = os.path.join(os.path.dirname(__file__), "static"),
	debug = DEBUG,
)

class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, URLS, **SETTINGS)

if __name__ == "__main__" and DEBUG:
	Application().listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
