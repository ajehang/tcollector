#!/usr/bin/perl
#
# a simple script to report per user stats for openshift users to opentsdb

$COLLECTION_INTERVAL=1;
$count=0;

my $users,@ps; 

# RS: get ps aux output and skip the first line
# RS: ps has different behaviour on IRIX vs Linux
my $uname=`uname`;
if ( $uname =~ /Linux/ ) 
{
        @ps=`ps aux| grep -v USER`;
}else{
        # RS: pcpu is repeated because this ps doesn't give %mem stats
        @ps=`ps -eo user,pid,pcpu,pcpu,vsz,rss,tty,state,stime,time,comm`;
}


# RS: iterate over each line of the ps output
foreach my $line (@ps) 
{
        # RS: eat any leading whitespace
        $line =~ s/^\s+//;
        
        # RS: split the line on whitespace, assigning vars
        my ($user,$pid,$cpu,$mem,$vsz,$rss,$tty,$stat,$start,$time,$command,@args) = split(/\s+/, $line);     

        # RS: populate the hash %users with references to the cumulative cpu,memz,time vars
        $users->{$user}{cpu}+=$cpu;
        $users->{$user}{mem}+=$mem;
        $users->{$user}{vsz}+=$vsz;
        # RS: calculate the time in seconds rather than min:sec
        my ($min,$sec)=split(/:/,$time);
        $sec+=($min*60);
        $users->{$user}{time}+=$time;
        $users->{$user}{procs}+=1; # total number of procs per user
 }

# RS: for each openshift user, send the stats to opentsdb
while(count<1){
    foreach my $user (keys %$users)
    {
        $new_time = time();        
        if($user =~/\d+/)
         {
	     ($login,$pass,$uid,$gid)=getpwuid($user);
	     print "openshift.user.cpu_percent $new_time $users->{$user}{cpu} app=$login\n";
	     print "openshift.user.mem_vsz $new_time $users->{$user}{vsz} app=$login\n";  
	# }        
       # if($user=~/\d+/)
	#{
	    #($login,$pass,$uid,$gid)=getpwuid($user);
	    print "openshift.user.cpu_total $new_time $users->{$user}{time} app=$login\n";
        #}
	
        #if($user=~/\d+/)
	#{
	   # ($login,$pass,$uid,$gid)=getpwuid($user);
	    print "openshift.user.procs_total $new_time $users->{$user}{procs} app=$login\n";
	#}
	 }
    }
sleep($COLLECTION_INTERVAL);
}
