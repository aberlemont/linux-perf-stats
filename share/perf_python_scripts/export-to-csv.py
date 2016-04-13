import os
import sys

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
        'split_size': 0
    }

    # Basic parsing stuff
    for arg in args:
        for key in config.keys():
            tmp = key + '='
            if not arg.startswith(tmp):
                continue
            config[key] = arg[len(tmp):]

    # Post-parsing check/init stuff

    # An output filename is mandatory
    if config['output'] is None:
        raise ValueError('No output filename')

    # Handle split size
    config['split_size'] = int(config['split_size'])
    if config['split_size'] > 0:
        # If a split size was defined, we need to inject a split index
        # into the filename
        split_fname = config['output'].split('.')
        old_suffix = split_fname[-1]
        new_suffix = 'SPLIT_IDX.' + old_suffix
        new_fname = '.'.join(split_fname[:-1] + [new_suffix])
        config['output'] = new_fname
        # Finally, let's define a flush limit to prevent perf from
        # holding all the events in memory
        config['split_size'] = 1000000
    
    return config


def flush(context):
    # Let's build the split filename if need be ...
    fname_pattern = context.config['output']
    split_idx_str = '{:03d}_'.format(context.file_count)
    fname = fname_pattern.replace('SPLIT_IDX', split_idx_str)

    # ...and dump header + lines into it...
    dump_header = not os.path.exists(fname)
    fd = open(fname, 'a')
    if dump_header:
        fd.write('nsecs,cpu,event,pid,comm\n')
    fd.writelines(context.lines)

    # ...and reinit/update the related fields
    context.lines = []
    context.file_count += 1


# --- The perf event callback function --- 

def trace_unhandled(event_name, context, fields):
    # Get the fields to serialize
    nsecs = Util.nsecs(fields['common_s'], fields['common_ns'])
    cpu = fields['common_cpu']
    pid = fields['common_pid']
    comm = fields['common_comm']

    # Generate the csv line
    line = ','.join((str(nsecs), str(cpu), event_name, str(pid), comm))
    line += '\n'

    # Append the line into the current set and...
    context = trace_unhandled.context
    context.lines.append(line)

    # ...write them into a file if need be
    if len(context.lines) > context.config['split_size']:
        flush(context)

    
# --- The perf init / cleanup functions --- 
        
def trace_begin():
    # Initialize a context
    context = Context()

    # Parse the script-specific options
    context.config = parse_perf_args(sys.argv[1:])

    # Init internal stuff for csv dumping
    context.lines = []
    context.file_count = 0

    # Store the context as a field of the event callback instance
    trace_unhandled.context = context

    
def trace_end():
    # Force pending lines flushing
    flush(trace_unhandled.context)
