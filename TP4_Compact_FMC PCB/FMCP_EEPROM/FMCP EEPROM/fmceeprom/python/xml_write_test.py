#!   /usr/bin/env   python
#    coding: utf8

# Copyright CERN, 2011
# Author: Matthieu Cattin <matthieu.cattin@cern.ch>
# Licence: GPL v2 or later.
# Website: http://www.ohwr.org

import sys
import time
import os
import libxml2


def main (default_directory = '.'):

    filename = "test.xml"
    doc = libxml2.parseFile(filename)
    root = doc.getRootElement()
    area = root.children

    while area is not None:
        if area.type == "element":
            areaContent = area.children
            while areaContent is not None:
                if areaContent.type == "element":
                    if areaContent.prop('name') == "Board_serial_number":
                        areaContent.setProp('content', '123456')
                        print "youhou"
                areaContent=areaContent.next
        area=area.next

    f = open(filename, 'w')
    doc.saveTo(f)
    f.close


if __name__ == '__main__' :
    main()
