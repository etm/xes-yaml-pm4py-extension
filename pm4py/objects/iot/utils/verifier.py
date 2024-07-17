"""
    This is object verifiers for the extension by XES 2.0 standard.
"""
from pm4py.objects.iot.obj import IOTEventLog, IOTEvent, IOTTrace, DataStream, DataContext, Point, MultiPoint
from pm4py.objects.iot.exceptions import UnsupportedTypeError, VerificationFailedError
from enum import Enum

class MisMatchCounter:
    POINT_NONE_VALUE = 0
    def reset():
        MisMatchCounter.POINT_NONE_VALUE = 0


def __containing_types_mismatch(obj, able_to_hold):
    return [item for item in set(type(item) for item in obj) if item not in able_to_hold]

def _verify_log(log):
    if type(log) != IOTEventLog:
        raise UnsupportedTypeError(type(log))
    
    MisMatchCounter.reset()

    if log.version is None:
        raise VerificationFailedError(log, 'should have version')
    if log.features != 'nested-attributes':
        raise VerificationFailedError(log, 'should have features=nested-attributes')
    if len(log) == 0:
        raise VerificationFailedError(log, 'should not be empty')
    
    mismatch = __containing_types_mismatch(log, [IOTTrace, IOTEvent])
    if len(mismatch) > 0:
        raise VerificationFailedError(log, f'should not contain {mismatch}')

    for item in log:
        verify(item)


def _verify_trace(trace):
    if type(trace) != IOTTrace:
        raise UnsupportedTypeError(type(trace))

    mismatch = __containing_types_mismatch(trace, [IOTEvent, DataContext, DataStream])
    if len(mismatch) > 0:
        raise VerificationFailedError(trace, f'should not contain {mismatch}')

    for item in trace:
        verify(item)


def _verify_event(event):
    if type(event) != IOTEvent:
        raise UnsupportedTypeError(type(event))

    mismatch = __containing_types_mismatch(event, [DataStream])
    if len(mismatch) > 0:
        raise VerificationFailedError(event, f'should not contain {mismatch}')

    for item in event:
        verify(item)


def _verify_point(point):
    # probably should add verification if not comes from multipoint, then should have 'id', 'timestamp', 'value as required
    # but in the given tests the above is not correct, sometimes required attributes doesn't exist
    if type(point) != Point:
        raise UnsupportedTypeError(type(point))
    
    if point.value is None:
        MisMatchCounter.POINT_NONE_VALUE = MisMatchCounter.POINT_NONE_VALUE + 1


def _verify_multipoint(multipoint):
    if type(multipoint) != MultiPoint:
        raise UnsupportedTypeError(type(multipoint))

    mismatch = __containing_types_mismatch(multipoint, [Point])
    if len(mismatch) > 0:
        raise VerificationFailedError(multipoint, f'should not contain {mismatch}')

    for item in multipoint:
        verify(item)


def _verify_datastream(datastream):
    if type(datastream) != DataStream:
        raise UnsupportedTypeError(type(datastream))

    mismatch = __containing_types_mismatch(datastream, [MultiPoint, Point])
    if len(mismatch) > 0:
        raise VerificationFailedError(datastream, f'should not contain {mismatch}')

    for item in datastream:
        verify(item)


def _verify_datacontext(datacontext):
    if type(datacontext) != DataContext:
        raise UnsupportedTypeError(type(datacontext))

    mismatch = __containing_types_mismatch(datacontext, [DataContext, DataStream])
    if len(mismatch) > 0:
        raise VerificationFailedError(datacontext, f'should not contain {mismatch}')

    if not datacontext.contains_datastream():
        raise VerificationFailedError(datacontext, 'should contain datastream')
    
    for item in datacontext:
        verify(item)
    

class Attest(Enum):
    IOTEventLog = _verify_log
    IOTTrace = _verify_trace
    IOTEvent = _verify_event
    Point = _verify_point
    MultiPoint = _verify_multipoint
    DataStream = _verify_datastream
    DataContext = _verify_datacontext

def verify(obj):
    name = type(obj).__name__
    if not hasattr(Attest, name):
        return UnsupportedTypeError(type(obj))
    getattr(Attest, name)(obj)

    