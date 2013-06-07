#!/bin/env python
#
# timeit_exec_time.py
# http://bytebaker.com/2008/07/30/python-namespaces/

import timeit

def line_endswith(line):
    if line.endswith("\n"):
        pass

def line_slice(line):
    if line[-1] == "\n":
        pass

def get_exec_time(line, times, counts):
    endswith_exec_time_list = timeit.repeat('line_endswith(line)',
                                       'from __main__ import line_endswith,line',
                                       repeat=times, number=counts)
    endswith_exec_time_list.sort()
    slice_exec_time_list = timeit.repeat('line_slice(line)',
                                    'from __main__ import line_slice,line',
                                    repeat=times, number=counts)
    slice_exec_time_list.sort()
    print "endswith: %s(s)" % endswith_exec_time_list[-1]
    print "slice   : %s(s)" % slice_exec_time_list[-1]

if __name__ == "__main__":
    line = "aha aha ehene 3jnd 4 hhhlll ninin namae 4mdmjcola jjhhsjs 33 d oldnhd\n"
    get_exec_time(line, 10, 1000)
