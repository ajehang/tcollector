 = 0

        # package up the data you want to submit
        hps_metric = GangliaMetricObject('apache_hits', hits_per_second, units='hps')
        gps_metric = GangliaMetricObject('apache_gets', gets_per_second, units='hps')
        avgdur_metric = GangliaMetricObject('apache_avg_dur', avg_req_time, units='sec')
        ninetieth_metric = GangliaMetricObject('apache_90th_dur', ninetieth_element, units='sec')
        twops_metric = GangliaMetricObject('apache_200', two_per_second, units='hps')
        threeps_metric = GangliaMetricObject('apache_300', three_per_second, units='hps')
        fourps_metric = GangliaMetricObject('apache_400', four_per_second, units='hps')
        fiveps_metric = GangliaMetricObject('apache_500', five_per_second, units='hps')

        # return a list of metric objects
        return [ hps_metric, gps_metric, avgdur_metric, ninetieth_metric, twops_metric, threeps_metric, fourps_metric, fiveps_metric, ]
