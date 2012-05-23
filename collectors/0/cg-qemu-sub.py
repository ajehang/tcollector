#!/usr/bin/python
# Copyright (C) 2012 Ali Imran Jehangiri
import os
import sys
import time

rootdir="/dev/cgroups/cpuacct/sysdefault/libvirt/qemu"
def collectData(groups):
        cpu_usage = 0;
	user = 0;
	system = 0;
        ts = int(time.time())
# total CPU time (in nanoseconds) consumed by all tasks in this cgroup
        with open('/dev/cgroups/cpuacct/sysdefault/libvirt/qemu/%s/cpuacct.usage' % (groups,), 'r') as f:
                cpu_usage = int(f.readline())
                print("cgroup.domain.cpuacct.usage %d %s vm=%s" % (ts, cpu_usage, groups))
# CPU time is reported in the units defined by the USER_HZ variable. 				 
	with open('/dev/cgroups/cpuacct/sysdefault/libvirt/qemu/%s/cpuacct.stat' % (groups,), 'r') as f:
		lines = f.read().splitlines()
				
	for line in lines:
		data = line.split()
		if data[0] == "user":
			user = int(data[1])
			print("cgroup.domain.cpuacct.cputime %d %s vm=%s mode=user" % (ts, user, groups))
		elif data[0] == "system":
			system = int(data[1])
			print("cgroup.domain.cpuacct.cputime %d %s vm=%s mode=system" % (ts, system, groups))
				
# total_swap reports the total swap usage by the cgroup and all its child groups
# total_cache reports the total page cache, including tmpfs (shmem), in bytes used by cgroup and all its child groups
# total_rss anonymous and swap cache, not including tmpfs (shmem), in bytesused by cgroup and all its child groups
	with open('/dev/cgroups/memory/sysdefault/libvirt/qemu/%s/memory.stat' % (groups,), 'r') as f:
		lines = f.read().splitlines()
	for line in lines:
                data = line.split()
                if data[0] == "total_rss":
                        mem_rss = int(data[1])
			print("cgroup.domain.memory.total_rss %d %s vm=%s" % (ts, mem_rss, groups))
		elif data[0] == "total_cache":
                        mem_cache = int(data[1])
			print("cgroup.domain.memory.total_cache %d %s vm=%s" % (ts, mem_cache, groups))
		elif data[0] == "total_swap":
                        mem_swap = int(data[1])
			print("cgroup.domain.memory.total_swap %d %s vm=%s" % (ts, mem_swap, groups))


def main():
        for root, subFolders, files in os.walk(rootdir):
                        for folder in subFolders:
                                collectData(folder)
if __name__ == "__main__":
    main()

