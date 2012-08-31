#!/usr/bin/python
#
# Copyright (C) 2012 Piotr Kasprzak 
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.
#
"""VM stats based on libvirt for TSDB"""

# "virt.domain.state": 			state of libvirt domain:

# 	enum virDomainState {
# 		VIR_DOMAIN_NOSTATE	= 	0	: no state
# 		VIR_DOMAIN_RUNNING	= 	1	: the domain is running
# 		VIR_DOMAIN_BLOCKED	= 	2	: the domain is blocked on resource
# 		VIR_DOMAIN_PAUSED	= 	3	: the domain is paused by user
# 		VIR_DOMAIN_SHUTDOWN	= 	4	: the domain is being shut down
# 		VIR_DOMAIN_SHUTOFF	= 	5	: the domain is shut off
# 		VIR_DOMAIN_CRASHED	= 	6	: the domain is crashed
# 		VIR_DOMAIN_PMSUSPENDED	= 	7	: NB: this enum value will increase over time as new events are added to the libvirt API. It reflects the last state supported by this version of the libvirt API.
# 		VIR_DOMAIN_LAST		= 	8
# 	}

# "virt.domain.max_mem": 		the maximum memory in KBytes allowed
# "virt.domain.memory": 		the memory in KBytes used by the domain
# "virt.domain.nr_virt_cpu":		the number of virtual CPUs for the domain
# "virt.domain.cpu_time":		the CPU time used in milliseconds

# "virt.domain.interface.rx_bytes":
# "virt.domain.interface.rx_packets":
# "virt.domain.interface.rx_errs":
# "virt.domain.interface.rx_drop":
# "virt.domain.interface.tx_bytes":
# "virt.domain.interface.tx_packets":
# "virt.domain.interface.tx_errs":
# "virt.domain.interface.tx_drop":

# "virt.domain.disk.rd_req":		number of read requests
# "virt.domain.disk.rd_bytes":		number of read bytes
# "virt.domain.disk.wr_req":		number of write requests
# "virt.domain.disk.wr_bytes":		number of written bytes
# "virt.domain.disk.errs":		In Xen this returns the mysterious 'oo_req'.

import os
import sys
import time
import socket
import re
import pprint
import libvirt
import libxml2

# Poll interval in seconds

COLLECTION_INTERVAL = 1

def get_devices(document, xpath):
    """get list of specified devices from XML definition"""

    context 	= document.xpathNewContext()
    devices 	= []
    try:
        ret = context.xpathEval(xpath)
        for node in ret:
            device = None
            for child in node.children:
                if child.name == "target":
                    device = child.prop("dev")
            if device == None:
                continue
            devices.append(device)
    finally:
        if context != None:
            context.xpathFreeContext()
    return devices


def main():
    """libvirtstat main loop"""

    while True:

        ts = int(time.time())
        
	lv = libvirt.openReadOnly("qemu:///system")

	domain_ids = lv.listDomainsID()

	for domain_id in domain_ids:

		domain 		= lv.lookupByID(domain_id)
		domain_name	= domain.name()
		infos 		= domain.info()
		# Parse domain XML definition for devices
                #pprint.pprint(dir(domain))
                uid = domain.UUIDString()
                #print("uid= %s"           % (uid))
    		xml 		= domain.XMLDesc(0)
    		document 	= None
    		try:
        		document 	= libxml2.parseDoc(xml) 
                	interfaces 	= get_devices(document, "/domain/devices/interface")
			disks		= get_devices(document, "/domain/devices/disk")

    		except:
			continue
		finally:
			if document != None:
				document.freeDoc()

		# Data from "virDomainInfo" structure

		print("virt.domain.state %d %s vm=%s" 		% (ts, infos[0], uid))
		print("virt.domain.max_mem %d %s vm=%s"		% (ts, infos[1], uid))
		print("virt.domain.memory %d %s vm=%s"		% (ts, infos[2], uid))

                print("virt.domain.nr_virt_cpu %d %s vm=%s"  	% (ts, infos[3], uid))
                print("virt.domain.cpu_time %d %s vm=%s"  	% (ts, infos[4] / 1000000, uid))

		# Data from "virDomainInterfaceStatsStruct" structure

		for interface in interfaces:
			
			interface_stats = domain.interfaceStats(interface)

			print("virt.domain.interface.rx_bytes %d %s vm=%s interface=%s" 	% (ts, interface_stats[0], uid, interface))
                        print("virt.domain.interface.rx_packets %d %s vm=%s interface=%s" 	% (ts, interface_stats[1], uid, interface))
                        print("virt.domain.interface.rx_errs %d %s vm=%s interface=%s" 		% (ts, interface_stats[2], uid, interface))
                        print("virt.domain.interface.rx_drop %d %s vm=%s interface=%s" 		% (ts, interface_stats[3], uid, interface))
                        print("virt.domain.interface.tx_bytes %d %s vm=%s interface=%s" 	% (ts, interface_stats[4], uid, interface))
                        print("virt.domain.interface.tx_packets %d %s vm=%s interface=%s" 	% (ts, interface_stats[5], uid, interface))
                        print("virt.domain.interface.tx_errs %d %s vm=%s interface=%s" 		% (ts, interface_stats[6], uid, interface))
                        print("virt.domain.interface.tx_drop %d %s vm=%s interface=%s" 		% (ts, interface_stats[7], uid, interface))

		# Data from "virDomainBlockStatsStruct" structure

		for disk in disks:

			block_stats = domain.blockStats(disk)

			print("virt.domain.disk.rd_req %d %s vm=%s disk=%s"			% (ts, block_stats[0], uid, disk))
                        print("virt.domain.disk.rd_bytes %d %s vm=%s disk=%s"                  	% (ts, block_stats[1], uid, disk))
                        print("virt.domain.disk.wr_req %d %s vm=%s disk=%s"                   	% (ts, block_stats[2], uid, disk))
                        print("virt.domain.disk.wr_bytes %d %s vm=%s disk=%s"                 	% (ts, block_stats[3], uid, disk))
                        print("virt.domain.disk.errs %d %s vm=%s disk=%s"                     	% (ts, block_stats[4], uid, disk))

        sys.stdout.flush()
        time.sleep(COLLECTION_INTERVAL)

if __name__ == "__main__":
    main()

