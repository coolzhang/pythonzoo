#!/bin/env python
#
# check_big_log_updated_frequently.py
# Thanks to @limodou & mao(Kingsoft)
#
# Test Case:
# shell> printf "1. ERROR LINE\n" >> mysql-error.log  # whole line check
# shell> printf "2. ERROR not EOF," >> mysql-error.log
# shell> printf " now EOF\n" >> mysql-error.log       # half line check


import time

SEEK_FILE = '/tmp/seek.txt'
ERROR_LOG = '/data/mysql/mysql-error.log'

try:                                                    # check seek file
    f_seek = open(SEEK_FILE, 'r')
    last_offset = long(f_seek.read())
except IOError:
    f_seek = open(SEEK_FILE, 'w')
    f_seek.write('0')
    last_offset = 0
finally:
    f_seek.close()

with open(ERROR_LOG, 'r') as f_log:
    f_log.seek(last_offset)
    line_buf = ""                                       # init buf
    while True:
        line = f_log.readline()
        if not line:                                    # EOF
            with open(SEEK_FILE, 'r') as f_seek_r:
                old_offset = long(f_seek_r.read())
                #print "old_offset: %s" % old_offset    # debug_log
            new_offset = long(f_log.tell())
            #print "new_offset: %s" % new_offset        # debug_log
            if new_offset == old_offset:
                #print 'waiting 5sec ...'               # debug_log
                time.sleep(5)
            else:
                with open(SEEK_FILE,'w') as f_seek_w:
                    f_seek_w.write(str(new_offset))
        else:
            if not line.endswith("\n"):                 # half line
                line_buf = line_buf + line
                #print 'half line ...'                  # debug_log
            else:                                       # whole line
                if len(line_buf) > 0:
                    line = line_buf + line
                if "ERROR" in line:
                    print line,
                line_buf = ""                           # reset buf
