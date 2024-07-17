"""
    This is an apis and example usages for our extension
"""


def add_sensor_value_to_event(event, point):
    event.add_sensor_value(point)


def remove_sensor_value_from_event(event, point):
    event.remove_sensor_value(point)


def sensor_values_of_specific_type(event, fset):
    """ 
        Resulting set of values will be returned sorted
        fset is FilterSet()
    """
    return event.fetch_sensor_values(fset)


def get_traces_with_datastream(log):
    ret = []
    for trace in log:
        if trace.contains_datastream():
            ret.append(trace)

    return ret


def count_distinct_datacontext_groups_at_trace_level(trace):
    return trace.count_distinct_datacontext_groups()


def count_datastreams_and_points_in_event(event):
    points_count = []
    for datastream in event:
        points_count.append(datastream.count_points())

    return points_count


def find_all_stream_data_entries_in_event(event):
    ret = []
    for datastream in event:
        if datastream.is_stream_data():
            ret.append(datastream)
    return ret


def count_points_in_multipoint_entry(multipoint):
    return multipoint.count_points()


def count_events_with_datastreams_in_trace(trace):
    events_count = 0
    for event in trace:
        if event.contains_datastream():
            events_count = events_count + 1

    return events_count