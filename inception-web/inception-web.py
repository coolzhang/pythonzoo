#!/bin/env python
# -*- coding: utf-8 -*-
#

import MySQLdb
from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import time
import ConfigParser
import os
import logging
from logging.handlers import RotatingFileHandler

config = ConfigParser.SafeConfigParser()
if not os.path.exists('./inception-web.conf'):
	config.add_section('inception-server')
	config.set('inception-server','user','root')
	config.set('inception-server','password','')
	config.set('inception-server','host','127.0.0.1')
	config.set('inception-server','port','3306')
	config.set('inception-server','charsetr','utf8')
	config.add_section('inception-web')
	config.set('inception-web','user','root')
	config.set('inception-web','password','')
	config.set('inception-web','host','127.0.0.1')
	config.set('inception-web','port','3306')
	config.set('inception-web','db','test')
	config.set('inception-web','charsetr','utf8')
	config.set('inception-web','code-timeout','3600')
	with open('./inception-web.conf', 'wb') as configfile:
		config.write(configfile)
config.read('./inception-web.conf')

app = Flask(__name__)
@app.route('/', methods=['get'])
def inception_home():
	return render_template('index.html')

@app.route('/login', methods=['post','get'])
def inception_login():
	if request.method == 'GET':
		return render_template('index.html')

	code = request.values.get('dyncode','')
	if code:
		if code.isdigit():
			sql = 'select code from dyncode where code=%d' % int(code)
			code_exist = sqlaudit_query(sql, 'select')
			now = int(time.time())
			code_timeout = now - int(code)
			if code_exist:
				if code_timeout < config.getint('inception-web','code-timeout'):
					return redirect(url_for('inception_web', icode=code))
				else:
					return render_template('index.html', errmsg=u'此动态验证码已过期，请联系DBA!')
			else:
				return render_template('index.html', errmsg=u'此动态验证码无效，不要尝试破解哦!')
		else:
			return render_template('index.html', errmsg=u'此动态验证码不合法!')
	else:
		return render_template('index.html', errmsg=u'请先输入动态验证码!')

@app.route('/inception/<icode>',methods=['get'])
def inception_web(icode):
	return render_template('audit.html')

@app.route('/sqlaudit',methods=['post','get'])
def inception_audit():
	code = int(request.headers['Referer'].split('/')[-1])
	now = int(time.time())
	code_timeout = now - code
	if code_timeout < config.getint('inception-web','code-timeout'):
		online = {
			"user": "inception",
			"password": "JvnX9qc2NvkuHdxwUxvxIMN5C",
			"instance": request.values.get("dbinstance",""),
			"database": request.values.get("dbname",""),
			"sql": request.values.get("auditcontent",""),
			"operator": request.values.get("operator",""),
			"redmineissue": request.values.get("redmineissue","")
		}
		inception_server = {
			"host": config.get("inception-server","host"),
			"user": config.get("inception-server","user"),
			"passwd": config.get("inception-server","password"),
			"db": config.get("inception-server","db"),
			"port": int(config.get("inception-server","port")),
			"charset": config.get("inception-server","charset")
		}
		idsn = '/*--user=' + online['user'] + ';--password=' + online['password'] + ';--host=' + online['instance'].split(':')[0] + ';--execute=1;--remote-backup=0;--port=' + online['instance'].split(':')[1] + ';*/'
		istart = 'inception_magic_start;'
		icommit = 'inception_magic_commit;'
		isql = idsn + istart + online['sql'] + icommit

		try:
			iconn = MySQLdb.connect(**inception_server)
			icur = iconn.cursor()
			iquery = icur.execute(isql)
			irows = icur.fetchall()
			audit_result = []
			errlevels = []
			for row in irows:
				r_id = row[0]
				r_errlevel = row[2]
				r_stagestatus = row[3]
				if len(row[5].split()) >= 3:
					r_sql = row[5].split()[0] + ' ' + row[5].split()[1] + ' ' + row[5].split()[2].replace('`','')
				else:
					r_sql = row[5]
				r_exetime = row[9]
				r_err = row[4].replace('\n',';')
				audit_result.append([r_id, r_stagestatus, r_sql, r_exetime, r_err])
				errlevels.append(r_errlevel)
				if r_errlevel != 0:
					sql = 'insert into operator_log(operator,redmineissue,errlevel,errmsg) values("%s",%s,%d,"%s");' %(online['operator'], online['redmineissue'], r_errlevel, r_err)
					sqlaudit_query(sql, 'insert')
			icur.close()

			if sum(errlevels) == 0:
				sql = 'insert into inception_log(dbinstance,dbname,ioutput) values("%s","%s","%s");' %(online["instance"], online["database"], audit_result)
				sqlaudit_query(sql, 'insert')
			return jsonify(audit_result)
		except MySQLdb.Error, err:
			app.logger.error('Inception-server DBconnect Error: %s', err)
			return jsonify('')
		else:
			iconn.close()


def sqlaudit_query(sql, sqltype):
	inception_web = {
		"host": config.get("inception-web","host"),
		"user": config.get("inception-web","user"),
		"passwd": config.get("inception-web","password"),
		"db": config.get("inception-web","db"),
		"port": config.getint("inception-web","port"),
		"charset": config.get("inception-web","charset")
	}

	try:
		conn = MySQLdb.connect(**inception_web)
		cursor = conn.cursor()
		query = cursor.execute(sql)
		if sqltype == 'select':
			row = cursor.fetchone()
			if row:
				return row[0]
		conn.commit()
		cursor.close()
	except MySQLdb.Error, err:
		app.logger.error('Inception-web DBconnect Error: %s', err)
	else:
		conn.close()

@app.route('/sqlguide', methods=['get'])
def sqlguide():
	return render_template('sqlguide.html')

@app.route('/inception-auth', methods=['get'])
def coder():
	return render_template('coder.html')

@app.route('/icode', methods=['get'])
def code():
	code = int(time.time())
	sql = 'insert into dyncode(code) values(%d);' % code
	sqlaudit_query(sql, 'insert')
	return jsonify(code)

if __name__ == '__main__':
	formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
	handler = RotatingFileHandler('./inception.log', maxBytes=262144, backupCount=2)
	handler.setFormatter(formatter)
	handler.setLevel(logging.INFO)
	app.logger.addHandler(handler)

	app.run('0.0.0.0',debug=True)
