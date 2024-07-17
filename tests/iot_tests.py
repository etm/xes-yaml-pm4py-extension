"""
    This is a collection for sensor and additional test handlers
    Every case returns:
        path -> original input path
        modified -> modified output path
"""
import os
from enum import Enum
from pathlib import Path

iot_xes_data_dir = Path(os.path.dirname(__file__)).joinpath('iot_xes_data')

sensor_dir = iot_xes_data_dir.joinpath('sensor')
additional_dir = iot_xes_data_dir.joinpath('additional')
modified_dir = iot_xes_data_dir.joinpath('modified')
SENSOR_FILES = ['04235115-af91-4f61-ac19-aba689ef6179.xes.xml', '05f8e513-3580-4b90-94e1-91811165069a.xes.xml', '06d75e4c-7fe2-4a65-bc23-a67dda530441.xes.xml', '083a25f8-f378-48ce-bc42-dc9a14536498.xes.xml', '0a7ab0ad-a8cd-47df-9625-7ea71e27ff98.xes.xml', '0c325bc4-c768-4e4a-8228-9976457ae24f.xes.xml', '0d5ca6c6-be94-4087-9143-40d96f861cc4.xes.xml', '0dc1f5ff-255e-41bc-a962-022a601496d1.xes.xml', '144074e1-1414-4442-9002-9f1417b070ee.xes.xml', '15f14fd8-4285-4c4c-aec4-7bb1b7479a5c.xes.xml', '1796a647-3372-4a56-b7e6-e080bb88e334.xes.xml', '18b27bff-18e5-47d6-a0fb-40e22c8c877b.xes.xml', '1abd45e2-62d1-455c-a30a-b76eaee77024.xes.xml', '1cac4039-57b3-4d5b-8b9f-d543882b0172.xes.xml', '1d6853ba-e879-46ba-acab-4c3422c18f0d.xes.xml', '285ce7ee-f098-47bc-8592-ef0eefa9fffc.xes.xml', '2d659f33-7359-49e3-8a10-e1d21cfa1028.xes.xml', '2de15c4d-a5d3-485f-b56d-1f66cb2935bb.xes.xml', '4027d7f3-d848-4904-b1e7-0ddfed874da4.xes.xml', '42d6f896-bfd7-46d0-9405-451c143ac3af.xes.xml', '44b5168b-3bc9-47ca-a4d8-5f178006c6c2.xes.xml', '4514ea49-8e77-47f5-9650-94a80128d2a2.xes.xml', '4b97e831-180f-438b-9986-f0ec6aa924cc.xes.xml', '4bd81fad-c6ff-461d-87a9-e35b4a98d705.xes.xml', '507ad02d-f40b-4d2d-b6da-6788005d817c.xes.xml', '5acb045b-fae7-4b25-9377-07f24184fe26.xes.xml', '5cc31326-298f-49de-8421-1830d6c5a876.xes.xml', '602ddce1-ac34-4e9a-a8a5-90bf764a92db.xes.xml', '671f74c4-1c1c-4f72-9fcf-f965e659eaae.xes.xml', '678ee86f-c3df-45df-b11f-d1108eb2ebf2.xes.xml', '6b34d92d-fb0e-4d48-a263-49992a629db8.xes.xml', '6f419fe7-7e98-4910-9df1-737cd4834eab.xes.xml', '74fa3d5a-2b77-43c2-be1c-8423154622f3.xes.xml', '7aab8ef9-ec8a-4c3c-a899-2e0a1c6ab89b.xes.xml', '7c657523-813e-41b8-acc5-f304b179cc4a.xes.xml', '7d94a20a-3b35-4a37-97ad-8c6d55f06dd5.xes.xml', '80a2726a-ab11-4988-b0cc-3efac9a9a7fb.xes.xml', '81108b7b-47d4-4013-966d-d3137df1a7a2.xes.xml', '8ae82436-b190-449b-ba7d-3a57b1f8b070.xes.xml', '8cc305ec-ed44-4d10-94bf-b01301c83c86.xes.xml', '91e67eb4-6558-4231-9e36-e5e092126f4f.xes.xml', '97993283-dbdc-47eb-bc31-acdd3658edbd.xes.xml', '9851ce02-7cdd-49e2-8921-ad5ae4f7502c.xes.xml', 'a1b59310-dfe1-408a-b42e-a418a751fc8d.xes.xml', 'a6dc87b4-fa21-4865-b43b-0f0c889a52f5.xes.xml', 'a71c89f3-096a-40d0-a8be-17f777aeeb51.xes.xml', 'a7fbc3e1-cc70-4741-a609-34e1ff657411.xes.xml', 'acc0be00-a10d-4740-bd16-701aceff6ad3.xes.xml', 'ba41ed91-9967-4492-951b-918fbb50b807.xes.xml', 'be4df304-a6bb-4b93-a839-c0d1780c35dd.xes.xml', 'bee24a5a-8d58-4b45-8a67-7f7ef6e82ad3.xes.xml', 'c4fed37d-63a7-4963-84a5-e27d7583fbfa.xes.xml', 'c519ab15-3bd9-4a99-b373-a0520c549822.xes.xml', 'c9b0bfbb-b6cd-46c2-a475-a97742e3fc00.xes.xml', 'cb8270bb-b0e8-4c3b-92f5-e2b2f975c5f9.xes.xml', 'cf999a92-8fa8-4b12-bebb-7fa5c91dd672.xes.xml', 'd10263c2-2493-448e-a13b-4e1132b1305a.xes.xml', 'd6e24a79-97f6-4bd6-824c-73acb08bac3e.xes.xml', 'd810f7e4-3e81-4674-b256-304d16088765.xes.xml', 'd835ea25-eaa1-4610-850a-25a149e64cd5.xes.xml', 'd8f7843b-a195-4ac1-a87e-c55844a79ed2.xes.xml', 'd9daf97e-13ab-4d59-b6ea-c2326a315acb.xes.xml', 'e64f7365-acc8-459f-a579-53d40f8e7142.xes.xml', 'eb5f130e-685f-4670-b07c-cb6e3ce953fd.xes.xml', 'ed1d4c66-9218-437d-99f3-3d6201c384d9.xes.xml', 'f060e3e1-db91-4092-ba70-8fe53b25d146.xes.xml', 'f576b0f6-f164-41ce-a5e9-1e65180fc79d.xes.xml', 'f94072c4-95f1-4204-b6cd-72ca2d141c1a.xes.xml', 'fa3c3782-c777-4c64-aa57-b531bb7f0f99.xes.xml', 'fca5a286-0a04-4e39-864c-27b5afb2fc05.xes.xml']

def case_additional_decorator(fname):
    def case_additional():        
        return str(additional_dir.joinpath(fname)), str(modified_dir.joinpath('modified_' + fname))
    return case_additional

def case_sensor(id):
    if not isinstance(id, int):
        raise Exception('id should be int, type(id)='.format(type(id)))
    if id < 0 or id >= len(SENSOR_FILES):
        raise Exception('id={} should be in range {} to {}'.format(id, 0, len(SENSOR_FILES)))
    fname = SENSOR_FILES[id]
    return str(sensor_dir.joinpath(fname)), str(modified_dir.joinpath('modified_' + fname))

class TestCase(Enum):
    __test__ = False
    SENSOR_DATA = case_sensor
    ALLOW_EMPTY_MULTIPOINT = case_additional_decorator('allow_empty_multipoint.xes.xml')
    GET_TRACES_WITH_DATASTREAM = case_additional_decorator('api_get_traces_with_datastream.xes.xml')
    COUNT_DATASTRAMS_AND_POINTS_IN_EVENT = case_additional_decorator('api_count_datastreams_and_points_in_event.xes.xml')
    FIND_ALL_STREAM_DATA_ENTRIES_IN_EVENT = case_additional_decorator('api_find_all_stream_data_entries_in_event.xes.xml')
    COUNT_EVENTS_WITH_DATASTREAMS_IN_TRACE = case_additional_decorator('api_count_events_with_datastreams_in_trace.xes.xml')
    MULTIPOINT = case_additional_decorator('multipoint.xes.xml')
    COUNT_POINTS_IN_MULTIPOINT_ENTRY = case_additional_decorator('api_count_points_in_multipoint_entry.xes.xml')
    ADD_SENSOR_VALUE_TO_EVENT = case_additional_decorator('api_add_sensor_value_to_event.xes.xml')
    REMOVE_SENSOR_VALUE_FROM_EVENT = case_additional_decorator('api_remove_sensor_value_from_event.xes.xml')
    SENSOR_VALUES_OF_SPECIFIC_TYPE = case_additional_decorator('api_sensor_values_of_specific_type.xes.xml')
    COUNT_DISTINCT_DATACONTEXT_GROUPS_AT_TRACE_LEVEL = case_additional_decorator('api_count_distinct_datacontext_groups_at_trace_level.xes.xml')
    DATASTREAM_IN_TRACE = case_additional_decorator('datastream_in_trace.xes.xml')
    DATACONTEXT_IN_TRACE = case_additional_decorator('datacontext_in_trace.xes.xml')
    EVENT_IN_LOG = case_additional_decorator('event_in_log.xes.xml')
    EXPORTER_CUSTOM = case_additional_decorator('exporter_custom.xes.xml')
    EXPORTER_EMPTY_LIST = case_additional_decorator('exporter_empty_list.xes.xml')
    BIG_FILE_LIMITATION = case_additional_decorator('big_file_limitation.xes.xml')
