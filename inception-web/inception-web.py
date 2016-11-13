#!/bin/env python
# -*- coding: utf-8 -*-
#

import MySQLdb
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import time
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('inception-web.conf')

app = Flask(__name__)

@app.route('/', methods=["get"])
def inception_home():
	return render_template("index.html")

@app.route('/login', methods=["post","get"])
def inception_login():
	if request.method == "GET":
		return render_template("index.html")

	code = request.values.get("dyncode","")
	if code:
		sql = "select code from dyncode where code=%d" % int(code)
		code_exist = sqlaudit_query(sql, "select")
		now = int(time.time())
		code_timeout = now - int(code)
		if code_exist and code_timeout < int(config.get("inception-web","code-timeout")):
			return redirect(url_for('inception_web', icode=code))
		else:
			return render_template("index.html", errmsg=u"此动态验证码无效!")
	return render_template("index.html", errmsg=u"请先输入动态验证码!")

@app.route('/inception/<icode>',methods=["get"])
def inception_web(icode):
	return render_template("audit.html")

@app.route('/sqlaudit',methods=["post","get"])
def inception_audit():
	code = int(request.headers["Referer"].split('/')[-1])
	now = int(time.time())
	code_timeout = now - code
	if code_timeout < int(config.get("inception-web","code-timeout")):
		online = {
			"user": "root",
			"password": "",
			"instance": request.values.get("dbinstance",""),
			"db": request.values.get("dbname",""),
			"sql": request.values.get("auditcontent",""),
			"operator": request.values.get("operator",""),
			"redmineissue": int(request.values.get("redmineissue",""))
		}
		inception_server = {
			"host": config.get("inception-server","host"),
			"user": config.get("inception-server","user"),
			"passwd": config.get("inception-server","password"),
			"db": config.get("inception-server","db"),
			"port": int(config.get("inception-server","port")),
			"charset": config.get("inception-server","charset")
		}
		idsn = "/*--user=" + online["user"] + ";--password=" + online["password"] + ";--host=" + online["instance"].split(':')[0] + ";--execute=1;--port=" + online["instance"].split(':')[1] + ";*/"
		istart = "inception_magic_start;"
		icommit = "inception_magic_commit;"
		isql = idsn + istart + online["sql"] + icommit

		iconn = MySQLdb.connect(**inception_server)
		icur = iconn.cursor()
		iquery = icur.execute(isql)
		ioutput = icur.fetchall()

		audit_result = []
		errlevels = []
		for row in ioutput:
			r_id = row[0]
			r_errlevel = row[2]
			r_stagestatus = row[3]
			if len(row[5].split()) >= 3:
				r_sql = row[5].split()[0] + " " + row[5].split()[1] + " " + row[5].split()[2].replace('`','')
			else:
				r_sql = row[5]
			r_exetime = row[9]
			r_err = row[4].replace('\n',' ')
			audit_result.append([r_id, r_stagestatus, r_sql, r_exetime, r_err])
			errlevels.append(r_errlevel)
			if r_errlevel != 0:
				sql = 'insert into operator_log(operator,redmineissue,errlevel,errmsg) values("%s",%d,%d,"%s");' %(online["operator"], online["redmineissue"], r_errlevel, r_err)
				sqlaudit_query(sql, "insert")
		icur.close()
		iconn.close()

		if sum(errlevels) == 0:
			sql = 'insert into inception_log(dbinstance,dbname,ioutput) values("%s","%s","%s");' %(online["instance"], online["db"], audit_result)
			sqlaudit_query(sql, "insert")

		return jsonify(audit_result)

def sqlaudit_query(sql, sqltype):
	inception_web = {
		"host": config.get("inception-web","host"),
		"user": config.get("inception-web","user"),
		"passwd": config.get("inception-web","password"),
		"db": config.get("inception-web","db"),
		"port": int(config.get("inception-web","port")),
		"charset": config.get("inception-web","charset")
	}
	conn = MySQLdb.connect(**inception_web)
	cur = conn.cursor()
	query = cur.execute(sql)
	if sqltype == "select":
		result = cur.fetchone()
		if result:
			return result[0]
	conn.commit()
	cur.close()
	conn.close()

@app.route('/sqlguide', methods=["get"])
def sqlguide():
	return render_template("sqlguide.html")

@app.route('/icoder', methods=["get"])
def coder():
	return render_template("coder.html")

@app.route('/icode', methods=["get"])
def code():
	code = int(time.time())
	sql = "insert into dyncode(code) values(%d);" % code
	sqlaudit_query(sql, "insert")
	return jsonify(code)

if __name__ == '__main__':
	app.run('0.0.0.0',debug=True)
