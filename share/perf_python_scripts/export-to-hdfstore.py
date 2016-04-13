
import os
import sys
import pandas

sys.path.append(os.environ['PERF_EXEC_PATH'] + \
	'/scripts/python/Perf-Trace-Util/lib/Perf/Trace')

import Util 

# --- Helper stuff ---

# Small helper class just for convenience
# There must be a better way I do not know...
class Context(object):
    pass


def parse_perf_args(args):
    # The options we are looking for
    config = {
        'output': None,
        'output_group': None,
        'flush_size': 1000000
    }

    # Basic parsing stuff
    for arg in args:
        for key in config.keys():
            tmp = key + '='
            if not arg.startswith(tmp):
                continue
            config[key] = arg[len(tmp):]
            
    # Post parsing stuff

    if config['output'] is None:
        raise ValueError('No output filename')

    if config['output_group'] is None:
        config['output_group'] = 'events'

    config['flush_size'] = int(config['flush_size'])
        
    return config

def flush(context):
    # Convenience variables to create...
    flush_count = context.flush_count
    flush_next_count = flush_count + len(context.events['nsecs'])
    index_values = range(flush_count, flush_next_count)

    # ...the pandas dataframe
    index = pandas.Index(index_values)
    df = pandas.DataFrame(data=context.events, index=index)

    # Appending into a non-existing group seems OK; so there is no
    # need to handle a specific case
    context.store.append(context.config['output_group'], df)

    # Reinit / update the related fields
    context.flush_count = flush_next_count
    context.events = {
        'nsecs': [], 'cpu': [], 'event': [], 'pid': [], 'comm': []
    }

        
# --- The perf event callback function --- 

def trace_unhandled(event_name, context, fields):

    context = trace_unhandled.context
    events = context.events
    
    # Fill all the fields composing the dict thanks to the perf event
    nsecs = Util.nsecs(fields['common_s'], fields['common_ns'])
    events['nsecs'].append(nsecs)
    events['cpu'].append(fields['common_cpu'])
    events['event'].append(event_name)
    events['pid'].append(fields['common_pid'])
    events['comm'].append(fields['common_comm'])

    # If the events container size crossed the line...
    if len(events['nsecs']) >= context.config['flush_size']:
        flush(context)

# --- The perf init / cleanup functions --- 
        
def trace_begin():
    # Initialize a context
    context = Context()

    # Parse the script-specific options
    context.config = parse_perf_args(sys.argv[1:])

    # Instanciate an HDFStore according to the options
    context.store = pandas.HDFStore(context.config['output'])

    # Initialize the flush-related fields
    context.flush_count = 0
    context.events = {
        'nsecs': [], 'cpu': [], 'event': [], 'pid': [], 'comm': []
    }

    # Store the context as a field of the event callback instance
    trace_unhandled.context = context

    
def trace_end():
    # Force pending lines flushing
    flush(trace_unhandled.context)
