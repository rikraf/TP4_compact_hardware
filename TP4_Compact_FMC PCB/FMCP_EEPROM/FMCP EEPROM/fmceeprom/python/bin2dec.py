#!   /usr/bin/env   python
#    coding: utf8

# Copyright CERN, 2011
# Author: Matthieu Cattin <matthieu.cattin@cern.ch>
# Licence: GPL v2 or later.
# Website: http://www.ohwr.org

import sys
import time
import os


def dump_file_to_eeprom(filename):
    eeprom_content = []
    eeprom_addr = []
    print filename
    f = open(filename,"r+")
    for line in f:
        addr,data=line.split()
        eeprom_content.append(int(data,2))
        eeprom_addr.append(int(addr,2))
    return 


def main (default_directory = '.'):

    in_filename = "eeprom_formatted_data.txt"

    f_in = open(in_filename, 'r')

    eeprom_content = []
    eeprom_addr = []

    for line in f_in:
        addr,data=line.split()
        print "%d 0x%X"%(int(addr,2), int(data,2))
        eeprom_content.append(int(data,2))
        eeprom_addr.append(int(addr,2))

    print "\nCONTENT"
    print eeprom_content
    print "\nADDR"
    print eeprom_addr

if __name__ == '__main__' :
    main()
