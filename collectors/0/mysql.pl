#!/usr/bin/perl

###########################################################################
# Author: Ali Imran Jehangiri
# Last Changed: 
# Collects mySQL server metrics
###########################################################################


# You only need to grant usage privilege to the user getting the stats e.g.

$stats_command = "mysqladmin -u root  extended-status";
$host_name = `hostname |awk -F"." '{print $2}' `;

# YOU COULD MODIFY FOLLOWING
# To find out a list of all metrics please do mysqladmin extended-status
# MySQL keeps two types of metrics. Counters e.g. ones that keep increasing
# and absolute metrics ie. number of connections right now. For counters 
# we need to calculate rate ie. delta between timeA and timeB divided by time.
# If you need other metrics add them to either of the two hashes and specify
# the units e.g. bytes, connections, etc.
# Explanation what these metrics means can be found at
# http://dev.mysql.com/doc/refman/5.0/en/server-status-variables.html
%counter_metrics = (
	"Bytes_received" => "bytes",
	"Bytes_sent" => "bytes",
	"Com_delete" => "operations",
	"Com_insert" => "operations",
	"Com_replace" => "operations", 
	"Com_select" => "operations", 
	"Com_update" => "operations",
	"Key_reads" => "operations",
	"Qcache_hits" => "hits",
	"Questions" => "queries",
	"Connections" => "connections",
	"Threads_created" => "threads",
        "Slow_queries" => "queries",
        "Slow_launch_threads" => "threads",
        "Tc_log_page_waits" => "transaction",
        "Com_show_processlist" => "processlist"
);

%absolute_metrics = ( 
        "Threads_connected" => "threads",
	"Threads_running" => "threads",
);

# Where to store the last stats file
$tmp_dir_base="/tmp/mysqld_stats";
$tmp_stats_file=$tmp_dir_base . "/" . "mysqld_stats";

# If the tmp directory doesn't exit create it
if ( ! -d $tmp_dir_base ) {
	system("mkdir -p $tmp_dir_base");
}

###############################################################################
# We need to store a baseline with statistics. If it's not there let's dump 
# it into a file. Don't do anything else
###############################################################################
if ( ! -f $tmp_stats_file ) {
	print "Creating baseline. No output this cycle\n";
	system("$stats_command > $tmp_stats_file");
} else {

	######################################################
	# Let's read in the file from the last poll
	open(OLDSTATUS, "< $tmp_stats_file");
	
	while(<OLDSTATUS>)
	{
		if (/\s+(\S+)\s+\S+\s+(\S+)/) {
			$old_stats{$1}=${2};
		}	
	}
	$old_time = (stat $tmp_stats_file)[9];
	close(OLDSTATUS);

	#####################################################
	# Get the new stats
	#####################################################
	system("$stats_command > $tmp_stats_file");
	open(NEWSTATUS, "< $tmp_stats_file");	
	$new_time = time();
	while(<NEWSTATUS>)
	{
		if (/\s+(\S+)\s+\S+\s+(\S+)/) {
			$new_stats{$1}=${2};
		}
	}
	close(NEWSTATUS);
	my $time_difference = $new_time - $old_time;
	#################################################################################
	# Calculate deltas for counter metrics and send them to ganglia
	#################################################################################	
	while ( my ($metric, $units) = each(%counter_metrics) ) {
	        my $rate = ($new_stats{$metric} - $old_stats{$metric})/$time_difference; 
		if ( $rate < 0 ) {
			print "Something is fishy. Rate for " . $metric . " shouldn't be negative. Perhaps counters were reset. Doing nothing";
		} else {
			print "mysql.$metric $new_time  $rate host=$host_name";
								
		        }
	}	
	#################################################################################
	# Just send absolute metrics. No need to calculate delta
	#################################################################################
	while ( my ($metric, $units) = each(%absolute_metrics) ) {
		print "mysql.$metric $new_time $new_stats{$metric} host=$host_name";
	}

}
