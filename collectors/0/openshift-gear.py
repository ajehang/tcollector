#!/usr/bin/python
                                                                                                                                                                                               
###########################################################################
# Author: Ali Imran Jehangiri
# Last Changed: 
# Collects openshift cgroup data for openshift gears
###########################################################################

                                                                   
import os
import sys
import time

COLLECTION_INTERVAL = 60
rootdir="/cgroup/all/openshift"

def collectData(groups):
        cpu_usage = 0;
	user = 0;
	system = 0;
        ts = int(time.time())
# total CPU time (in nanoseconds) consumed by all tasks in this cgroup
        with open('/cgroup/all/openshift/%s/cpuacct.usage' % (groups,), 'r') as f:
                cpu_usage = int(f.readline())
                print("openshift.app.cpuacct.usage %d %s gear=%s" % (ts, cpu_usage, groups))
# CPU time is reported in the units defined by the USER_HZ variable. 				 
	with open('/cgroup/all/openshift/%s/cpuacct.stat' % (groups,), 'r') as f:
		lines = f.read().splitlines()
				
	for line in lines:
		data = line.split()
		if data[0] == "user":
			user = int(data[1])
			print("openshift.app.cpuacct.cputime %d %s gear=%s mode=user" % (ts, user, groups))
		elif data[0] == "system":
			system = int(data[1])
			print("openshift.app.cpuacct.cputime %d %s gear=%s mode=system" % (ts, system, groups))
# memory.limit_in_bytes reports the maximum amount of user memory (including file cache). the value is interpreted as bytes
        with open('/cgroup/all/openshift/%s/memory.limit_in_bytes' % (groups,), 'r') as f:
                memlimit=int(f.readline())
		print("openshift.app.memory.limit %d %s gear=%s" % (ts, memlimit, groups))

# reports the number of times that the memory limit has reached the value set in memory.limit_in_bytes
        with open('/cgroup/all/openshift/%s/memory.failcnt' % (groups,), 'r') as f:
		memfailcnt=int(f.readline())
                print("openshift.app.memory.failcnt %d %s gear=%s" % (ts, memfailcnt, groups))
# total_swap reports the total swap usage by the cgroup and all its child groups
# total_cache reports the total page cache, including tmpfs (shmem), in bytes used by cgroup and all its child groups
# total_rss anonymous and swap cache, not including tmpfs (shmem), in bytesused by cgroup and all its child groups
	with open('/cgroup/all/openshift/%s/memory.stat' % (groups,), 'r') as f:
		lines = f.read().splitlines()
	for line in lines:
                data = line.split()
                if data[0] == "total_rss":
                        mem_rss = int(data[1])
			print("openshift.app.memory.total_rss %d %s gear=%s" % (ts, mem_rss, groups))
		elif data[0] == "total_cache":
                        mem_cache = int(data[1])
			print("openshift.app.memory.total_cache %d %s gear=%s" % (ts, mem_cache, groups))
		elif data[0] == "total_swap":
                        mem_swap = int(data[1])
			print("openshift.app.memory.total_swap %d %s gear=%s" % (ts, mem_swap, groups))


def main():
 while True:
        for root, subFolders, files in os.walk(rootdir):
                        for folder in subFolders:
                                collectData(folder)
        sys.stdout.flush()
        time.sleep(COLLECTION_INTERVAL)

if __name__ == "__main__":
    main()

