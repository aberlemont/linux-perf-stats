import matplotlib as mpl
import matplotlib.pyplot as plt

from .helpers import str_to_ns

def plot_event_timeline(df, offset = 0, delay = '1ms', events = None):
    """Plot events occurences on a timeline graph

    This function takes as input a Pandas dataframe which should be
    composed of the following columns:
    - "nsecs": the timestamp at which the event occurred;
    - "cpu": the cpu/core in which the event occurred;
    - "event": the event name;

    Thanks to this dataframe, this function will display the events in
    a timeline graph.

    :param df: Pandas dataframe
    :param offset: The parameter offset and delay define a time window \
    to select the event to display; offset is the start edge
    :param delay: The parameter offset and delay define a time window \
    to select the event to display; offset is the stop edge
    :param events: If events is set, the input dataframe will be \
    filtered thanks to the subset of event
    """

    if isinstance(offset, str):
        offset = str_to_ns(offset)

    if isinstance(delay, str):
        delay = str_to_ns(delay)
        
    first_ns = df.nsecs.iloc[0] + offset
    last_ns = first_ns + delay

    fig, pt = plt.subplots()

    all_events = df.loc[(df.nsecs >= first_ns) & (df.nsecs < last_ns)]
    plot_value = 0

    if events is None:
        events = list(all_events.event.unique())
    
    for i, event in enumerate(events):
        
        tmp = all_events.loc[all_events.event == event]

        cpus = list(tmp.cpu.unique())
        cpus.sort()

        for cpu in cpus:
            plot_value += 1
        
            tmp2 = tmp.loc[tmp.cpu == cpu].copy()
            tmp2['plot_value'] = plot_value
            tmp2['usecs'] = (tmp.nsecs - first_ns) / float(10 ** 3)
                
            label = event + ' events'
            label += ' on CPU {:d}'.format(cpu)
            label += '(value: {:d})'.format(plot_value)
            pt.plot(tmp2.usecs, tmp2.plot_value, '.', label = label)
    
    labels_area = 3
    pt.set_ylim(0, plot_value + labels_area)
    last_us = (last_ns - first_ns) / float(10 ** 3) 
    pt.set_xlim(-10, last_us + 5)
    pt.set_title('Events display')
    pt.set_ylabel('Events')
    pt.set_xlabel('Time (us)')
    pt.legend()
