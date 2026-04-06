import bpy

from ..core.state import object_4d_data, remove_missing_objects
from .transformers import reset_object_to_original, transform_curve_object, transform_mesh_object


def ensure_timer_running():
    if not bpy.app.timers.is_registered(animation_update):
        bpy.app.timers.register(animation_update, persistent=True)


def animation_update():
    context = bpy.context

    if not hasattr(context.scene, "universal_4d_settings"):
        return 1.0 / 60.0

    if not object_4d_data:
        return 1.0 / 60.0

    remove_missing_objects(bpy.data.objects.get)
    if not object_4d_data:
        return 1.0 / 60.0

    if not hasattr(animation_update, "frame_counter"):
        animation_update.frame_counter = 0
    animation_update.frame_counter += 1

    current_time = animation_update.frame_counter / 60.0
    settings = context.scene.universal_4d_settings

    for obj_name in list(object_4d_data.keys()):
        obj = bpy.data.objects.get(obj_name)
        if obj is None:
            continue

        data = object_4d_data[obj_name]
        if data.get("animation_running", False):
            transform_4d_object(obj, data, settings, current_time)

    return 1.0 / 60.0


def transform_4d_object(obj, data, settings, current_time):
    speed = settings.speed
    scale = settings.scale

    angles = {
        "xy": current_time * speed * settings.rotation_xy,
        "xz": current_time * speed * settings.rotation_xz,
        "yz": current_time * speed * settings.rotation_yz,
        "xw": current_time * speed * settings.rotation_xw,
        "yw": current_time * speed * settings.rotation_yw,
        "zw": current_time * speed * settings.rotation_zw,
    }

    if data.get("type") == "CURVE":
        transform_curve_object(obj, data, angles, settings.w_depth, scale)
    else:
        transform_mesh_object(obj, data, angles, settings.w_depth, scale)


def reset_all_objects(w_depth):
    for data in object_4d_data.values():
        data["animation_running"] = False

    for obj_name in list(object_4d_data.keys()):
        obj = bpy.data.objects.get(obj_name)
        if obj is not None:
            reset_object_to_original(obj, object_4d_data[obj_name], w_depth)
