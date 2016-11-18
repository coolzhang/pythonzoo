#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import MySQLdb
from optparse import OptionParser

USAGE = """%prog -  SQL Audit Tool based on Inception
e.g.:
%prog --sqltext=run.sql --host=127.0.0.1 --port=3306

Note: Firstly to start Inception Server and then to config the connection arguments in the following incetption_config variable.
"""
VERSION = "%prog Alpha"

optparser = OptionParser(usage=USAGE, version=VERSION)
optparser.add_option("-f", "--sqltext", action="store", dest="sqltext", help="Given a sql text", metavar="FILE") 
optparser.add_option("-H", "--host", action="store", dest="host", default="127.0.0.1", help="IP of MySQL server. Default: 127.0.0.1") 
optparser.add_option("-P", "--port", action="store", dest="port", default="3306", help="Port of MySQL server. Default: 3306") 
optparser.add_option("-u", "--user", action="store", dest="user", default="admin", help="Admin account") 
optparser.add_option("-p", "--password", action="store", dest="password", default="", help="Password of admin") 
(options,args) = optparser.parse_args()

dsn = "/*--user=" + options.user + ";--password=" + options.password + ";--host=" + options.host + ";--execute=1;--port=" + options.port + ";*/"
istart = "inception_magic_start;"
icommit = "inception_magic_commit;"
inception_config = {
	"host": "127.0.0.1",
	"user": "",
	"passwd": "",
	"db": "",
	"port": 33066,
	"charset": "utf8"
}

if options.sqltext:
	with open(options.sqltext, 'r') as file:
		sql = dsn + istart + file.read().replace('\n','') + icommit
	
	try:
		conn = MySQLdb.connect(**inception_config)
		cur = conn.cursor()
		query = cur.execute(sql)
		result = cur.fetchall()
		field_names = [ i[0] for i in cur.description ]
		f_id, f_stagestatus, f_sql, f_exetime, f_err  = field_names[0],field_names[3],field_names[5],field_names[9],field_names[4]

		print "-" * 131
		print "| %-5s | %-26s | %-43s | %-12s | %-29s |" %(f_id, f_stagestatus, f_sql, f_exetime, f_err)
		print "-" * 131
		for row in result:
			r_id = row[0]
			r_stagestatus = row[3]
			r_sql = row[5].split()[0] + " " + row[5].split()[1] + " " + row[5].split()[2]
			r_exetime = row[9]
			r_err = row[4].split('\n')
			print "| %-5s | %-26s | %-43s | %-12s | %-29s" %(r_id,r_stagestatus,r_sql,r_exetime,'... ... ... ... ... ... ... ...')
			print "\\"
			for err in r_err:
				print " --> %s" % err
		        print "-" * 131
		cur.close()
		conn.close()
	except MySQLdb.Error, e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])
else:
	print optparser.error("option --sqltext (-f) is mandatory")
