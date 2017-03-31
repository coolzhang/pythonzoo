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
from redmine import Redmine

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
	config.set('inception-web','token-timeout','3600')
	config.set('inception-web','with-redmine','False')
	config.add_section('inception-client')
	config.set('inception-client','user','inception')
	config.set('inception-client','password','')
	config.add_section('redmine')
	config.set('redmine','username','')
	config.set('redmine','password','')
	config.set('redmine','assigned_to','')
	with open('./inception-web.conf', 'wb') as configfile:
		config.write(configfile)
config.read('./inception-web.conf')

app = Flask(__name__)

@app.route('/', methods=['get'])
def login_pre():
	return render_template('login-pre.html')

@app.route('/tokengenbyissue', methods=['post'])
def tokengenbyissue():
	issue = request.values.get('redmineissue','')
	if issue:
		if issue.isdigit():
			try:
				redmine = Redmine('http://redmine.intra.wepiao.com', username=config.get("redmine","username"), password=config.get("redmine","password"))
				redmine_issue = redmine.issue.get(int(issue))
				assigned_to = config.get("redmine","assigned_to")
				if assigned_to.lower() == redmine_issue.assigned_to.name.lower():
					issue_exist = 'select issue,token,(expire + unix_timestamp(ctime)) as deadline from login where issue=%d' %(int(issue))
					issue, token, deadline = incwebDB_exec(issue_exist, 'select')
					if issue:
						now = int(time.time())
						if now < deadline:
							res, msg = token_check(token)
							if not res:
								token_new = token_maker()
								token_update = 'update login set token=%d where token=%d;' %(token_new, token)
								incwebDB_exec(token_update, 'insert')
							token_new = token
							return jsonify({"success": True, "token": token_new})
						else:
							return jsonify({"success": False, "errmsg": u'此工单号已过期，请重新创建工单!'})
					else:
						token = token_maker()
						issue_save = 'insert into login(issue, token) values(%d, %d);' %(int(issue), token)
						incwebDB_exec(issue_save, 'insert')
						return jsonify({"success": True, "token": token})
				else:
					return jsonify({"success": False, "errmsg": u'此工单号无效!'})
			except Exception, err:
				print(err)
				return jsonify({"success": False, "errmsg": u'此工单号不存在!'})
		else:
			return jsonify({"success": False, "errmsg": u'此工单号不合法!'})
	else:
		return jsonify({"success": False, "errmsg": u'请先输入工单号!'})

@app.route('/login', methods=['post','get'])
def login():
	if request.method == 'GET':
		return render_template('login.html')

	token = request.values.get('dyncode','')
	res, msg = token_check(token)
	if res:
		return redirect(url_for('audit', token=token))
	else:
		return render_template('login-pre.html', errmsg=msg)

@app.route('/audit/<token>', methods=['get'])
def audit(token):
	res, msg = token_check(token)
	if res:
		return render_template('sqlaudit.html')
	else:
		return render_template('login-pre.html', errmsg=msg)

@app.route('/sqlaudit',methods=['post','get'])
def audit_exec():
	token = int(request.headers['Referer'].split('/')[-1])
	now = int(time.time())
	token_timeout = now - token
	if token_timeout < config.getint("inception-web","token-timeout"):
		online = {
			"user": config.get("inception-client","user"),
			"password": config.get("inception-client","password"),
			"instance": request.values.get("dbinstance",""),
			"database": request.values.get("dbname",""),
			"sql": request.values.get("auditcontent",""),
			"operator": request.values.get("operator",""),
			"redmineissue": request.values.get("redmineissue",""),
			"connect_timeout": 3
		}

		if config.getboolean("inception-web", "with-redmine"):
			try:
				redmine = Redmine('http://redmine.intra.wepiao.com', username=config.get("redmine","username"), password=config.get("redmine","password"))
				redmine_issue = redmine.issue.get(int(online['redmineissue']))
				if online['operator'] != ''.join(redmine_issue.author.name.split())[1:]:
					return jsonify('redmine_author')
			except Exception, err:
				print(err)
				return jsonify('redmine_issue')

		try:
			conn = MySQLdb.connect(user=online['user'], passwd=online['password'], host=online['instance'].split(':')[0], port=int(online['instance'].split(':')[1]), db=online['database'], connect_timeout=online['connect_timeout'], charset='utf8')
		except MySQLdb.Error, err:
			app.logger.error('MySQL Server DBconnect Error %d: %s', err[0],err[1])
			if err[0] == 1045:
				return jsonify('incuser')
			else:
				return jsonify('mysql') 

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
					sql = 'insert into operator_log(operator,issue,errlevel,errmsg) values("%s",%s,%d,"%s");' %(online['operator'], online['redmineissue'], r_errlevel, r_err)
					sqlaudit_query(sql, 'insert')
			icur.close()

			if sum(errlevels) == 0:
				sql = 'insert into inception_log(dbinstance,dbname,ioutput) values("%s","%s","%s");' %(online["instance"], online["database"], audit_result)
				sqlaudit_query(sql, 'insert')
			return jsonify(audit_result)
		except MySQLdb.Error, err:
			app.logger.error('Inception-server DBconnect Error: %s', err)
			return jsonify('incserver')
		else:
			iconn.close()

@app.route('/tokenKznxVczC', methods=['get'])
def token():
	return render_template('token.html')

@app.route('/tokengen', methods=['post'])
def tokengen():
	token = token_maker()
	return jsonify(token)

@app.route('/sqlguide', methods=['get'])
def sqlguide():
	return render_template('sqlguide.html')

def incwebDB_exec(sql, sqltype):
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
				return row
		conn.commit()
		cursor.close()
	except MySQLdb.Error, err:
		app.logger.error('Inception-web DBconnect Error: %s', err)
	else:
		conn.close()

def token_maker():
	token = int(time.time())
	sql = 'insert into token(token) values(%d);' % token
	incwebDB_exec(sql, 'insert')
	return token

def token_check(token):
	if token:
		if str(token).isdigit():
			sql = 'select token from token where token=%d' % int(token)
			token_exist = incwebDB_exec(sql, 'select')
			now = int(time.time())
			token_timeout = now - int(token)
			if token_exist:
				if token_timeout < config.getint('inception-web','token-timeout'):
					result = True
					message = u'此动态验证码有效!'
				else:
					result = False
					message = u'此动态验证码已过期，请联系DBA!'
			else:
				result = False
				message = u'此动态验证码无效，不要尝试破解哦!'
		else:
			result = False
			message = u'此动态验证码不合法!'
	else:
		result = False
		message = u'请先输入动态验证码!'
	return (result, message)

if __name__ == '__main__':
	formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
	handler = RotatingFileHandler('./inception.log', maxBytes=262144, backupCount=2)
	handler.setFormatter(formatter)
	handler.setLevel(logging.ERROR)
	app.logger.addHandler(handler)

	app.run('0.0.0.0', debug=True)
