object_4d_data = {}


def clear_missing_objects(get_object):
    for obj_name in list(object_4d_data.keys()):
        if get_object(obj_name) is None:
            object_4d_data.pop(obj_name, None)


def clear_state():
    object_4d_data.clear()
