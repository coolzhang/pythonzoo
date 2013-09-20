#!/bin/env python
#
# vimycnf.py - show and modify option from the configuration file of mysqld
# code by vj.zhanghai@gmail.com
#

from optparse import OptionParser
import ConfigParser

USAGE = """%prog - Show and modify option from the configuration file of mysqld
e.g.:
%prog --mycnf /path/to/my.cnf --section mysqld --show variable
%prog --mycnf /path/to/my.cnf --section mysqld --set variable=value
"""
VERSION = "%prog Alpha"

optparser = OptionParser(usage=USAGE, version=VERSION)
optparser.add_option("-f", "--mycnf", action='store', dest="mycnf",
                     help="Given the configuration file.",
                     metavar="FILE")
optparser.add_option("-g", "--section", action='store', dest="section",
                     help="Given section from the configuration.",
                     metavar="SECTION")
optparser.add_option("-s", "--show", action='store', dest="getopt",
                     help="Get an option value for the named section.")
optparser.add_option("-m", "--set", action='store', dest="setopt",
                     help="Set the given option to the specified value.")

(options, args) = optparser.parse_args()

config = ConfigParser.SafeConfigParser()
config.read(options.mycnf)

def show_variable():
    try:
        if options.getopt == 'all':
            print "The whole variables are as follow:"
            print "----------------------------------"
            for name, value in config.items(options.section):
                print "%-35s = %s" %(name, value)
        else:
            print "type(optins.getopt) options.getopt"
            print "current variable: [ %s = %s ]" \
                  %(options.getopt, config.get(options.section, options.getopt))

    except ConfigParser.NoSectionError, err:
        print str(err)
    except ConfigParser.NoOptionError, err:
        print str(err)

def set_variable():
    try:
        if args:
            options.setopt = options.setopt + ''.join(args)

        (option, value) = tuple(options.setopt.replace(' ','').split('='))
        print "before modifying: [ %s = %s ]" \
              %(option, config.get(options.section, option))
        config.set(options.section, option, value)
        with open(options.mycnf, 'w') as mycnf:
            config.write(mycnf)
        print "after modifying:  [ %s = %s ]" \
              %(option, config.get(options.section, option))
    except ConfigParser.NoSectionError, err:
        print str(err)
    except ConfigParser.NoOptionError, err:
        print str(err)

if __name__ == "__main__":
    if options.getopt and options.setopt:
        print optparser.error("option -s and -m are mutually exclusive.")

    if options.getopt:
        show_variable()

    if options.setopt:
        set_variable()
