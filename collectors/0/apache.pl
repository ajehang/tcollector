#!/usr/bin/perl

###########################################################################
# Author: Ali Imran Jehangiri
# Last Changed: 
# Collects apache webhits
###########################################################################
## If the tmp directory doesn't exit create it                                                                                                                                                                   
$host_name = `hostname |awk -F"." '{print $2}' `;
$COLLECTION_INTERVAL=1;
$count=0;
## Create Base Line                                                                                                                                                                                              
unless ($ARGV[0]) {
    $log_path = '/var/log/apache2/access_log';
} else {
    $log_path = $ARGV[0];
}

$old_time = time();
open(PROCESS,"wc -l $log_path |");
$old_webhits = <PROCESS>;
close(PROCESS);
$old_webhits =~ s/[\s]*([0-9]+).*//;
$old=$1;
sleep($COLLECTION_INTERVAL);
while(count<1)
{
    $new_time = time();
    open(PROCESS,"wc -l $log_path |");
    $webhits = <PROCESS>;
    close(PROCESS);
    $webhits =~ s/[\s]*([0-9]+).*//;
	#	print $1;
    $new=$1;
	#calculate rate: webhits / second
    my $rate = ($new - $old)/($new_time - $old_time);
    print "apache.webhits $new_time $rate host=$host_name";
	$old=$new;
    $old_time=$new_time;
    sleep($COLLECTION_INTERVAL);
}

