import datetime
import pm4py
from pm4py.objects.iot import apis
from pm4py.objects.iot.importer.xes.variants.xmlxes20 import State

#import XES
filename = '507ad02d-f40b-4d2d-b6da-6788005d817c.xes.xml'
log = pm4py.read.read_iot_xes(filename)


x = datetime.datetime(2023, 7, 15)

#create a Point
point = pm4py.objects.iot.obj.Point(
  id = 'point1_id',
  #timestamp = State.date_parser.apply('2023-04-28T17:38:20.0747454+02:00'),
  timestamp = x,
  value = 'point1_val',
  source = 'point1_source',
  meta = [{'type':'System.String1'}]
)
#create a Point
point2 = pm4py.objects.iot.obj.Point(
  id = 'point1_id',
  #timestamp = State.date_parser.apply('2023-04-28T17:38:20.0747454+02:00'),
  timestamp = x,
  value = 'point2_val',
  source = 'point1_source',
  meta = [{'type':'System.String1'}]
)
#create a Point
point3 = pm4py.objects.iot.obj.Point(
  id = 'point1_id',
  #timestamp = State.date_parser.apply('2023-04-28T17:38:20.0747454+02:00'),
  timestamp = x,
  value = 'point3_val',
  source = 'point1_source',
  meta = [{'type':'System.String1'}]
)

ds1 = pm4py.objects.iot.obj.DataStream(
  name="a",
  id="b",
  source = "c"
)
ds2 = pm4py.objects.iot.obj.DataStream(
  name="x",
  id="y",
  source = "z"
)

log[0][0].append(ds1)
log[0][0].append(ds2)



print(log[0][0])
apis.add_sensor_value_to_event(log[0][0], point2)
log[0][0][1].add_sensor_value(point)
log[0][0][1].add_sensor_value(point3)
apis.add_sensor_value_to_event(log[0][0][0], point)
print(log[0][0])

fset1 = pm4py.objects.iot.obj.FilterSet(source="point1_source")
output = apis.sensor_values_of_specific_type(log[0][0], fset1)
print(fset1)
print(output)

print(apis.count_datastreams_and_points_in_event(log[0][0]))
print(apis.find_all_stream_data_entries_in_event(log[0][0]))
print(apis.count_events_with_datastreams_in_trace(log[0]))



print(apis.count_datastreams_and_points_in_event(log[0][11]))
print(apis.find_all_stream_data_entries_in_event(log[0][11]))

fset1 = pm4py.objects.iot.obj.FilterSet(id="MaxxTurn45/Power/Active/C")
print(apis.sensor_values_of_specific_type(log[0][11], fset1))
