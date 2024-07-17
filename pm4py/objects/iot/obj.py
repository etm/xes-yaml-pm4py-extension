import copy
from enum import Enum
from collections.abc import Sequence
from pm4py.objects.log.obj import EventLog, Trace

class IOTEventLog(EventLog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._version = kwargs['version'] if 'version' in kwargs else None
        self._features = kwargs['features'] if 'features' in kwargs else None

    def set_extension(self, ext):
        self.extensions[ext.name] = ext

    def set_global_attribute(self, scope, key, value):
        if scope not in self.omni_present:
            self.omni_present[scope] = {}
        self.omni_present[scope][key] = value

    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, version):
        self._version = version

    @property
    def features(self):
        return self._features
    
    @features.setter
    def features(self, features):
        self._features = features

    def __repr__(self):
        ret = []
        for i in range(len(self._list)):
            ret.append(self._list[i])
        return str(ret)

    def __str__(self):
        return str(self.__repr__())

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        elif self.attributes != other.attributes:
            return False
        elif self.extensions != other.extensions:
            return False
        elif self.omni_present != other.omni_present:
            return False
        elif self.classifiers != other.classifiers:
            return False
        else:
            for i in range(len(self._list)):
                if self[i] != other[i]:
                    return False
        return True
    
    def __copy__(self):
        log = IOTEventLog()
        log._features = copy.copy(self._features)
        log._version = copy.copy(self._version)
        log._attributes = copy.copy(self._attributes)
        log._extensions = copy.copy(self._extensions)
        log._omni = copy.copy(self._omni)
        log._classifiers = copy.copy(self._classifiers)
        log._properties = copy.copy(self._properties)
        for trace in self._list:
            log._list.append(trace)
        return log

    def __deepcopy__(self, memodict={}):
        log = IOTEventLog()
        log._features = copy.deepcopy(self._features)
        log._version = copy.deepcopy(self._version)
        log._attributes = copy.deepcopy(self._attributes)
        log._extensions = copy.deepcopy(self._extensions)
        log._omni = copy.deepcopy(self._omni)
        log._classifiers = copy.deepcopy(self._classifiers)
        log._properties = copy.deepcopy(self._properties)
        for trace in self._list:
            log._list.append(copy.deepcopy(trace))
        return log


class IOTTrace(Trace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        elif self.attributes != other.attributes:
            return False
        else:
            for i in range(len(self._list)):
                if self[i] != other[i]:
                    return False
        return True

    def __repr__(self, ret_list=False):
        ret = {"attributes": self.attributes, "datastreams": [], "events":[], "datacontexts": []}
        for i in range(len(self._list)):
            if isinstance(self._list[i], IOTEvent) and type(self._list[i]) == IOTEvent:
                ret["events"].append(self._list[i])
            elif isinstance(self._list[i], DataStream) and type(self._list[i]) == DataStream:
                ret["datastreams"].append(self._list[i])
            elif isinstance(self._list[i], DataContext) and type(self._list[i]) == DataContext:
                ret["datacontexts"].append(self._list[i])
            else:
                raise Exception('Invalid type = {}'.format(type(self._list[i])))
        return str(ret)

    def __str__(self):
        return str(self.__repr__())

    def __copy__(self):
        new_attributes = {}
        for k, v in self.attributes.items():
            new_attributes[k] = v
        trace = IOTTrace(attributes=new_attributes)
        for item in self._list:
            trace.append(item)
        return trace

    def __deepcopy__(self, memodict={}):
        new_attributes = {}
        for k, v in self.attributes.items():
            if type(new_attributes) is dict:
                new_attributes[k] = copy.deepcopy(v)
            else:
                new_attributes[k] = v
        trace = IOTTrace(attributes=new_attributes)
        for item in self._list:
            trace.append(copy.deepcopy(item))
        return trace

    def contains_datastream(self):
        for i in range(len(self._list)):
            if isinstance(self._list[i], DataStream) and type(self._list[i]) == DataStream:
                return True
        return False
    
    def count_distinct_datacontext_groups(self):
        groups_count = 0
        for item in self._list:
            if isinstance(item, DataContext) and type(item) == DataContext:
                groups_count += item.count_distinct_groups()
        return groups_count

class IOTEvent(Sequence):
    def __init__(self, *args, **kwargs):
        self._attributes = kwargs['attributes'] if 'attributes' in kwargs else {}
        self._list = list(*args)    

    @property
    def attributes(self):
        return self._attributes
    
    @attributes.setter
    def attributes(self, attributes):
        self._attributes = attributes

    def __len__(self):
        return len(self._list)
    
    def __eq__(self, other):
        if self.attributes != other.attributes or len(self._list) != len(other._list):
            return False
        for i in range(len(self._list)):
            if self._list[i] != other._list[i]:
                return False
        return True

    def __getitem__(self, key):
        return self._list[key]
    
    def __setitem__(self, key, value):
        self._list[key] = value

    def __iter__(self):
        return iter(self._list)

    def __repr__(self):
        ret = {"attributes": self._attributes, "datastreams": []}
        for i in range(len(self._list)):
            ret["datastreams"].append(self._list[i])

        return str(ret)

    def __str__(self):
        return str(self.__repr__())
    
    def __copy__(self):
        new_attributes = {}
        for k, v in self.attributes.items():
            new_attributes[k] = v
        event = IOTEvent(attributes=new_attributes)
        for item in self._list:
            event.append(item)
        return event
    
    def __deepcopy__(self, memodict={}):
        new_attributes = {}
        for k, v in self.attributes.items():
            if type(new_attributes) is dict:
                new_attributes[k] = copy.deepcopy(v)
            else:
                new_attributes[k] = v
        event = IOTEvent(attributes=new_attributes)
        for item in self._list:
            event.append(copy.deepcopy(item))
        return event

    def index(self, x, start: int = ..., end: int = ...):
        return self._list.index(x, start, end)

    def count(self, x):
        return self._list.count(x)

    def insert(self, i, x):
        self._list.insert(i, x)

    def append(self, x):
        self._list.append(x)

    def contains_datastream(self):
        return len(self) > 0

    def add_sensor_value(self, point):
        for item in self._list:
            item.add_sensor_value(point)

    def remove_sensor_value(self, point):
        for item in self._list:
            item.remove_sensor_value(point)

    def fetch_sensor_values(self, fset):
        ret_values = []
        for item in self._list:
            ret_values.extend(item.fetch_sensor_values(fset))

        return sorted(set(ret_values))

class Point:
    def __init__(self, *args, **kwargs):
        self._id = kwargs['id'] if 'id' in kwargs else None
        self._timestamp = kwargs['timestamp'] if 'timestamp' in kwargs else None
        self._value = kwargs['value'] if 'value' in kwargs else None
        self._source = kwargs['source'] if 'source' in kwargs else None
        self._meta = kwargs['meta'] if 'meta' in kwargs else None

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id
    
    @property
    def timestamp(self):
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
    
    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, source):
        self._source = source
    
    @property
    def meta(self):
        return self._meta
    
    @meta.setter
    def meta(self, meta):
        self._meta = meta

    def __repr__(self):
        ret = {}
        if self.id is not None:
            ret["id"] = self.id
        if self.timestamp is not None:
            ret["timestamp"] = str(self.timestamp)
        if self.value is not None:
            ret["value"] = self.value
        if self.source is not None:
            ret["source"] = self.source
        if self.meta is not None:
            ret["meta"] = self.meta
        return str(ret)

    def __str__(self):
        return str(self.__repr__())
    
    def __eq__(self, other):
        if self.id != other.id or self.timestamp != other.timestamp or self.value != other.value or self.source != other.source:
            return False
        if (self.meta is not None) != (other.meta is not None):
            return False
        if self.meta is None:
            return True
        if len(self.meta) != len(other.meta):
            return False
        for i in range(len(self.meta)):
            if self.meta[i] != other.meta[i]:
                return False
        return True

    def __copy__(self):
        point = Point()
        point._id = copy.copy(self._id)
        point._timestamp = copy.copy(self._timestamp)
        point._value = copy.copy(self._value)
        point._source = copy.copy(self._source)
        point._meta = copy.copy(self._meta)
        return point

    def __deepcopy__(self, memodict={}):
        point = Point()
        point._id = copy.deepcopy(self._id)
        point._timestamp = copy.deepcopy(self._timestamp)
        point._value = copy.deepcopy(self._value)
        point._source = copy.deepcopy(self._source)
        point._meta = copy.deepcopy(self._meta)
        return point

class DataStream(Sequence):
    def __init__(self, *args, **kwargs):
        self._name = kwargs['name'] if 'name' in kwargs else None
        self._id = kwargs['id'] if 'id' in kwargs else None
        self._source = kwargs['source'] if 'source' in kwargs else None
        self._list = list()
        self._stream_data_key = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id
    
    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, source):
        self._source = source

    @property
    def stream_data_key(self):
        return self._stream_data_key
    
    @stream_data_key.setter
    def stream_data_key(self, key):
        self._stream_data_key = key

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        if self.name != other.name or self.id != other.id or self.source != other.source or self.stream_data_key != other.stream_data_key:
            return False
        
        for i in range(len(self._list)):
            if self[i] != other[i]:
                return False
        return True

    def __setitem__(self, key, value):
        self._list[key] = value

    def __getitem__(self, key):
        return self._list[key]

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)
    
    def __repr__(self):
        ret = {
            "points": [],
            "multipoints": [],
        }
        if self.id is not None: 
            ret["id"] = self.id
        if self.name is not None: 
            ret["name"] = self.name
        if self.source is not None: 
            ret["source"] = self.source
        if self.stream_data_key is not None:
            ret["stream_data_key"] = self.stream_data_key
        for i in range(len(self._list)):
            if isinstance(self._list[i], Point) and type(self._list[i]) == Point:
                ret["points"].append(self._list[i])
            elif isinstance(self._list[i], MultiPoint) and type(self._list[i]) == MultiPoint:
                ret["multipoints"].append(self._list[i])
            else:
                raise Exception('Invalid type = {}'.format(type(self._list[i])))
            
        return str(ret)

    def __str__(self):
        return str(self.__repr__())
    
    def __copy__(self):
        datastream = DataStream()
        datastream._name = copy.copy(self._name)
        datastream._id = copy.copy(self._id)
        datastream._source = copy.copy(self._source)
        datastream._stream_data_key = copy.copy(self._stream_data_key)
        for item in self._list:
            datastream.append(item)
        return datastream

    def __deepcopy__(self, memodict={}):
        datastream = DataStream()
        datastream._name = copy.deepcopy(self._name)
        datastream._id = copy.deepcopy(self._id)
        datastream._source = copy.deepcopy(self._source)
        datastream._stream_data_key = copy.deepcopy(self._stream_data_key)
        for item in self._list:
            datastream.append(copy.deepcopy(item))
        return datastream

    def is_stream_data(self):
        return self.stream_data_key != None

    def count_points(self):
        return len(self)

    def index(self, x, start: int = ..., end: int = ...):
        return self._list.index(x, start, end)

    def count(self, x):
        return self._list.count(x)

    def remove(self, key):
        del self._list[key]

    def insert(self, i, x):
        self._list.insert(i, x)

    def append(self, x):
        self._list.append(x)

    def add_sensor_value(self, point):
        matched_key = None
        point_exists = False
        for i in range(len(self._list)):
            if isinstance(self._list[i], Point) and type(self._list[i]) == Point and point == self._list[i]:
                point_exists = True
                break
            elif isinstance(self._list[i], MultiPoint) and type(self._list[i]) == MultiPoint and self._list[i].matches(point):
                matched_key = i
                if self._list[i].contains(point):
                    point_exists = True
                    break
        if not point_exists:
            if matched_key is None:
                self.append(point)
            else:
                self._list[matched_key].add_sensor_value(point)

    def remove_sensor_value(self, point):
        to_remove = []
        for i in range(len(self._list)):
            if type(self._list[i]) == Point and point == self._list[i]:
                to_remove.append(i)
            elif type(self._list[i]) == MultiPoint and self._list[i].matches(point):
                self._list[i].remove_sensor_value(point)
        self._list = [item for id, item in enumerate(self._list) if id not in to_remove]

    def fetch_sensor_values(self, fset):
        ret_values = []
        for item in self._list:
            if not fset.matches(item):
                continue
            if isinstance(item, Point) and type(item) == Point:
                ret_values.append(item.value)
            elif isinstance(item, MultiPoint) and type(item) == MultiPoint:
                ret_values.extend(item.fetch_sensor_values(fset))
        return sorted(set(ret_values))


class DataContext(Sequence):
    def __init__(self):
        self._list = list()

    def __setitem__(self, key, value):
        self._list[key] = value

    def __getitem__(self, key):
        return self._list[key]

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in range(len(self._list)):
            if self[i] != other[i]:
                return False
        return True

    def __repr__(self):
        ret = {}
        ret["datacontexts"] = []
        ret["datastreams"] = []
        for i in range(len(self._list)):
            if isinstance(self[i], DataStream) and type(self[i]) == DataStream:
                ret["datastreams"].append(self[i])
            else:
                ret["datacontexts"].append(self[i])
        return str(ret)

    def __str__(self):
        return str(self.__repr__())

    def __copy__(self):
        datacontext = DataContext()
        for item in self._list:
            datacontext.append(item)
        return datacontext

    def __deepcopy__(self, memodict={}):
        datacontext = DataContext()
        for item in self._list:
            datacontext.append(copy.deepcopy(item))
        return datacontext

    def index(self, x, start: int = ..., end: int = ...):
        return self._list.index(x, start, end)

    def count(self, x):
        return self._list.count(x)

    def insert(self, i, x):
        self._list.insert(i, x)

    def append(self, x):
        self._list.append(x)

    def count_distinct_groups(self):
        groups_count = 0
        for item in self._list:
            if isinstance(item, DataStream) and type(item) == DataStream:
                groups_count += 1
            elif isinstance(item, DataContext) and type(item) == DataContext:
                groups_count += item.count_distinct_groups()
        return groups_count

    def contains_datastream(self):
        for i in range(len(self._list)):
            if isinstance(self._list[i], DataStream) and type(self._list[i]) == DataStream:
                return True
        return False


class MultiPoint(Sequence):
    def __init__(self, *args, **kwargs):
        self._id = kwargs['id'] if 'id' in kwargs else None
        self._timestamp = kwargs['timestamp'] if 'timestamp' in kwargs else None
        self._source = kwargs['source'] if 'source' in kwargs else None
        self._meta = kwargs['meta'] if 'meta' in kwargs else None
        self._list = list()

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, id):
        self._id = id
    
    @property
    def timestamp(self):
        return self._timestamp
    
    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp
    
    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, source):
        self._source = source
    
    @property
    def meta(self):
        return self._meta
    
    @meta.setter
    def meta(self, meta):
        self._meta = meta

    def __setitem__(self, key, value):
        self._list[key] = value

    def __getitem__(self, key):
        return self._list[key]

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def __repr__(self):
        ret = {
            "points": []
        }
        if self.id is not None:
            ret["id"] = self.id
        if self.timestamp is not None:
            ret["timestamp"] = str(self.timestamp)
        if self.source is not None:
            ret["source"] = self.source
        if self.meta is not None:
            ret["meta"] = self.meta

        for i in range(len(self._list)):
            ret["points"].append(self._list[i])

        return str(ret)

    def __str__(self):
        return str(self.__repr__())

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        if self.id != other.id or self.timestamp != other.timestamp or self.source != other.source:
            return False
        for i in range(len(self._list)):
            if self[i] != other[i]:
                return False
        if (self.meta is not None) != (other.meta is not None):
            return False
        if self.meta is None:
            return True

        if len(self.meta) != len(other.meta):
            return False
        for i in range(len(self.meta)):
            if self.meta[i] != other.meta[i]:
                return False
        return True

    def __copy__(self):
        multipoint = MultiPoint()
        multipoint._id = copy.copy(self._id)
        multipoint._timestamp = copy.copy(self._timestamp)
        multipoint._source = copy.copy(self._source)
        multipoint._meta = copy.copy(self._meta)

        for item in self._list:
            multipoint.append(item)

        return multipoint

    def __deepcopy__(self, memodict={}):
        multipoint = MultiPoint()
        multipoint._id = copy.deepcopy(self._id)
        multipoint._timestamp = copy.deepcopy(self._timestamp)
        multipoint._source = copy.deepcopy(self._source)
        multipoint._meta = copy.deepcopy(self._meta)

        for item in self._list:
            multipoint.append(copy.deepcopy(item))

        return multipoint

    def count_points(self):
        return len(self)

    def index(self, x, start: int = ..., end: int = ...):
        return self._list.index(x, start, end)

    def count(self, x):
        return self._list.count(x)

    def insert(self, i, x):
        self._list.insert(i, x)

    def append(self, x):
        self._list.append(x)

    def matches(self, point):
        if (self.id is not None) and self.id != point.id:
            return False
        if (self.timestamp is not None) and self.timestamp != point.timestamp:
            return False
        if (self.source is not None) and self.source != point.meta:
            return False
        if (self.meta is not None):
            if point.meta is None:
                return False
            if len(self.meta) != len(point.meta):
                return False
            for i in range(len(self.meta)):
                if self.meta[i] != point.meta[i]:
                    return False
        return True

    def complete(self, key):
        point = Point()
        point.id = self.id if self.id is not None else self._list[key].id
        point.timestamp = self.timestamp if self.timestamp is not None else self._list[key].timestamp
        point.source = self.source if self.source is not None else self._list[key].source
        point.meta = self.meta if self.meta is not None else self._list[key].meta
        point.value = self._list[key].value
        return point

    def fetch_keys(self, point):
        ret = []
        if not self.matches(point):
            return ret
        for key in range(len(self._list)):
            if self.complete(key) == point:
                ret.append(key)
        return ret

    def contains(self, point):
        if not self.matches(point):
            return False
        return len(self.fetch_keys(point)) > 0
    
    def add_sensor_value(self, point):
        if not self.matches(point):
            return
        new_point = copy.copy(point)
        if self.id is not None:
            new_point.id = None
        if self.timestamp is not None:
            new_point.timestamp = None
        if self.source is not None:
            new_point.source = None
        if self.meta is not None:
            new_point.meta = None
        self.append(new_point)

    def remove_sensor_value(self, point):
        to_remove = self.fetch_keys(point)
        self._list = [item for id, item in enumerate(self._list) if id not in to_remove]

    def fetch_sensor_values(self, fset):
        if not fset.matches_multipoint(self):
            return []

        ret_values = []

        for key in range(len(self._list)):
            if fset.matches_point(self.complete(key)):
                ret_values.append(self._list[key].value)
            
        return sorted(set(ret_values))

class FilterSet(Point):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def matches(self, point):
        if isinstance(point, Point) and type(point) == Point:
            return self.matches_point(point)
        elif isinstance(point, MultiPoint) and type(point) == MultiPoint:
            return self.matches_multipoint(point)
        else:
            raise Exception(f'Unsupported type={type(point)}')
        
    def matches_point(self, point):
        if (self.id is not None) and self.id != point.id:
            return False
        if (self.timestamp is not None) and self.timestamp != point.timestamp:
            return False
        if (self.source is not None) and self.source != point.source:
            return False
        if (self.value is not None) and self.value != point.value:
            return False
        if (self.meta is not None):
            if point.meta is None:
                return False
            if len(self.meta) != len(point.meta):
                return False
            for i in range(len(self.meta)):
                if self.meta[i] != point.meta[i]:
                    return False
        return True

    def matches_multipoint(self, multipoint):
        if (self.id is not None) and (multipoint.id is not None) and self.id != multipoint.id:
            return False
        if (self.timestamp is not None) and (multipoint.timestamp is not None) and self.timestamp != multipoint.timestamp:
            return False
        if (self.source is not None) and (multipoint.source is not None) and self.source != multipoint.source:
            return False
        if (self.value is not None) and (multipoint.value is not None) and self.value != multipoint.value:
            return False
        if (self.meta is not None) and (multipoint.meta is not None):
            if len(self.meta) != len(multipoint.meta):
                return False
            for i in range(len(self.meta)):
                if self.meta[i] != multipoint.meta[i]:
                    return False
        return True
    