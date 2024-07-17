import importlib.util

from enum import Enum
from io import BytesIO
from pm4py.util import exec_utils, constants
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.iot.utils import verifier
from pm4py.objects.iot.exceptions import UnsupportedTypeError
from pm4py.objects.iot import constants as xes_iot_constants
from pm4py.objects.iot.obj import IOTEventLog, IOTEvent, IOTTrace, DataStream, DataContext, Point, MultiPoint
from xml.sax.saxutils import quoteattr

class Parameters(Enum):
    SHOW_PROGRESS_BAR = "show_progress_bar"
    APPLY_VERIFIER = "apply_verifier"
    ENCODING = "encoding"

def export_nested_attribute_lines(attr_name, attr_value, indent=0):
    if attr_name is None:
        return []

    ret = []
    attr_type = Exporter.get_xes_attr_type(attr_name, type(attr_value).__name__)
    if not attr_type == xes_util.TAG_LIST:
        attr_value = xes_iot_constants.NOT_SPECIFIED if attr_value is None else Exporter.get_xes_attr_value(attr_value, attr_type)
        ret.append(Exporter.get_tab_indent(indent) + f'<{attr_type} key={Exporter.escape(attr_name)} value={Exporter.escape(attr_value)} />')
    else:
        # process nested list attr
        if len(attr_value) == 0:
            # process empty list in one line
            ret.append(Exporter.get_tab_indent(indent) + f'<list key={Exporter.escape(attr_name)} />')
        else:
            ret.append(Exporter.get_tab_indent(indent) + f'<list key={Exporter.escape(attr_name)}>')
            for item_dict in attr_value:
                for subbattr_name, subattr_value in item_dict.items():
                    ret.extend(export_nested_attribute_lines(subbattr_name, subattr_value, indent + 1))
            ret.append(Exporter.get_tab_indent(indent) + f'</list>')
    return ret


def _export_log(wrt, log):
    if type(log) != IOTEventLog:
        raise UnsupportedTypeError(type(log))
    wrt.write(f'<log {xes_util.TAG_VERSION}="{log.version}" {xes_util.TAG_FEATURES}="{log.features}" {xes_util.TAG_XMLNS}="{xes_util.VALUE_XMLNS}">')
    wrt.tab_inc()

    for ext in log.extensions.values():
        wrt.write(f'<extension name="{ext.name}" prefix="{ext.prefix}" uri="{ext.uri}" />')
    
    for class_name, class_val in log.classifiers.items():
        wrt.write(f'<classifier name="{class_name}" keys="{" ".join(class_val)}" />')

    for attr_name, attr_val in log.attributes.items():
        wrt.write_lines(export_nested_attribute_lines(attr_name, attr_val))

    for scope in log.omni_present:
        wrt.write(f'<global scope="{scope}">')
        for attr_name, attr_val in log.omni_present[scope].items():
            wrt.write_lines(export_nested_attribute_lines(attr_name, attr_val, 1))
        wrt.write(f'</global>')

    for item in log:
        wrt.apply(item)
        if Exporter.progress is not None:
            Exporter.progress.update()
    wrt.tab_decr()
    wrt.write("</log>")


def _export_trace(wrt, trace):
    if type(trace) != IOTTrace:
        raise UnsupportedTypeError(type(trace))

    wrt.write(f'<trace>')
    wrt.tab_inc()
    for attr_name, attr_val in trace.attributes.items():
        wrt.write_lines(export_nested_attribute_lines(attr_name, attr_val))

    for item in trace:
        wrt.apply(item)

    wrt.tab_decr()
    wrt.write(f'</trace>')


def _export_event(wrt, event):
    if type(event) != IOTEvent:
        raise UnsupportedTypeError(type(event))

    wrt.write(f'<event>')
    wrt.tab_inc()

    for attr_name, attr_val in event.attributes.items():
        wrt.write_lines(export_nested_attribute_lines(attr_name, attr_val))

    for item in event:
        wrt.apply(item)

    wrt.tab_decr()
    wrt.write(f'</event>')


def _export_point(wrt, point):
    if type(point) != Point:
        raise UnsupportedTypeError(type(point))
    wrt.write(f'<list key={Exporter.escape(xes_iot_constants.TAG_STREAM_POINT)}>')
    wrt.tab_inc()

    if point.id is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_ID, point.id))
    if point.timestamp is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_TIMESTAMP, point.timestamp))
    if point.value is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_VALUE, point.value))
    if point.source is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_SOURCE, point.source))
    if point.meta is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_META, point.meta))

    wrt.tab_decr()
    wrt.write(f'</list>')


def _export_multipoint(wrt, multipoint):
    if type(multipoint) != MultiPoint:
        raise UnsupportedTypeError(type(multipoint))

    wrt.write(f'<list key={Exporter.escape(xes_iot_constants.TAG_STREAM_MULTIPOINT)}>')
    wrt.tab_inc()
    if multipoint.id is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_ID, multipoint.id))
    if multipoint.timestamp is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_TIMESTAMP, multipoint.timestamp))
    if multipoint.source is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_SOURCE, multipoint.source))
    if multipoint.meta is not None:
        wrt.write_lines(export_nested_attribute_lines(xes_iot_constants.TAG_STREAM_META, multipoint.meta))

    for item in multipoint:
        wrt.apply(item)

    wrt.tab_decr()
    wrt.write(f'</list>')


def _export_datastream(wrt, datastream):
    if type(datastream) != DataStream:
        raise UnsupportedTypeError(type(datastream))

    if datastream.stream_data_key is not None:
        wrt.write(f'<string key={Exporter.escape(datastream.stream_data_key)} value={Exporter.escape(xes_iot_constants.STREAM_DATA)} />')

    wrt.write(f'<list key={Exporter.escape(xes_iot_constants.TAG_STREAM_DATASTREAM)}>')
    wrt.tab_inc()

    if datastream.name is not None:
        wrt.write(f'<string key={Exporter.escape(xes_iot_constants.TAG_STREAM_NAME)} value={Exporter.escape(datastream.name)} />')
    if datastream.id is not None:
        wrt.write(f'<string key={Exporter.escape(xes_iot_constants.TAG_STREAM_ID)} value={Exporter.escape(datastream.id)} />')
    if datastream.source is not None:
        wrt.write(f'<string key={Exporter.escape(xes_iot_constants.TAG_STREAM_SOURCE)} value={Exporter.escape(datastream.source)} />')

    for item in datastream:
        wrt.apply(item)

    wrt.tab_decr()
    wrt.write(f'</list>')

def _export_datacontext(wrt, datacontext):
    if type(datacontext) != DataContext:
        raise UnsupportedTypeError(type(datacontext))
    wrt.write(f'<list key={Exporter.escape(xes_iot_constants.TAG_STREAM_DATACONTEXT)}>')
    wrt.tab_inc()

    for item in datacontext:
        wrt.apply(item)

    wrt.tab_decr()
    wrt.write(f'</list>')


class Exporter:
    IOTEventLog = _export_log
    IOTTrace = _export_trace
    IOTEvent = _export_event
    Point = _export_point
    MultiPoint = _export_multipoint
    DataStream = _export_datastream
    DataContext = _export_datacontext
    progress = None

    # defines correspondence between Python types and XES types
    TYPE_CORRESPONDENCE = {
        "str": xes_util.TAG_STRING,
        "int": xes_util.TAG_INT,
        "float": xes_util.TAG_FLOAT,
        "list": xes_util.TAG_LIST,
        "datetime": xes_util.TAG_DATE,
        "Timestamp": xes_util.TAG_DATE,
        "bool": xes_util.TAG_BOOLEAN,
        "dict": xes_util.TAG_LIST,
        "numpy.int64": xes_util.TAG_INT,
        "numpy.float64": xes_util.TAG_FLOAT,
        "numpy.datetime64": xes_util.TAG_DATE
    }

    # if a type is not found in the previous list, then default to string
    DEFAULT_TYPE = xes_util.TAG_STRING

    def get_tab_indent(n):
        return "".join(["\t"] * n)

    def escape(stru):
        return '"' + stru + '"'

    def get_xes_attr_type(attr_name, attr_type):
        if attr_name == xes_util.DEFAULT_NAME_KEY:
            return xes_util.TAG_STRING
        elif attr_type in Exporter.TYPE_CORRESPONDENCE:
            attr_type_xes = Exporter.TYPE_CORRESPONDENCE[attr_type]
        else:
            attr_type_xes = Exporter.DEFAULT_TYPE
        return attr_type_xes

    def get_xes_attr_value(attr_value, attr_type_xes):
        if attr_type_xes == xes_util.TAG_DATE:
            return attr_value.isoformat()
        elif attr_type_xes == xes_util.TAG_BOOLEAN:
            return str(attr_value).lower()
        return str(attr_value)


class Writer:
    def __init__(self, fp_obj, encoding):
        self._fp_obj = fp_obj
        self._encoding = encoding
        self._indent = 0

    @property
    def indent(self):
        return self._indent
    
    @indent.setter
    def indent(self, indent):
        self._indent = indent

    @property
    def encoding(self):
        return self._encoding
    
    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    @property
    def fp_obj(self):
        return self._fp_obj
    
    @fp_obj.setter
    def fp_obj(self, fp_obj):
        self._fp_obj = fp_obj

    def tab_inc(self):
        self.indent = self.indent + 1

    def tab_decr(self):
        self.indent = self.indent - 1
        if self.indent < 0:
            raise Exception('can not have negative indent')

    def apply(self, obj):
        name = type(obj).__name__
        if not hasattr(Exporter, name):
            return UnsupportedTypeError(type(obj))
        getattr(Exporter, name)(self, obj)

    def write_lines(self, data_entries):
        for data in data_entries:
            self.write(data)

    def write(self, data):
        if not self.encoding:
            raise Exception('should have encoding')
        data = Exporter.get_tab_indent(self.indent) + data + '\n'
        self.fp_obj.write(data.encode(self.encoding))


def apply(log, filename, parameters=None):
    """
        Supports globals, nested attributes, extensions and IOTEventLog containing attributes.
        Please note:
        1) Original ordering of attributes could be different, streaming events ordering stays the same
        2) All event nested attributes have <list>..</list>
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)
    
    apply_verifier = exec_utils.get_param_value(Parameters.APPLY_VERIFIER, parameters, xes_iot_constants.DEFAULT_VERIFIER)
    if apply_verifier:
        verifier.verify(log)

    file = open(filename, "wb")
    export_log_line_by_line(log, file, encoding, parameters=parameters)
    file.close()


def export_log_line_by_line(log, fp_obj, encoding, parameters=None):
    """
    Exports the contents of the log line-by-line to a file object
    """
    if parameters is None:
        parameters = {}

    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR)
    Exporter.progress = None
    if importlib.util.find_spec("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        Exporter.progress = tqdm(total=len(log), desc="exporting log, completed :: ")

    wrt = Writer(fp_obj, encoding)
    wrt.write(f'<?xml version="1.0" encoding="{encoding}"?>' )
    wrt.apply(log)

    # gracefully close progress bar
    if Exporter.progress is not None:
        Exporter.progress.close()
    del Exporter.progress

    if wrt.indent != 0:
        raise Exception('indent should be 0')
    

def export_log_as_string(log, parameters=None):
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)    
    apply_verifier = exec_utils.get_param_value(Parameters.APPLY_VERIFIER, parameters, xes_iot_constants.DEFAULT_VERIFIER)

    if apply_verifier:
        verifier.verify(log)

    b = BytesIO()
    export_log_line_by_line(log, b, encoding, parameters=parameters)

    return b.getvalue()
