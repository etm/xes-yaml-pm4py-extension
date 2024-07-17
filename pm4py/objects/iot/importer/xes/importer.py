from enum import Enum

from pm4py.objects.iot.importer.xes.variants import xmlxes20
from pm4py.objects.log.importer.xes.variants import iterparse

class Variants(Enum):
    XMLXES20=xmlxes20

def apply(path, parameters=None, variant=Variants.XMLXES20):
    if parameters == None:
        parameters = {}

    log = variant.value.apply(path, parameters=parameters)

    return log
