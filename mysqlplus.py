#!/bin/env python
# mysqlplus.py - Play on Oracle Database like MySQL
# The idea and implemention by vj.zhanghai@gmail.com
#
# Reference:
#     Completer class:
#         http://effbot.org/librarybook/readline.htm
#     Subprocess usage:
#         http://moizmuhammad.wordpress.com/2012/01/31/run-oracle-commands-from-python-via-sql-plus/
# Thinks to:
#     Hiro(my best friend) and one pymaster @kingsoft


from optparse import OptionParser
import getpass
import readline
from subprocess import Popen, PIPE
import sys

cmd_mapping_m2o_notes = {
    'mysql -uroot': 'sqlplus / as sysdba',
    'status': 'define',
    'select current_user();': 'select username from user_users;',
    'show databases;': 'select username from all_users;',
    'use <db_name>': 'connect <user/pw>',
    'show tables;': 'select table_name from user_tables; or select * from tab/cat;',
    'show processlist;': 'select id,user,host,db,command,time,status,info from v$session;',
    'create database <db_name>;': 'create user user_name identified by "password";',
    'system <os_cmd>': 'host <os_cmd> or 1.host 2.os_cmd 3.exit',
    'source </path/to/run.sql>': '@</path/to/run>',
    'tee </path/to/outfile>': 'spool </path/to/outfile>',
    'notee': 'spool off',
    'pager less': 'set pagesize <number> -- default to 50 lines',
    }

cmd_mapping_m2o = {
    'show processlist;': 'select SID "Id", PROCESS "Pid", USERNAME "Username", MACHINE "Host", TYPE "Command", LAST_CALL_ET "Time", STATUS "State", COMMAND "Info" from v$session;',
    'show databases;': 'select username from all_users;',
    'show tables;': 'select table_name from user_tables;',
    'select current_user();': 'select username from user_users;',
    'create database': 'create user',
    'status': 'define',
    'use': 'connect',
    'system': 'host',
    'source': '@',
    'tee': 'spool',
    'notee': 'spool off',
    'pager less': 'set pagesize 50',
    'help': 'help'
    }

class Completer:

    def __init__(self, words):
        self.words = words
        self.prefix = None

    def complete(self, prefix, index):
        if prefix != self.prefix:
            self.matching_words = [
                w for w in self.words if w.startswith(prefix)
                ]
            self.prefix = prefix
            try:
                return self.matching_words[index]
            except IndexError:
                return None

def mysqlplus_options():
<<<<<<< HEAD
    USAGE = "%prog -u username -p [password] [-H Host:Port/service_name #easy_connect]"
=======
    USAGE = "%prog -u username -p [password]"
>>>>>>> origin/master
    DESCRIPTION = "Use SQL*PLUS like mysql style"
    VERSION = "%prog Alpha"

    parser = OptionParser(usage=USAGE, description=DESCRIPTION, version=VERSION)
    parser.add_option("-u", "--user", action='store', dest="user",
                      help="User for login if not current user.", metavar="name")
    parser.add_option("-p", "--password", action='store_true', dest="password",
                      help="Password to use when connecting to server.",
                      metavar="name")
    parser.add_option("-H", "--host", action='store', dest="host",
                      help="Connect to host", metavar="name")

    (options, args) = parser.parse_args()
    if options.user is None or options.password is None:
        parser.error("both username and password must be given")
    else:
        if len(args) != 0:
            parser.error("incorrect number of arguments")
        else:
            options.password = getpass.getpass()
            if options.password == '':
                parser.error("password can not be empty")
            else:
                user = options.user
                password = options.password
                host = options.host

    MYOPTIONS = {
        'user': user,
        'password': password,
        'host': host if host else '',
<<<<<<< HEAD
=======
#        'sname': sname if sname else ''
>>>>>>> origin/master
        }

    return MYOPTIONS

<<<<<<< HEAD
def cmd_mapping(mysql_cmd, user):
    mysql_cmd = mysql_cmd.split()
    username = user
=======
def cmd_mapping(mysql_cmd):
    mysql_cmd = mysql_cmd.split()
>>>>>>> origin/master

    if len(mysql_cmd) == 1:
        cmd_key = ' '.join(mysql_cmd).strip(';')
        try:
            sqlplus_cmd = cmd_mapping_m2o[cmd_key]
        except KeyError:
            sqlplus_cmd = cmd_key

    if len(mysql_cmd) == 2:
        if mysql_cmd[0] == "use":
            if mysql_cmd[1] == username:
                print "Current schema is already [ %s ]" % username
<<<<<<< HEAD
                sqlplus_cmd = cmd_mapping_m2o[mysql_cmd[0]] + " " + username +"/******"
            else:
                new_username = mysql_cmd[1]
                sys.exit("Please re-run mysqlplus to login via %s" % new_username)
=======
                sqlplus_cmd = cmd_mapping_m2o[mysql_cmd[0]] + " " + username + "/" + password
            else:
                print "Please re-run mysqlplus to login via %s" % username
>>>>>>> origin/master
        elif mysql_cmd[0] == "show" or mysql_cmd[0] == "select":
            cmd_key = ' '.join(mysql_cmd).strip(';') + ";"
            try:
                sqlplus_cmd = cmd_mapping_m2o[cmd_key]
            except KeyError:
                sqlplus_cmd = cmd_key
        else:
            cmd_key = ' '.join(mysql_cmd).strip(';')
            try:
                sqlplus_cmd = cmd_mapping_m2o[cmd_key]
            except KeyError:
                sqlplus_cmd = cmd_key

    if len(mysql_cmd) > 2:
        if mysql_cmd[0]+" "+mysql_cmd[1] == "create database":
            cmd_key = mysql_cmd[0] + " " + mysql_cmd[1]
            sqlplus_cmd = cmd_mapping_m2o[cmd_key] + " " + mysql_cmd[2].strip(';') + " identified by 'mysqlplus';"
            print "!!!Security Note: Please change the default password for user [%s]" % mysql_cmd[2].strip(';')
        elif mysql_cmd[0] == "system":
            sqlplus_cmd = cmd_mapping_m2o[mysql_cmd[0]] + " " + ' '.join(mysql_cmd[1:]).strip(';')
        else:
            sqlplus_cmd = ' '.join(mysql_cmd).strip(';') + ";"

    return sqlplus_cmd

def run_mysqlplus_cmd(sql_cmd, account):
    session = Popen(['sqlplus', '-S', account], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    session.stdin.write(sql_cmd)
    return session.communicate()

def input_loop(logon):
    mysql_cmd = ''
    while mysql_cmd != 'quit':
        try:
            mysql_cmd = raw_input('mysqlplus> ')
            if mysql_cmd == '':
                mysql_cmd = raw_input('mysqlplus> ')
            elif mysql_cmd == "help":
                show_cmd_mapping_help()
                print
            else:
<<<<<<< HEAD
                if mysql_cmd.split()[0] == 'use':
                    user = logon.split('/')[0]
                    oracle_cmd = cmd_mapping(mysql_cmd, user)
                    print "-------"
                    print "Mapping to SQL*Plus Command: %s" % oracle_cmd
                    print "-------"
                    print "Connected."
                else:
                    user = logon.split('/')[0]
                    oracle_cmd = cmd_mapping(mysql_cmd, user)
                    print "-------"
                    print "Mapping to SQL*Plus Command: %s" % oracle_cmd
                    print "-------"
                    account = logon
                    res, errmsg = run_mysqlplus_cmd(oracle_cmd, account)
                    print res
=======
                oracle_cmd = cmd_mapping(mysql_cmd)
                print "-------"
                print "Mapping to SQL*Plus Command: %s" % oracle_cmd
                print "-------"
                account = logon
                res, errmsg = run_mysqlplus_cmd(oracle_cmd, account)
                print res
>>>>>>> origin/master
        except KeyError:
            break

def sqlplus_logon():
    cnx = mysqlplus_options()

    if cnx['host']:
        if cnx['user'] == 'sys':
            logon = cnx['user'] + '/' + cnx['password'] + ' as sysdba' + '@' + '"' + cnx['host'] + '"'
        else:
            logon = cnx['user'] + '/' + cnx['password'] + '@' + '"' + cnx['host'] + '"'
    else:
        if cnx['user'] == 'sys':
            logon = cnx['user'] + '/' + cnx['password'] + ' as sysdba'
        else:
            logon = cnx['user'] + '/' + cnx['password']

    return logon

<<<<<<< HEAD
def check_logon():
=======
def logon_check():
>>>>>>> origin/master
    cmd = 'select 1+1 from dual;'
    account = sqlplus_logon()
    res, errmsg = run_mysqlplus_cmd(cmd, account)
    if res.split()[2]  == "2":
        return account
    else:
        sys.exit("ERROR: ORA-01017: invalid username/password; logon denied")

def show_cmd_mapping_help():
    notes = "Commands mapping on MySQL to Oracle"
    print notes
    print "-" * len(notes)

    for k in cmd_mapping_m2o_notes.keys():
        print "mysql> %-30s SQL> %-50s" % (k, cmd_mapping_m2o_notes[k])

def db_concepts():
    print """
    Concepts on Oracle v.s. MySQL:

                  Oracle                       MySQL
          database <--> instance              instance
              |                                   |
              |                                   |
              |                                   |
              V                                   V
        user <--> schema                database <--> schema

    """


if __name__ == "__main__":
    words = cmd_mapping_m2o.keys()
    completer = Completer(words)

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer.complete)

    if getpass.getuser() == "oracle":
<<<<<<< HEAD
        logon = check_logon()
=======
        logon = logon_check()
>>>>>>> origin/master
        db_concepts()
        input_loop(logon)
    else:
        print "Please run mysqlplus as oracle"
