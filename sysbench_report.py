#!/bin/env python
#  Author to: {lafeng: vj.zhanghai@gmail.com}
#  Thanks to:  master han
#  Welcome from your feedback:P

from optparse import OptionParser
import sys
import re
import glob

USAGE = """%prog -m testmode -f logfile[s]

e.g.:  %prog -m oltp -f oltp_128.log oltp_64.log
       %prog -m oltp -f oltp_*
        """
DESCRIPTION = "Print report from sysbench logs"
VERSION = "%prog Alpha"

parser = OptionParser(usage=USAGE, description=DESCRIPTION, version=VERSION)
parser.add_option("-m", "--mode", action="store", dest="mode",
                  help="name of the test mode to run", metavar="MODE")
parser.add_option("-f", "--logfile", action="store_true", dest="logfile",
                  help="logfile to be created by sysbench run", metavar="FILE")

(options, args) = parser.parse_args()

def show_report(mode):
    graph_items = {}
    pattern = {'cpu': '^Primer.*|.*threads.*|.*total time:.*',\
               'fileio': '.*file size.*|^Block.*|^Doing.*|.*Mb/sec.*|.*Requests/sec.*',\
               'oltp': '.*threads:.*|.*transactions:.*'}
    print "Sysbench - %s" % mode
    print "-" * len("Sysbench - mode")
    if "*" in sys.argv[4:][0]:
        logs = glob.glob(sys.argv[4:][0])
    else:
        logs = sys.argv[4:]

    for log in logs:
        run_info = [ line.strip("\n") for line in open(log) \
                     if re.match(pattern[mode], line) ]
        if mode == "cpu":
            graph_items["T" + run_info[0].split(":")[1].strip()] = run_info[2].split(":")[1].strip(" s")
                        print "Thread Number: %-9s" % run_info[0].split(":")[1].strip()
            print "Primer Number: %-9s" % run_info[1].split(":")[1].strip()
            print "Total Time:    %-9s" % run_info[2].split(":")[1].strip()
            print "-"
        elif mode == "fileio":
            rw_mode = {"sequential_read": "seqrd", "sequential_write": "seqwr",
                       "sequential_rewrite": "seqrewr", "random_read": "rndrd",
                       "random_write": "rndwr", "random_r/w": "rndrw"}
            graph_items["bs" + run_info[1].split()[2] + "_" + \
                        rw_mode[run_info[2].split()[1] + "_" + run_info[2].split()[2]]] \
                       = run_info[4].split()[0]
            print "Total size: %-10s" % run_info[0].split()[0]
            print "Block Size: %-10s" % run_info[1].split()[2]
            print "Test Mode:  %-10s" % (rw_mode[run_info[2].split()[1] + "_" + run_info[2].split()[2]])
            print "TpPS:       %-10s" % run_info[3].split()[7].strip("()")
            print "IOPS:       %-10s" % run_info[4].split()[0]
            print "-"
        elif mode == "oltp":
            graph_items["T" + run_info[0].split()[3]] = run_info[1].split()[2].strip("(")
            print "Thread Number: %-9s" % run_info[0].split()[3]
            print "TPS: %-9s" % run_info[1].split()[2].strip("(")
            print "-"

    return graph_items

def show_graph(item):
    tag = "+"
    for (k,v) in item.iteritems():
        if float(v) < 200:
            tag_count = 2
        elif 200 < float(v) < 500:
            tag_count = 3
        elif  500 < float(v) < 1000:
            tag_count = int(float(v)/100)
        elif 1000 < float(v) < 5000:
            tag_count = int(float(v)/100)
        elif 5000 < float(v) < 10000:
            tag_count = int(float(v)/1000)
        else:
            tag_count = 50
        print "%-15s:  %s" % (k,tag * tag_count)

graph_items = show_report(options.mode)
show_graph(graph_items)
print
