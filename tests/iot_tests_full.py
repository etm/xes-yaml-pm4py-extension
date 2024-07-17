import pytest

import copy
import tempfile

from pm4py import read, write
from pm4py.objects.iot.utils import cleaner
from pm4py.objects.iot.obj import IOTEventLog, IOTEvent, IOTTrace, Point, DataStream, MultiPoint, FilterSet
from pm4py.objects.iot.importer.xes.variants.xmlxes20 import State
from pm4py.objects.iot import apis
from pm4py.objects.iot.utils import verifier
from iot_tests import TestCase, SENSOR_FILES


point1 = Point(id='point1_id', timestamp=State.date_parser.apply('2023-04-28T17:18:20.0747454+02:00'), value='point1_val', source='point1_source', meta=[{'type':'System.String1'}])
point2 = Point(id='point2_id', timestamp=State.date_parser.apply('2021-04-28T17:18:20.0747454+02:00'), value='point2_val', source='point2_source', meta=[{'type':'System.String2'}])
point3 = Point(id='point3_id', timestamp=State.date_parser.apply('2021-04-28T17:18:20.0747454+02:00'), value='point3_val', source='point3_source', meta=[{'type':'System.String3'}])
point4 = Point(id='point4_id', timestamp=State.date_parser.apply('2018-04-28T17:18:20.0747454+02:00'), value='point4_val', source='point4_source', meta=[{'type':'System.String4'}])
point_add = Point(id='point5_id', timestamp=State.date_parser.apply('2018-04-28T17:18:20.0747454+02:00'), value='point5_val', source='point5_source', meta=[{'type':'System.String5'}])


@pytest.mark.parametrize("sensor_id", list(range(len(SENSOR_FILES))))
def test_sensor_data(sensor_id):
    path, modified = TestCase.SENSOR_DATA(sensor_id)
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)
    cleaner.remove_modified(modified)

def test_datastream_in_trace():
    path, modified = TestCase.DATASTREAM_IN_TRACE()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)
    assert len(log) == 2
    cleaner.remove_modified(modified)

def test_datacontext_in_trace():
    path, modified = TestCase.DATACONTEXT_IN_TRACE()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)
    assert len(log) == 1
    assert len(log[0]) == 2
    cleaner.remove_modified(modified)

def test_event_in_log():
    path, modified = TestCase.EVENT_IN_LOG()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    assert len(log) == 4
    assert type(log[0]) == IOTTrace
    assert type(log[1]) == IOTEvent
    assert type(log[2]) == IOTEvent
    assert type(log[3]) == IOTEvent
    assert len(log[0]) == 1
    assert type(log[0][0]) == IOTEvent

    cleaner.remove_modified(modified)


def test_multipoint():
    expected_datastream = DataStream(name='datastream2_name', source='datastream2_source')

    multipoint1 = MultiPoint(id='multipoint1_id', source='multipoint1_source', timestamp=State.date_parser.apply('2022-04-28T17:18:20.0747454+02:00'), meta=[{'type':'multipoint1_meta'}])
    multipoint1.append(copy.copy(point2))
    multipoint1.append(copy.copy(point2))

    multipoint2 = MultiPoint(id='multipoint2_id', source='multipoint2_source', timestamp=State.date_parser.apply('2023-04-28T17:18:20.0747454+02:00'), meta=[{'type':'multipoint2_meta'}])
    multipoint2.append(copy.copy(point3))

    expected_datastream.append(multipoint1)
    expected_datastream.append(multipoint2)
    expected_datastream.append(copy.copy(point1))

    path, modified = TestCase.MULTIPOINT()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    have_datastream = log[0][0][0]

    assert len(have_datastream) == len(expected_datastream)
    assert have_datastream == expected_datastream

    for i in range(len(expected_datastream)):
        assert have_datastream[i] == expected_datastream[i]

    cleaner.remove_modified(modified)


def test_get_traces_with_datastream():
    datastream1 = DataStream(name='datastream1_name', source='datastream1_source')
    datastream1.append(copy.copy(point1))
    trace1 = IOTTrace()
    trace1.attributes['attr_key'] = 'attr_val'
    trace1.append(datastream1)

    datastream2 = DataStream(name='datastream2_name', source='datastream2_source')
    datastream2.append(copy.copy(point2))
    trace2 = IOTTrace()
    trace2.append(datastream2)

    expected_traces = [trace1, trace2]

    path, modified = TestCase.GET_TRACES_WITH_DATASTREAM()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)
    have_traces = apis.get_traces_with_datastream(log)

    assert len(have_traces) == len(expected_traces)
    for i in range(len(have_traces)):
        assert have_traces[i] == expected_traces[i]
    cleaner.remove_modified(modified)


def test_count_datastreams_and_points_in_event():
    path, modified = TestCase.COUNT_DATASTRAMS_AND_POINTS_IN_EVENT()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    points_count = apis.count_datastreams_and_points_in_event(log[0][0])
    assert len(points_count) == 4
    assert points_count[0] == 2
    assert points_count[1] == 1
    assert points_count[2] == 4
    assert points_count[3] == 0

    cleaner.remove_modified(modified)


def test_find_all_stream_data_entries_in_event():
    datastream2 = DataStream(name='datastream2_name', source='datastream2_source')
    datastream2.stream_data_key = 'cpee:lifecycle:transition'
    datastream2.append(copy.copy(point2))
    datastream2.append(copy.copy(point1))
    datastream4 = DataStream(name='datastream4_name')
    datastream4.stream_data_key = 'lifecycle:transition'
    datastream4.append(copy.copy(point3))
    datastream4.append(copy.copy(point1))
    expected_datastreams = [datastream2, datastream4]

    path, modified = TestCase.FIND_ALL_STREAM_DATA_ENTRIES_IN_EVENT()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)
    have_datastreams = apis.find_all_stream_data_entries_in_event(log[0][0])

    assert len(have_datastreams) == len(expected_datastreams)

    for i in range(len(have_datastreams)):
        assert have_datastreams[i] == expected_datastreams[i]

    cleaner.remove_modified(modified)


def test_count_events_with_datastreams_in_trace():
    expected_counts = [2, 6, 0, 0]

    path, modified = TestCase.COUNT_EVENTS_WITH_DATASTREAMS_IN_TRACE()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    assert len(log) == 4

    for i in range(0, 4):
        assert expected_counts[i] == apis.count_events_with_datastreams_in_trace(log[i])

    cleaner.remove_modified(modified)


def test_count_points_in_multipoint_entry():
    path, modified = TestCase.COUNT_POINTS_IN_MULTIPOINT_ENTRY()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    expected_points_count = [6, 2, 0]
    have_points_count = []
    have_datastream = log[0][0][0]

    assert len(have_datastream) == 4

    for point in have_datastream:
        if isinstance(point, MultiPoint):
            have_points_count.append(apis.count_points_in_multipoint_entry(point))

    assert len(have_points_count) == len(expected_points_count)

    for i in range(len(have_points_count)):
        assert have_points_count[i] == expected_points_count[i]

    cleaner.remove_modified(modified)


def test_count_distinct_datacontext_groups_at_trace_level():
    expected_groups_count = [2, 4, 8]

    path, modified = TestCase.COUNT_DISTINCT_DATACONTEXT_GROUPS_AT_TRACE_LEVEL()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    assert len(log) == len(expected_groups_count)

    for i, trace in enumerate(log):
        assert apis.count_distinct_datacontext_groups_at_trace_level(trace) == expected_groups_count[i]

    cleaner.remove_modified(modified)


def test_add_sensor_value_to_event():
    """
        should add to datastream, empty multipoint
        should add to datastream, non-empty multipoint
        should add to multipoint in datastream
        shouldn't add, exist in datastream
        shouldn't add, exist in multipoint
    """
    expected_datastream1 = DataStream(name='datastream1_name', source='datastream1_source')
    expected_datastream1.append(copy.copy(point2))
    expected_datastream1.append(copy.copy(point_add))

    expected_datastream2 = DataStream(name='datastream2_name')
    multipoint2 = MultiPoint(timestamp=State.date_parser.apply('2021-04-28T17:18:20.0747454+02:00'))
    multipoint2.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream2.append(multipoint2)
    expected_datastream2.append(copy.copy(point_add))

    expected_datastream3 = DataStream(name='datastream3_name')
    multipoint3 = MultiPoint(timestamp=State.date_parser.apply('2018-04-28T17:18:20.0747454+02:00'))
    multipoint3.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    multipoint3.append(Point(id='point5_id', value='point5_val', source='point5_source', meta=[{'type':'System.String5'}]))
    expected_datastream3.append(multipoint3)


    expected_datastream4 = DataStream(name='datastream4_name')
    multipoint4 = MultiPoint(timestamp=State.date_parser.apply('2010-04-28T17:18:20.0747454+02:00'))
    multipoint4.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream4.append(multipoint4)
    expected_datastream4.append(copy.copy(point_add))

    expected_datastream5 = DataStream(name='datastream5_name')
    expected_datastream5.append(copy.copy(point2))
    multipoint5 = MultiPoint(id='point5_id')
    multipoint5.append(Point(timestamp=State.date_parser.apply('2018-04-28T17:18:20.0747454+02:00'), value='point5_val', source='point5_source', meta=[{'type':'System.String5'}]))
    expected_datastream5.append(multipoint5)

    path, modified = TestCase.ADD_SENSOR_VALUE_TO_EVENT()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    event = log[0][0]

    assert len(event) == 5

    apis.add_sensor_value_to_event(event, point_add)

    assert event[0] == expected_datastream1
    assert event[1] == expected_datastream2
    assert event[2] == expected_datastream3
    assert event[3] == expected_datastream4
    assert event[4] == expected_datastream5

    cleaner.remove_modified(modified)


def test_remove_sensor_value_from_event():
    """
        should remove from datastream, empty multipoint
        should remove from datastream, non-empty multipoint
        should remove from multipoint
        should not remove
        should remove many points from datastream
        should remove many points from multipoint
        should remove both from datastream and multipoint
    """
    expected_datastream1 = DataStream(name='datastream1_name', source='datastream1_source')
    expected_datastream1.append(copy.copy(point2))

    expected_datastream2 = DataStream(name='datastream2_name')
    multipoint2 = MultiPoint(timestamp=State.date_parser.apply('2021-04-28T17:18:20.0747454+02:00'))
    multipoint2.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream2.append(copy.copy(point2))
    expected_datastream2.append(multipoint2)

    expected_datastream3 = DataStream(name='datastream3_name')
    multipoint3 = MultiPoint(timestamp=State.date_parser.apply('2018-04-28T17:18:20.0747454+02:00'))
    multipoint3.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream3.append(copy.copy(point2))
    expected_datastream3.append(copy.copy(point2))
    expected_datastream3.append(copy.copy(point2))
    expected_datastream3.append(multipoint3)

    expected_datastream4 = DataStream(name='datastream4_name')
    multipoint4 = MultiPoint(timestamp=State.date_parser.apply('2010-04-28T17:18:20.0747454+02:00'))
    multipoint4.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream4.append(multipoint4)
    expected_datastream4.append(Point(timestamp=State.date_parser.apply('2019-04-28T17:18:20.0747454+02:00'),id='point5_id', value='point5_val', source='point5_source', meta=[{'type':'System.String5'}]))

    expected_datastream5 = DataStream(name='datastream5_name')
    multipoint5 = MultiPoint(timestamp=State.date_parser.apply('2021-04-28T17:18:20.0747454+02:00'))
    multipoint5.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream5.append(copy.copy(point2))
    expected_datastream5.append(copy.copy(point2))
    expected_datastream5.append(multipoint5)
    expected_datastream5.append(copy.copy(point2))

    expected_datastream6 = DataStream(name='datastream6_name')
    multipoint6 = MultiPoint(timestamp=State.date_parser.apply('2018-04-28T17:18:20.0747454+02:00'))
    multipoint6.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    multipoint6.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream6.append(copy.copy(point2))
    expected_datastream6.append(copy.copy(point2))
    expected_datastream6.append(copy.copy(point2))
    expected_datastream6.append(multipoint6)

    expected_datastream7 = DataStream(name='datastream7_name')
    multipoint7 = MultiPoint(timestamp=State.date_parser.apply('2018-04-28T17:18:20.0747454+02:00'))
    multipoint7.append(Point(id='point2_id', value='point2_val', source='point2_source', meta=[{'type':'System.String2'}]))
    expected_datastream7.append(copy.copy(point2))
    expected_datastream7.append(copy.copy(point2))
    expected_datastream7.append(copy.copy(point2))
    expected_datastream7.append(multipoint7)


    path, modified = TestCase.REMOVE_SENSOR_VALUE_FROM_EVENT()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    event = log[0][0]

    assert len(event) == 7
    apis.remove_sensor_value_from_event(event, point_add)

    assert event[0] == expected_datastream1
    assert event[1] == expected_datastream2
    assert event[2] == expected_datastream3
    assert event[3] == expected_datastream4
    assert event[4] == expected_datastream5
    assert event[5] == expected_datastream6
    assert event[6] == expected_datastream7

    cleaner.remove_modified(modified)


def test_sensor_values_of_specific_type():
    expected_values1 = ['point1_val', 'point1_val_d2', 'point1_val_d2_m1']
    expected_values2 = ['point2_val', 'point2_val_d2', 'point2_val_d2_m2']
    expected_values3 = ['point3_val', 'point3_val_d2', 'point3_val_d2_m3']
    expected_values4 = ['point4_val', 'point4_val_d2', 'point4_val_d2_m4']

    path, modified = TestCase.SENSOR_VALUES_OF_SPECIFIC_TYPE()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    event = log[0][0]

    assert len(event) == 2

    fset1 = FilterSet(id='point1_id')
    have_values1 = apis.sensor_values_of_specific_type(event, fset1)

    fset2 = FilterSet(timestamp=State.date_parser.apply('2022-04-28T17:18:20.0747454+02:00'))
    have_values2 = apis.sensor_values_of_specific_type(event, fset2)

    fset3 = FilterSet(source='point3_source')
    have_values3 = apis.sensor_values_of_specific_type(event, fset3)

    fset4 = FilterSet(meta=[{'type':'System.String4'}])
    have_values4 = apis.sensor_values_of_specific_type(event, fset4)

    assert have_values1 == expected_values1
    assert have_values2 == expected_values2
    assert have_values3 == expected_values3
    assert have_values4 == expected_values4

    cleaner.remove_modified(modified)


def test_allow_empty_multipoint():
    path, modified = TestCase.ALLOW_EMPTY_MULTIPOINT()
    cleaner.rewrite(path, modified)
    log = read.read_iot_xes(modified)

    cleaner.remove_modified(modified)

def count_lines_in_file(path):
    with open(path, 'r') as file:
        return len(file.readlines())

def test_exporter_multipoint():
    path, modified = TestCase.MULTIPOINT()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log

    cleaner.remove_modified(modified)


def test_exporter_datacontext():
    path, modified = TestCase.DATACONTEXT_IN_TRACE()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log

    cleaner.remove_modified(modified)


def test_exporter_datastream():
    path, modified = TestCase.DATASTREAM_IN_TRACE()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log
    cleaner.remove_modified(modified)

def test_exporter_empty_list():
    path, modified = TestCase.EXPORTER_EMPTY_LIST()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log
    cleaner.remove_modified(modified)


def test_exporter_datacontext_2():
    path, modified = TestCase.COUNT_DISTINCT_DATACONTEXT_GROUPS_AT_TRACE_LEVEL()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log

    cleaner.remove_modified(modified)

def test_exporter_event_in_log():
    path, modified = TestCase.EVENT_IN_LOG()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log

    cleaner.remove_modified(modified)


def test_exporter_as_string():
    from pm4py.objects.iot.exporter.xes import exporter as iot_xes_exporter
    from pm4py.util import constants
    path, modified = TestCase.EVENT_IN_LOG()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    serialized = iot_xes_exporter.serialize(expected_log)
    file = tempfile.NamedTemporaryFile(suffix='.xes')
    file.write(serialized)

    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log

    cleaner.remove_modified(modified)


def test_exporter_limitation():
    path, modified = TestCase.BIG_FILE_LIMITATION()
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log

    cleaner.remove_modified(modified)


@pytest.mark.parametrize("sensor_id", list(range(len(SENSOR_FILES))))
def test_exporter_sensor_data(sensor_id):
    path, modified = TestCase.SENSOR_DATA(sensor_id)
    cleaner.rewrite(path, modified)
    expected_log = read.read_iot_xes(modified)

    file = tempfile.NamedTemporaryFile(suffix='.xes')
    write.write_iot_xes(expected_log, file.name)
    have_log = read.read_iot_xes(file.name)

    assert count_lines_in_file(modified) == count_lines_in_file(file.name)
    assert have_log == expected_log

    cleaner.remove_modified(modified)
