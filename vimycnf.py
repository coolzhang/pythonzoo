#!/bin/env python
#
# vimycnf.py - show and modify option from the configuration file of mysqld
# code by vj.zhanghai@gmail.com
#

from optparse import OptionParser
import ConfigParser

USAGE = """%prog - Show and modify option from the configuration file of mysqld
e.g.:
#show variable:>   %prog -f /path/to/my.cnf -g mysqld -s variable
#set  variable:>   %prog -f /path/to/my.cnf -g mysqld -m variable=value
#add  variable:>   %prog -f /path/to/my.cnf -g mysqld -a variable=value
#list sections:>   %prog -f /path/to/my.cnf -l
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
optparser.add_option("-l", "--list", action='store_true', dest="group",
                     help="List all sections in the configuration.")
optparser.add_option("-a", "--append", action='store', dest="addopt",
                     help="Append new option into the existing section.")

(options, args) = optparser.parse_args()

config = ConfigParser.SafeConfigParser()
config.read(options.mycnf)

def show_variable():
    try:
        if options.getopt == 'all':
            print "[%s]" %options.section
            for name, value in config.items(options.section):
                print "%-35s = %s" %(name, value)
        else:
            print "Current variable:  %s = %s" \
                  %(options.getopt, config.get(options.section, options.getopt))

    except ConfigParser.NoSectionError, err:
        print str(err)
    except ConfigParser.NoOptionError, err:
        print str(err)

def set_variable():
    try:
        options.setopt = options.setopt + ''.join(args)
        if "=" not in options.setopt:
            print "Argument not available: should be variable=value"
        else:
            (option, value) = tuple(options.setopt.replace(' ','').split('='))
            if value:
                print "Before modifying: %s = %s" \
                      %(option, config.get(options.section, option))
                config.set(options.section, option, value)
                with open(options.mycnf, 'w') as mycnf:
                     config.write(mycnf)
                print "After modifying:  %s = %s" \
                      %(option, config.get(options.section, option))
            else:
                print "Argument not available: should be variable=value"
    except ConfigParser.NoSectionError, err:
        print str(err)
    except ConfigParser.NoOptionError, err:
        print str(err)

def add_variable():
    options.addopt = options.addopt + ''.join(args)
    if "=" not in options.addopt:
        print "Argument not available: should be variable=value"
    else:
        (option, value) = tuple(options.addopt.replace(' ','').split('='))
        if value:
            if config.has_option(options.section, option):
                print "Variable: '%s' already exists, should use --set|-m option" \
                      %option
            if config.has_section(options.section) and not config.has_option(options.section, option):
                config.set(options.section, option, value)
                with open(options.mycnf, 'w') as mycnf:
                    config.write(mycnf)
                print "Append new variable: %s = %s" \
                      %(option, config.get(options.section, option))
            else:
                print "No section: '%s'" %options.section
        else:
            print "Argument not available: should be variable=value"

def list_section():
    print "%d sections in %s :" %(len(config.sections()), options.mycnf)
    for section in config.sections():
        print "[%s]" %section


if __name__ == "__main__":
    if options.getopt and options.setopt:
        print optparser.error("Option -s and -m are mutually exclusive.")

    if options.getopt:
        show_variable()

    if options.setopt:
        set_variable()

    if options.group:
        list_section()

    if options.addopt:
        add_variable()
