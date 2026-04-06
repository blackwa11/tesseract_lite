object_4d_data = {}


def remove_missing_objects(objects_getter):
    stale = [name for name in object_4d_data if objects_getter(name) is None]
    for name in stale:
        object_4d_data.pop(name, None)


def clear_state():
    object_4d_data.clear()
