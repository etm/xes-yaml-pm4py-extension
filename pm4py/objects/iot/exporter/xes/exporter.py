from enum import Enum
from pm4py.objects.iot.exporter.xes.variants import line_by_line

class Variants(Enum):
    LINE_BY_LINE = line_by_line


DEFAULT_VARIANT = Variants.LINE_BY_LINE

def apply(log, output_file_path, variant=DEFAULT_VARIANT, parameters=None):
    """
        Method to export a XES from an IOTEventLog
    """
    if parameters == None:
        parameters = {}

    return variant.value.apply(log, output_file_path, parameters)


def serialize(log, variant=DEFAULT_VARIANT, parameters=None):
    """
        Serialize an IOTEventLog into a binary string containing the XES of the log
        Returns string describing the XES
    """
    if parameters == None:
        parameters = {}
    
    return variant.value.export_log_as_string(log, parameters)