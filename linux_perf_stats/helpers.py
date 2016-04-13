import pandas
import matplotlib as mpl

def str_to_ns(delay_str):

    NS_PER_US = 1000
    NS_PER_MS = 1000000
    NS_PER_S = 1000000000
    
    factor = 1
    tmp_str = delay_str.lower()

    if tmp_str.endswith('us'):
        factor = NS_PER_US
        tmp_str = tmp_str.replace('us', '')
    elif tmp_str.endswith('ms'):
        factor = NS_PER_MS
        tmp_str = tmp_str.replace('ms', '')
    elif tmp_str.endswith('s'):
        tmp_str = tmp_str.replace('s', '')
        factor = NS_PER_S
    else:
        tmp_str = tmp_str.replace('ns', '')

    return factor * int(tmp_str)

def filter_events(df, events):    
    criterion = df.event.map(lambda x: x in events)
    tmp = df.loc[criterion]
    return tmp.reset_index(drop = True)

def configure_plots(font_size = 10, fig_size = (13.0, 5.0), fig_dpi = 100):
    # Use default pandas plot theme
    pandas.options.display.mpl_style = 'default'

    # Additional Matplotlib stuff
    mpl.rcParams['font.size'] = font_size
    mpl.rcParams['figure.figsize'] = fig_size
    mpl.rcParams['savefig.dpi'] = fig_dpi
    mpl.rcParams['figure.subplot.bottom'] = .1
