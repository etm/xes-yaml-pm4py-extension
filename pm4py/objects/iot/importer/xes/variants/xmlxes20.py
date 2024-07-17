import os, gzip, sys, json

from enum import Enum
from pm4py.util import constants, xes_constants, exec_utils
from pm4py.util.dt_parsing import parser as dt_parser
from pm4py.objects.log.obj import XESExtension
from pm4py.objects.iot.utils import verifier
from pm4py.objects.iot import constants as xes_iot_constants
from pm4py.objects.iot.obj import IOTEventLog, IOTTrace, IOTEvent, DataStream, DataContext, Point, MultiPoint
from pm4py.objects.iot.exceptions import UnexpectedStateError, UnexpectedAttributeError, InvalidAttributeError, AttributeShouldBeNoneError, AttributeShouldNotBeNoneError, NestedAttributeShouldBeEmptyError, NestedAttributeShouldNotBeEmptyError, PresentAttributeError, UnexpectedMultipleLogError

class StateProcess(Enum):
    ATTRIBUTE_COMPLETED = 'process_attribute'
    POINT_COMPLETED = 'process_point'
    DATASTREAM_COMPLETED = 'process_datastream'
    DATACONTEXT_COMPLETED = 'process_datacontext'
    EVENT_COMPLETED = 'process_event'
    TRACE_COMPLETED = 'process_trace'
    MULTIPOINT_COMPLETED = 'process_multipoint'
    LOG_COMPLETED = 'process_log'
    GLOBAL_SCOPE_COMPLETED = 'process_global_scope'


class Parameters(Enum):
    ENCODING = "encoding"
    APPLY_VERIFIER = "apply_verifier"


# Attributes for different states during Parser execution
class State:
    date_parser = dt_parser.get()
    def __init__(self):
        self.log = None
        self.global_scope = None
        self.trace = None
        self.event = None
        self.datastream = None
        self.datacontext = None
        self.multipoint = None
        self.point = None
        self.point_meta = None # for nested meta attribute 
        self.point_source = None # for nested source attribute
        self.stream_data_key = None
        self.nested_key = []
        self.nested_datacontext = []
        self.line_count = 0
        self.debug = xes_iot_constants.DEBUG

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        return self.__dict__


def apply(filename, parameters=None):
    return import_log(filename, parameters)


def import_log(filename, parameters=None):
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)
    apply_verifier = exec_utils.get_param_value(Parameters.APPLY_VERIFIER, parameters, xes_iot_constants.DEFAULT_VERIFIER)

    is_compressed = filename.endswith(".gz")
    file_size = os.stat(filename).st_size

    if is_compressed:
        f = gzip.open(filename, mode="rb")
    else:
        f = open(filename, "rb")

    log = import_log_from_file_object(f, encoding, file_size=file_size, parameters=parameters)
    f.close()

    if apply_verifier:
        verifier.verify(log)

    return log


def inject_attribute(nested_attr, key, value):
    if isinstance(nested_attr, list):
        nested_attr.append({key:value})
    elif isinstance(nested_attr, dict):
        #disallow multiple attributes with equal key
        if key in nested_attr:
            raise PresentAttributeError('nested_attr', key, nested_attr[key])
        nested_attr[key] = value
    else:
        raise UnexpectedAttributeError('nested_attr', nested_attr)


def process_attribute(tag, content, st):
    """
        Allow nested lists as attributes
        Returns:
            ATTRIBUTE_COMPLETED -> if processed all attributes
    """
    if len(st.nested_key) == 0:
        raise NestedAttributeShouldNotBeEmptyError('st.nested_key')
    if len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        inject_attribute(st.nested_key[-1], key, value)
    elif len(content) == 3 and tag.startswith(xes_constants.TAG_LIST):
        key = content[1]
        new_list = list()
        inject_attribute(st.nested_key[-1], key, new_list)
        if not content[2].lstrip().startswith('/>'):
            st.nested_key.append(new_list)
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_LIST):
        st.nested_key.pop()
    else:
        raise InvalidAttributeError('in process_attribute', tag, content)

    if len(st.nested_key) == 0:
        return StateProcess.ATTRIBUTE_COMPLETED


def process_point(tag, content, st):
    """
        Returns:
            POINT_COMPLETED -> if finished processing point
    """
    if st.point is None:
        raise AttributeShouldNotBeNoneError('st.point')

    if st.point_meta is not None:
        if process_attribute(tag, content, st) == StateProcess.ATTRIBUTE_COMPLETED:
            set_attribute_point(st.point, xes_iot_constants.TAG_STREAM_META, st.point_meta)
            st.point_meta = None
    elif st.point_source is not None:
        if process_attribute(tag, content, st) == StateProcess.ATTRIBUTE_COMPLETED:
            set_attribute_point(st.point, xes_iot_constants.TAG_STREAM_SOURCE, st.point_source)
            st.point_source = None
    elif len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        set_attribute_point(st.point, key, value)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_META:
        if st.point_meta is not None:
            raise AttributeShouldBeNoneError('st.point_meta', st.point_meta)
        
        #allow empty stream:meta list
        if content[2].lstrip().startswith('/>'):
            set_attribute_point(st.point, xes_iot_constants.TAG_STREAM_META, list())
        else:
            st.point_meta = list()
            if len(st.nested_key) > 0:
                raise NestedAttributeShouldBeEmptyError('st.nested_key', st.nested_key)
            st.nested_key.append(st.point_meta)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_SOURCE:
        if st.point_source is not None:
            raise AttributeShouldBeNoneError('st.point_source', st.point_source)
        
        #allow empty stream:source list
        if content[2].lstrip().startswith('/>'):
            set_attribute_point(st.point, xes_iot_constants.TAG_STREAM_SOURCE, list())
        else:
            st.point_source = list()
            if len(st.nested_key) > 0:
                raise NestedAttributeShouldBeEmptyError('st.nested_key', st.nested_key)
            st.nested_key.append(st.point_source)
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_LIST):
        if st.debug:
            print('END_POINT')
        return StateProcess.POINT_COMPLETED
    else:
        raise UnexpectedStateError(process_point, st)


def process_multipoint(tag, content, st):
    """
        Returns:
            MULTIPOINT_COMPLETED -> if finished processing multipoint
    """
    if st.multipoint is None:
        raise AttributeShouldNotBeNoneError('st.multipoint')
    
    if st.point is not None:
        if process_point(tag, content, st) == StateProcess.POINT_COMPLETED:
            st.multipoint.append(st.point)
            st.point = None
    elif st.point_meta is not None:
        if process_attribute(tag, content, st) == StateProcess.ATTRIBUTE_COMPLETED:
            set_attribute_multipoint(st.multipoint, xes_iot_constants.TAG_STREAM_META, st.point_meta)
            st.point_meta = None
    elif st.point_source is not None:
        if process_attribute(tag, content, st) == StateProcess.ATTRIBUTE_COMPLETED:
            set_attribute_multipoint(st.multipoint, xes_iot_constants.TAG_STREAM_SOURCE, st.point_source)
            st.point_source = None
    elif len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        set_attribute_multipoint(st.multipoint, key, value)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_META:
        if st.point_meta is not None:
            raise AttributeShouldBeNoneError('st.point_meta', st.point_meta)
        
        #allow empty stream:meta list
        if content[2].lstrip().startswith('/>'):
            set_attribute_multipoint(st.multipoint, xes_iot_constants.TAG_STREAM_META, st.point_meta)
        else:
            st.point_meta = list()
            if len(st.nested_key) > 0:
                raise NestedAttributeShouldBeEmptyError('st.nested_key', st.nested_key)
            st.nested_key.append(st.point_meta)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_SOURCE:
        if st.point_source is not None:
            raise AttributeShouldBeNoneError('st.point_source', st.point_source)
        
        #allow empty stream:source list
        if content[2].lstrip().startswith('/>'):
            set_attribute_multipoint(st.multipoint, xes_iot_constants.TAG_STREAM_SOURCE, st.point_source)
        else:
            st.point_source = list()
            if len(st.nested_key) > 0:
                raise NestedAttributeShouldBeEmptyError('st.nested_key', st.nested_key)
            st.nested_key.append(st.point_source)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_POINT:
        if st.debug:
            print('START_POINT')
        st.point = Point()
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_LIST):
        if st.debug:
            print('END_MULTIPOINT')
        return StateProcess.MULTIPOINT_COMPLETED
    else:
        raise UnexpectedStateError(process_multipoint, st)


def process_datastream(tag, content, st):
    """
        Returns:
            DATASTREAM_COMPLETED -> if finished processing datastream
    """
    if st.datastream is None:
        raise AttributeShouldNotBeNoneError('st.datastream')

    if st.multipoint is not None:
        if process_multipoint(tag, content, st) == StateProcess.MULTIPOINT_COMPLETED:
            st.datastream.append(st.multipoint)
            st.multipoint = None
    elif st.point is not None:
        if process_point(tag, content, st) == StateProcess.POINT_COMPLETED:
            st.datastream.append(st.point)
            st.point = None
    elif len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        set_attribute_datastream(st.datastream, key, value)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_POINT:        
        if st.debug:
            print('START_POINT')
        st.point = Point()
        if content[2].lstrip().startswith('/>'):
            # allow empty point
            st.datastream.append(st.point)
            st.point = None
            if st.debug:
                print('END_POINT')
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_MULTIPOINT:
        if st.debug:
            print('START_MULTIPOINT')
        st.multipoint = MultiPoint()
        if content[2].lstrip().startswith('/>'):
            # allow empty multipoint
            st.datastream.append(st.multipoint)
            st.multipoint = None
            if st.debug:
                print('END_MULTIPOINT')
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_LIST):
        if st.debug:
            print('END_DATASTREAM')
        return StateProcess.DATASTREAM_COMPLETED
    else:
        raise UnexpectedStateError(process_datastream, st)


def process_event(tag, content, st):
    """
        Returns:
            EVENT_COMPLETED -> if finished processing event
    """
    if st.event is None:
        raise AttributeShouldNotBeNoneError('st.event')
    
    if st.datastream is not None:
        if process_datastream(tag, content, st) == StateProcess.DATASTREAM_COMPLETED:
            st.event.append(st.datastream)
            st.datastream = None
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_DATASTREAM:
        if st.debug:
            print('START_DATASTREAM')
        st.datastream = DataStream()
        if st.stream_data_key is not None:
            #this datastream coming from lifecycle:transition
            st.datastream.stream_data_key = st.stream_data_key
            st.stream_data_key = None
    elif len(content) == 5 and content[1].endswith(xes_iot_constants.LIFECYCLE_TRANSITION) and content[3] == xes_iot_constants.STREAM_DATA:
        if st.stream_data_key is not None:
            raise AttributeShouldBeNoneError('st.stream_data_key', st.stream_data_key)
        st.stream_data_key = content[1]
    elif len(st.nested_key) > 0:
        #allow nested attributes
        processed = process_attribute(tag, content, st)
    elif len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        inject_attribute(st.event.attributes, key, value)
    elif len(content) == 3 and tag.startswith(xes_constants.TAG_LIST):
        key = content[1]
        new_list = list()
        inject_attribute(st.event.attributes, key, new_list)
        if not content[2].lstrip().startswith('/>'):
            st.nested_key.append(st.event.attributes[key])
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_EVENT):
        if st.debug:
            print('END_EVENT')
        return StateProcess.EVENT_COMPLETED
    else:
        raise UnexpectedStateError(process_event, st)


def process_datacontext(tag, content, st):
    """
        Returns:
            DATACONTEXT_COMPLETED -> if finished processing datacontext
    """
    if st.datacontext is None:
        raise AttributeShouldNotBeNoneError('st.datacontext')
    if len(st.nested_datacontext) == 0:
        raise NestedAttributeShouldNotBeEmptyError('st.nested_datacontext')
    
    if st.datastream is not None:
        if process_datastream(tag, content, st) == StateProcess.DATASTREAM_COMPLETED:
            st.nested_datacontext[-1].append(st.datastream)
            st.datastream = None
    elif len(content) == 3 and tag.startswith(xes_constants.TAG_LIST) and content[1] == xes_iot_constants.TAG_STREAM_DATASTREAM:
        if st.datastream is not None:
            raise AttributeShouldBeNoneError('st.datastream', st.datastream)
        st.datastream = DataStream()
        if st.debug:
            print('START_DATASTREAM')
    elif len(content) == 3 and tag.startswith(xes_constants.TAG_LIST) and content[1] == xes_iot_constants.TAG_STREAM_DATACONTEXT:
        new_datacontext = DataContext()
        st.nested_datacontext[-1].append(new_datacontext)
        st.nested_datacontext.append(new_datacontext)
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_LIST):
        if st.debug:
            print('END_DATACONTEXT')
        st.nested_datacontext.pop()
        if len(st.nested_datacontext) == 0:
            return StateProcess.DATACONTEXT_COMPLETED
    else:
        raise UnexpectedStateError(process_datacontext, st)


def process_trace(tag, content, st):
    """
        Returns:
            TRACE_COMPLETED -> if finished processing trace
    """
    if st.trace is None:
        raise AttributeShouldNotBeNoneError('st.trace')
    
    if st.datacontext is not None:
        if process_datacontext(tag, content, st) == StateProcess.DATACONTEXT_COMPLETED:
            st.trace.append(st.datacontext)
            st.datacontext = None
    elif st.event is not None:
        if process_event(tag, content, st) == StateProcess.EVENT_COMPLETED:
            st.trace.append(st.event)
            st.event = None
    elif st.datastream is not None:
        if process_datastream(tag, content, st) == StateProcess.DATASTREAM_COMPLETED:
            st.trace.append(st.datastream)
            st.datastream = None
    elif tag.startswith(xes_constants.TAG_EVENT):
        if st.debug:
            print('START_EVENT')
        st.event = IOTEvent()
    elif len(st.nested_key) > 0:
        processed = process_attribute(tag, content, st)
    elif len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        inject_attribute(st.trace.attributes, key, value)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_DATACONTEXT:
        if st.debug:
            print('START_DATACONTEXT')
        st.datacontext = DataContext()
        if len(st.nested_datacontext) != 0:
            raise NestedAttributeShouldBeEmptyError('st.nested_datacontext', st.nested_datacontext)
        st.nested_datacontext.append(st.datacontext)
    elif len(content) == 3 and content[1] == xes_iot_constants.TAG_STREAM_DATASTREAM:
        if st.debug:
            print('START_DATASTREAM')
        st.datastream = DataStream()
    elif len(content) == 3 and tag.startswith(xes_constants.TAG_LIST):
        #usual attribute list 
        key = content[1]
        new_list = list()
        inject_attribute(st.trace.attributes, key, new_list)
        if not content[2].lstrip().startswith('/>'):
            st.nested_key.append(st.trace.attributes[key])
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_TRACE):
        if st.debug:
            print('END_TRACE')
        return StateProcess.TRACE_COMPLETED
    else:
        raise UnexpectedStateError(process_trace, st)


def process_global_scope(tag, content, st):
    """
        Returns:
            GLOBAL_SCOPE_COMPLETED -> if finished processing global scope
    """
    if st.global_scope is None:
        raise AttributeShouldNotBeNoneError('st.global_scope')
    
    if tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_GLOBAL):
        return StateProcess.GLOBAL_SCOPE_COMPLETED
    elif len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        st.log.set_global_attribute(st.global_scope, key, value)
    else:
        raise UnexpectedStateError(process_global_scope, st)


def process_log(tag, content, st):
    """
        Returns:
            LOG_COMPLETED -> if finished processing log
    """
    if st.log is None:
        raise AttributeShouldNotBeNoneError('st.log')
    
    if tag.startswith(xes_constants.TAG_EXTENSION):
        st.log.set_extension(parse_extension(content))
    
    elif st.global_scope is not None:
        if process_global_scope(tag, content, st) == StateProcess.GLOBAL_SCOPE_COMPLETED:
            st.global_scope = None
    elif tag.startswith(xes_constants.TAG_GLOBAL):
        if st.global_scope is not None:
            raise AttributeShouldBeNoneError('st.global_scope')
        if content[1] not in [xes_constants.TAG_EVENT, xes_constants.TAG_TRACE]:
            raise InvalidAttributeError('global_scope', tag, content[1])
        st.global_scope = content[1]
    elif st.trace is not None:
        if process_trace(tag, content, st) == StateProcess.TRACE_COMPLETED:
            st.log.append(st.trace)
            st.trace = None
    elif st.event is not None:
        if process_event(tag, content, st) == StateProcess.EVENT_COMPLETED:
            st.log.append(st.event)
            st.event = None
    elif tag.startswith(xes_constants.TAG_TRACE):
        if st.debug:
            print('START_TRACE')
        st.trace = IOTTrace()
    elif len(content) == 5:
        key, value = read_attribute_key_value(tag, content)
        inject_attribute(st.log.attributes, key, value)
    elif tag.startswith(xes_constants.TAG_EVENT):
        if st.debug:
            print('START_EVENT')
        st.event = IOTEvent()
    elif tag[0] == '/' and tag[1:].startswith(xes_constants.TAG_LOG):
        if st.debug:
            print('END_LOG')
        return StateProcess.LOG_COMPLETED
    else:
        raise UnexpectedStateError(process_log, st)


def import_log_from_file_object(f, encoding, file_size=sys.maxsize, parameters=None):
    if parameters is None:
        parameters = {}

    st = State()
    f.seek(0)

    is_log_processed = False
    for line_count, line in enumerate(f):
        content = line.decode(encoding).split("\"")
        if len(content) == 0:
            pass

        tag = content[0].split("<")[-1]
        if st.debug:
            print(line_count + 1, ' --> ', len(content), content)
        
        if is_log_processed:
            raise UnexpectedMultipleLogError()

        if st.log is not None:
            if process_log(tag, content, st) == StateProcess.LOG_COMPLETED:
                is_log_processed = True
        elif tag.startswith(xes_constants.TAG_LOG):
            #parse log attrs here
            st.log = IOTEventLog()
            set_log_level_attributes(st.log, content)
            if st.debug:
                print('START_LOG')

    if st.log is None:
        raise AttributeShouldNotBeNoneError('st.log')

    return st.log


def set_attribute_multipoint(multipoint, key, value):
    if not key.startswith(xes_iot_constants.TAG_STREAM) or not hasattr(multipoint, key[7:]):
        raise InvalidAttributeError('multipoint', key, value)
    setattr(multipoint, key[7:], value)


def set_attribute_point(point, key, value):
    if not key.startswith(xes_iot_constants.TAG_STREAM) or not hasattr(point, key[7:]):
        raise InvalidAttributeError('point', key, value)
    setattr(point, key[7:], value)


def set_attribute_datastream(datastream, key, value):
    if not key.startswith(xes_iot_constants.TAG_STREAM) or not hasattr(datastream, key[7:]):
        raise InvalidAttributeError('datastream', key, value)
    setattr(datastream, key[7:], value)


def set_log_level_attributes(log, content):
    for i in range(0, len(content) - 1, 2):
        attr = content[i].rsplit('.', 1)[-1]
        attr = attr[:-1]
        if hasattr(log, attr):
            setattr(log, attr, content[i+1])


def parse_extension(content):
    if len(content) != 7:
        raise Exception(f'Incorrect extension {content}')
    for i in range(0, len(content) - 1, 2):
        if content[i].endswith('name='):
            name = content[i + 1]
        if content[i].endswith('prefix='):
            prefix = content[i + 1]
        if content[i].endswith('uri='):
            uri = content[i + 1]
    return XESExtension(name, prefix, uri)


def read_attribute_key_value(tag, content):
    key = content[1]
    value = None
    #allow not specified attributes for global
    if content[3] == xes_iot_constants.NOT_SPECIFIED:
        return key, content[3]

    if tag.startswith(xes_constants.TAG_STRING):
        value = content[3]
    elif tag.startswith(xes_constants.TAG_DATE):
        value = State.date_parser.apply(content[3])
    elif tag.startswith(xes_constants.TAG_INT):
        value = int(content[3])
    elif tag.startswith(xes_constants.TAG_FLOAT):
        value = float(content[3])
    elif tag.startswith(xes_constants.TAG_BOOLEAN):
        value = True if content[3] == "true" else False
    else:
        value = content[3]

    return key, value