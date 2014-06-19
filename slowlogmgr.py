#!/bin/env python
#  Program: slowlogmgr - MySQL Slow Query Log Manger
#  Author to: {lafeng: vj.zhanghai@gmail.com}
#  Welcome from your feedback:P

from optparse import OptionParser
import mysql.connector
import time

USAGE = """%prog - Analyze slow query log and inform DBA/DEV of TOP n slow queries
e.g.:
# slowlogmgr --server=root:12345@localhost:3308 --long-query-time=3 --runtime=3600 --top=5 
# slowlogmgr --server=root:12345@localhost:3308 --long-query-time=3 --daemon
# slowlogmgr --server=root:12345@localhost:3308 --runtime=60 --report-account
# slowlogmgr --server=root:12345@localhost:3308 --report-account
"""
VERSION = "%prog Alpha"

optparser = OptionParser(usage=USAGE, version=VERSION)
optparser.add_option("-l", "--long-query-time", action="store", dest="querytime", default=2,
                     help="Longer than the threshold to be logged,default:2", metavar="SECOND")
optparser.add_option("-r", "--runtime", action="store", dest="runtime",
                     help="Collection time of slow log,default:10", metavar="SECOND")
optparser.add_option("-t", "--top", action="store", dest="topN", default=5,
                     help="Just show the top n queries,default:5", metavar="NUMBER")
optparser.add_option("-d", "--daemon", action="store_true", dest="daemon", default=False,
                     help="Run slowlogmgr as a daemon in the background,overrides option --runtime (-r)")
optparser.add_option("-s", "--server", action="store", dest="server",
                     help="Connection information", metavar="<user>[:<passwd>]@<host>[:<port>]")
optparser.add_option("--report-account", action="store_true", dest="account", default=False,
                     help="summarize account info")

(options,args) = optparser.parse_args()

def cnx_config():
    try:
        if "@" in options.server:
            if len(options.server.split(':')) == 3:
                USER = options.server.split('@')[0].split(':')[0]
                PASS = options.server.split('@')[0].split(':')[1]
                HOST = options.server.split('@')[1].split(':')[0]
                PORT = options.server.split('@')[1].split(':')[1]
            elif len(options.server.split(':')) == 2:
                            if ":" in options.server.split('@')[0]:
                    USER = options.server.split('@')[0].split(':')[0]
                    PASS = options.server.split('@')[0].split(':')[1]
                    HOST = options.server.split('@')[1].split(':')[0]
                    PORT = '3306'
                else:
                    USER = options.server.split('@')[0]
                    PASS = ''
                    HOST = options.server.split('@')[1].split(':')[0]
                    PORT = options.server.split('@')[1].split(':')[1]
            elif len(options.server.split(':')) == 1:
                USER = options.server.split('@')[0]
                PASS = ''
                HOST = ''
                PORT = ''
            else:
                USER = options.server.split('@')[0]
                PASS = ''
                HOST = options.server.split('@')[1]
                PORT = '3306'
        else:
            print optparser.error("Argument of option --server is not correct. <user>[:<passwd>]@<host>[:<port>]")

        config = {
          'user': USER,
          'password': PASS,
          'host': HOST if HOST else '127.0.0.1',
          'port': PORT if PORT else '3306',
          'database': 'mysql'
        }

        return config
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."

def rotate_slowlog():
    try:
        config = cnx_config()
        cnx = mysql.connector.connect(**config)
        cur_rotate_slowlog = cnx.cursor()
        query1 = ("set global slow_query_log = 0")
                query2 = ("drop table if exists slow_log_bak")
        query3 = ("create table slow_log_temp like slow_log")
        query4 = ("rename table slow_log to slow_log_bak, slow_log_temp to slow_log")
        cur_rotate_slowlog.execute(query1)
        cur_rotate_slowlog.execute(query2)
        cur_rotate_slowlog.execute(query3)
        cur_rotate_slowlog.execute(query4)
        cnx.close()
    except mysql.connector.errors.Error as err:
        print "Database connection or operation went wrong: %s" %(err)
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."

def enable_slowlog():
    try:
        config = cnx_config()
        cnx = mysql.connector.connect(**config)
        cur_enable_slowlog = cnx.cursor()
        query1 = ("set global log_output = 'table'")
        query2 = ("set global slow_query_log = 1")
        query3 = ("set global long_query_time = %s")
        cur_enable_slowlog.execute(query1)
        cur_enable_slowlog.execute(query2)
        querytime = float(options.querytime) if '.' in 'options.querytime' else int(options.querytime)
        cur_enable_slowlog.execute(query3, (querytime,))
        cnx.close()
    except mysql.connector.errors.Error as err:
        print "Database connection or operation went wrong: %s" %(err)
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."

def disable_slowlog():
    try:
        config = cnx_config()
        cnx = mysql.connector.connect(**config)
        cur_enable_slowlog = cnx.cursor()
        query1 = ("set global slow_query_log = 0")
        query2 = ("set global long_query_time = 10")
        cur_enable_slowlog.execute(query1)
        cur_enable_slowlog.execute(query2)
        cnx.close()
            except mysql.connector.errors.Error as err:
        print "Database connection or operation went wrong: %s" %(err)
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."

def print_topN():
    try:
        config = cnx_config()
        cnx = mysql.connector.connect(**config)
        cur_print_topN = cnx.cursor()
        query_topN = (
          "select start_time, sql_text, query_time from mysql.slow_log "
          "order by query_time desc limit %s"
        )
        topN = int(options.topN)
        cur_print_topN.execute(query_topN, (topN,))

        print """
        +-----------------------------------------+
        |         Top """,options.topN,""" Slow Queries            |
        |   start_time | sql_text | query_time    |
        +-----------------------------------------+
        """
        for (stime, query, qtime) in cur_print_topN:
            print stime, " | ", query, " | ", qtime
        cnx.close()
    except mysql.connector.errors.Error as err:
        print "Database connection or operation went wrong: %s" %(err)
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."

def show_slow_queries():
    try:
        config = cnx_config()
        cnx = mysql.connector.connect(**config)
        cur_slow_queries = cnx.cursor()
        query_slow_queries = ("show global status like 'slow_queries'")
        cur_slow_queries.execute(query_slow_queries)
        for (variable, value) in cur_slow_queries:
            slow_queries = value
        cnx.close()
        
        return slow_queries
    except mysql.connector.errors.Error as err:
        print "Database connection or operation went wrong: %s" %(err)
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."


def print_slowquery(start_time):
    try:
        config = cnx_config()
        cnx = mysql.connector.connect(**config)
        cur_print_slowquery = cnx.cursor()
        query_slowquery = (
          "select start_time, sql_text, query_time from mysql.slow_log "
          "where start_time > %s"
        )
        cur_print_slowquery.execute(query_slowquery, (start_time,))
        print "---- %s ----" %(start_time)
        for (stime, query, qtime) in cur_print_slowquery:
            print stime, " | ", query, " | ", qtime
        print "---- end ----"
        print
        cnx.close()

        return stime
    except mysql.connector.errors.Error as err:
        print "Database connection or operation went wrong: %s" %(err)
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."

def slowlog_daemonize():
    try:
        enable_slowlog()
        old_stat = show_slow_queries()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        while True:
            new_stat = show_slow_queries()
            if new_stat:
                #print "new: %s %s" %(new_stat, start_time)
                if new_stat == old_stat:
                                    time.sleep(10)
                elif new_stat > old_stat:
                    last_time = print_slowquery(start_time)
                    start_time = last_time
                    old_stat = new_stat
                    #print "old: %s %s" %(old_stat, start_time)
            else:
                break
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."

def report_account():
    try:
        config = cnx_config()
        cnx = mysql.connector.connect(**config)
        cur_userhost = cnx.cursor()
        query_userhost = (
          "select user_host, count(*) from mysql.slow_log "
          "group by user_host order by count(*) desc"
        )
        cur_userhost.execute(query_userhost)
        print """
        +-------------------------------------+
        |     Remote Account Access Report    |
        |           (Account|Count)           |
        +-------------------------------------+"""

        for (user_host, count) in cur_userhost:
            if 'localhost' not in user_host and '127.0.0.1' not in user_host:
                print "%-10s        |%-10s" %(user_host.split('[')[0]+'@'+user_host.split('[')[2].strip(']'), count)
    except mysql.connector.errors.Error as err:
        print "Database connection or operation went wrong: %s" %(err)
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."


if __name__ == "__main__":
    try:
        if options.server:
            if options.runtime and not options.daemon and not options.account:
                rotate_slowlog()
                                enable_slowlog()
                time.sleep(float(options.runtime))
                print_topN()
                disable_slowlog()
            elif not options.runtime and options.daemon and not options.account:
                try:
                    slowlog_daemonize()
                except (KeyboardInterrupt, SystemExit):
                    disable_slowlog()
                    print
                    print "slowlogmgr.py is stopped."
            elif options.runtime and options.daemon and not options.account:
                print ("Warning: option --daemon overrides option --runtime")
                try:
                    slowlog_daemonize()
                except (KeyboardInterrupt, SystemExit):
                    disable_slowlog()
                    print
                    print "slowlogmgr.py is stopped."
            elif (not options.runtime and not options.account) or (not options.daemon and not options.account):
                print optparser.error("Either option --runtime (-r) or --daemon (-d) must be used")
            elif options.account and options.runtime:
                rotate_slowlog()
                options.querytime = 0
                enable_slowlog()
                time.sleep(float(options.runtime))
                report_account()
                disable_slowlog()
            elif options.account and not options.runtime:
                options.querytime = 0
                enable_slowlog()
                report_account()
                disable_slowlog()
        else:
            print optparser.error("option --server (-s) is mandatory")
    except (KeyboardInterrupt, SystemExit):
        print
        print "slowlogmgr.py is stopped."
