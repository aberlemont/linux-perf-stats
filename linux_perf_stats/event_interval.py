import numpy
import pandas
import matplotlib as mpl
import matplotlib.pyplot as plt
from helpers import filter_events

def _add_intervals(df):    
    tmp = df.copy()
    tmp.index = pandas.Int64Index(range(-1, -1 + len(df)))
    tmp = tmp.reindex(df.index, method = 'ffill')
    
    tmp2 = df.copy()
    tmp2['next_cpu'] = tmp.cpu
    tmp2['next_event'] = tmp.event
    tmp2['next_nsecs'] = tmp.nsecs
    tmp2['duration'] = tmp2.next_nsecs - tmp2.nsecs
    
    return tmp2

def get_event_itv_quantile(df, 
                           evt1, evt2,
                           quantile_value = 0.95,
                           filter = False, cpu = 0):
    """Print specified quantile on time interval between 2 events

    This function takes as input a Pandas dataframe which should be
    composed of the following columns:
    - "nsecs": the timestamp at which the event occurred;
    - "cpu": the cpu/core in which the event occurred;
    - "event": the event name;

    Thanks to this dataframe, this function will return the specified
    quantile value (default: quantile-95) on the time interval between
    2 events.

    :param df: Pandas dataframe
    :param evt1: First event
    :param evt2: Second event
    :param filter: If the events do not follow each other in the trace \
    record, we should filter the other events (we keep only evt1 and \
    evt2); this can have a significant impact on the results.
    :param cpu: The CPU on which the events occurred (default: 0)
    """
    
    df = df.loc[df.cpu == cpu].reset_index(drop = True)
    if filter:
        df = filter_events(df, (evt1, evt2))
    df = _add_intervals(df)

    criteria = (df.event == evt1) & (df.next_event == evt2)
    df = df.loc[criteria]

    return tmp.duration.quantile(quantile_value)

def print_event_intervals(df, evt1, evt2, filter = False):
    """Print statistics on time interval between 2 events

    This function takes as input a Pandas dataframe which should be
    composed of the following columns:
    - "nsecs": the timestamp at which the event occurred;
    - "cpu": the cpu/core in which the event occurred;
    - "event": the event name;

    Thanks to this dataframe, this function will print statistics on
    the time interval between 2 events.

    :param df: Pandas dataframe
    :param evt1: First event
    :param evt2: Second event
    :param filter: If the events do not follow each other in the trace \
    record, we should filter the other events (we keep only evt1 and \
    evt2)
    """
    
    print 'Time interval statistics from', evt1, 'to', evt2,':'
    
    cpus = list(df.cpu.unique())
    cpus.sort()
    
    for cpu in cpus:
        print 'CPU', cpu
        
        local_events = df.loc[df.cpu == cpu].reset_index(drop = True)
        
        if filter:
            local_events = filter_events(local_events, (evt1, evt2))
        
        local_events = _add_intervals(local_events)
        
        criteria = (local_events.event == evt1) & \
            (local_events.next_event == evt2)
            
        print local_events.loc[criteria].duration.describe()

def plot_event_intervals(df, evt1, evt2, filter = False, cpu = 0):
    """Plot quantile diagram on time interval between 2 events

    This function takes as input a Pandas dataframe which should be
    composed of the following columns:
    - "nsecs": the timestamp at which the event occurred;
    - "cpu": the cpu/core in which the event occurred;
    - "event": the event name;

    Thanks to this dataframe, this function will plot a graphic on the
    time interval between 2 events.

    :param df: Pandas dataframe
    :param evt1: First event
    :param evt2: Second event
    :param filter: If the events do not follow each other in the trace \
    record, we should filter the other events (we keep only evt1 and \
    evt2)
    :param cpu: The CPU / core ID on which the plot will focus
    """

    df = df.loc[df.cpu == cpu].reset_index(drop = True)
    
    tmp = df
    
    if filter:
        tmp = filter_events(tmp, (evt1, evt2))
    
    tmp = _add_intervals(tmp)
    
    criteria = (tmp.event == evt1) & (tmp.next_event == evt2)
    tmp = tmp.loc[criteria]
    
    count_dn = tmp.groupby('duration', sort = True).size()
    count_cumsum_dn = (count_dn.cumsum() * 100) / count_dn.sum()

    plot = count_cumsum_dn.plot()
    plot.set_xlim(tmp.duration.min(), tmp.duration.quantile(0.99))
    plot.set_title(evt1 + ' -> ' + evt2 + ' times on CPU ' + str(cpu))
    plot.set_ylabel('Percentile (%)')
    plot.set_xlabel('Time interval (ns)')
