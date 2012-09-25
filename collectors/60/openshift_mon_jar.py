#!/usr/bin/python
import os
import pwd
import re
import signal
import subprocess
import sys
import time

# We add those files to the classpath if they exist.
CLASSPATH = [
    "/Users/ali/tcollector/collectors/lib/test.jar",
]


# How many times, maximum, will we attempt to restart the  collector.
# If we reach this limit, we'll exit with an error.
MAX_RESTARTS = 10

TOP = False  # Set to True when we want to terminate.
RETVAL = 0    # Return value set by signal handler.

def kill(proc):
  """Kills the subprocess given in argument."""
  # Clean up after ourselves.
  proc.stdout.close()
  rv = proc.poll()
  if rv is None:
      os.kill(proc.pid, 15)
      rv = proc.poll()
      if rv is None:
          os.kill(proc.pid, 9) 
          rv = proc.wait() 
  print >>sys.stderr, "warning: proc exited %d" % rv
  return rv


def do_on_signal(signum, func, *args, **kwargs):
  """Calls func(*args, **kwargs) before exiting when receiving signum."""
  def signal_shutdown(signum, frame):
    print >>sys.stderr, "got signal %d, exiting" % signum
    func(*args, **kwargs)
    sys.exit(128 + signum)
  signal.signal(signum, signal_shutdown)


def main(argv):
   
    # Build the classpath.
    dir = os.path.dirname(sys.argv[0])
    jar = os.path.normpath(dir + "/../lib/test.jar")
    if not os.path.exists(jar):
        print >>sys.stderr, "WTF?!  Can't run, %s doesn't exist" % jar
        return 13
    classpath = [jar]
    for jar in CLASSPATH:
        if os.path.exists(jar):
            classpath.append(jar)
    classpath = ":".join(classpath)
    oshift = subprocess.Popen(
        ["java", "-Djavax.net.ssl.trustStore=/Users/ali/truststore.jks","-cp", classpath, "org.gwdg.cloud.opaas.test.Test","ed", "123"
         ], stdout=subprocess.PIPE, bufsize=1)
    do_on_signal(signal.SIGINT, kill, oshift)
    do_on_signal(signal.SIGPIPE, kill, oshift)
    do_on_signal(signal.SIGTERM, kill, oshift)
    try:
        prev_timestamp = 0
        while True:
            line = oshift.stdout.readline()

            if not line and oshift.poll() is not None:
                break  # Nothing more to read and process exited.
            elif len(line) < 4:
                print >>sys.stderr, "invalid line (too short): %r" % line
                continue
            #ignore diy metrics
            if len(line)<100:
                print line            
			#metric, timestamp, value = line.split(",",3);
            #print metric
    finally:
        kill(oshift)
        time.sleep(10)
        return 0  # Ask the tcollector to re-spawn us.


if __name__ == "__main__":
    sys.exit(main(sys.argv))
