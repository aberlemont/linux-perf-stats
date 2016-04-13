import numpy
import pandas
import matplotlib as mpl
import matplotlib.pyplot as plt
from helpers import filter_events

def print_event_counts(df, event_to_count, event_before, event_after = None):
    """Print statistiscs on count of event between other events

    This function takes as input a Pandas dataframe which should be
    composed of the following columns:
    - "nsecs": the timestamp at which the event occurred;
    - "cpu": the cpu/core in which the event occurred;
    - "event": the event name;

    Thanks to this dataframe, this function will print statistics on
    the number of events which occurred between 2 (or 1) other events.

    :param df: Pandas dataframe
    :param event_to_count: The event the occurrence should be counted
    :param event_before: The event before the event to count
    :param event_after: The event after the event to count; this \
    argument could be left unfilled, in such a case this function will \
    count the event "event_to_count" between 2 events "event_before".
    """
    
    # Get a list of events we should filter
    events = [event_to_count, event_before]
    if event_after:
        events.append(event_after)

    # Keep only the selected events
    # Note: if event_after was filled, it will be useful only here;
    # the corresponding entries will be kept and will stop forward
    # fillna method
    selected_events = filter_events(df, events)

    print 'Counts of events', events[0], 'between the events', events[1:]
    
    cpus = list(selected_events.cpu.unique())
    cpus.sort()
    
    for cpu in cpus:

        tmp = selected_events.loc[selected_events.cpu == cpu]
        tmp = tmp.reset_index(drop = True)
    
        # Add two new columns: 
        # - The column fwd_event for finding out the "begin event" of the
        #  current event
        # - The column fwd_nsecs will be useful at group-by time
        tmp['fwd_event'] = tmp.event
        tmp['fwd_nsecs'] = tmp.nsecs

        # Remove all values of the lines corresponding to the events we
        # should count
        tmp.fwd_event.loc[tmp.event == event_to_count] = None
        tmp.fwd_nsecs.loc[tmp.event == event_to_count] = None
    
        # Fill missing values (those corresponding to the event we should
        # count); thus, we will be able to perform the group-by on the
        # column fwd_nsecs, all the events to be counted will have the
        # same value as the event_before's one
        tmp = tmp.fillna(method = 'ffill')
    
        # Keep only the events between the before and after events
        criteria = (tmp.event == event_to_count) & \
                   (tmp.fwd_event == event_before)
        events_to_count = tmp.loc[criteria]
    
        # Last step: the group-by on counting purpose
        count_nsecs = events_to_count.groupby('fwd_nsecs', sort = True).size()
    
        # Print the results
        print 'CPU', cpu
        print count_nsecs.describe()

def plot_event_counts(df, event_to_count,
                      event_before, event_after = None, cpu = 0):
    """Plot quantile diagram on count of event between other events

    This function takes as input a Pandas dataframe which should be
    composed of the following columns:
    - "nsecs": the timestamp at which the event occurred;
    - "cpu": the cpu/core in which the event occurred;
    - "event": the event name;

    Thanks to this dataframe, this function will plot a graphic on the
    number of events which occurred between 2 (or 1) other events.

    :param df: Pandas dataframe
    :param event_to_count: The event the occurrence should be counted
    :param event_before: The event before the event to count
    :param event_after: The event after the event to count; this \
    argument could be left unfilled, in such a case this function will \
    count the event "event_to_count" between 2 events "event_before"
    :param cpu: The CPU / core ID on which the plot will focus
    """
    
    df = df.loc[df.cpu == cpu].reset_index(drop = True)

    # Get a list of events we should filter
    events = [event_to_count, event_before]
    if event_after:
        events.append(event_after)
    
    # Keep only the selected events
    # Note: if event_after was filled, it will be useful only here;
    # the corresponding entries will be kept and will stop forward
    # fillna method
    tmp = filter_events(df, events)
        
    # Add two new columns: 
    # - The column fwd_event for finding out the "begin event" of the
    #  current event
    # - The column fwd_nsecs will be useful at group-by time
    tmp['fwd_event'] = tmp.event
    tmp['fwd_nsecs'] = tmp.nsecs

    # Remove all values of the lines corresponding to the events we
    # should count
    tmp.fwd_event.loc[tmp.event == event_to_count] = None
    tmp.fwd_nsecs.loc[tmp.event == event_to_count] = None

    # Fill missing values (those corresponding to the event we should
    # count); thus, we will be able to perform the group-by on the
    # column fwd_nsecs, all the events to be counted will have the
    # same value as the event_before's one
    tmp = tmp.fillna(method = 'ffill')

    # Keep only the events between the begin and end events
    criteria = (tmp.event == event_to_count) & (tmp.fwd_event == event_before)
    events_to_count = tmp.loc[criteria]

    # Last step: the group-by on counting purpose
    count_nsecs = events_to_count.groupby('fwd_nsecs', sort = True).size()
    tmp_count = pandas.DataFrame(data = {'count': count_nsecs})
    count_btw = tmp_count.groupby('count', sort = True).size()
    count_cumsum_btw = (count_btw.cumsum() * 100) / count_btw.sum()

    plot = count_cumsum_btw.plot(label = 'Cumulative sum')
    plot.set_xlim(count_nsecs.min(), count_nsecs.quantile(0.99))
    plot.set_title('Counts of ' + event_to_count +
                   '\nbetween ' + str(events[1:]) + '\n(CPU:' + str(cpu) + ')')
    plot.set_ylabel('Percentile (%)')
    plot.set_xlabel('Event count')
