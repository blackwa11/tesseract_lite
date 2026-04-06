import bpy

from ..core.state import object_4d_data, clear_missing_objects
from .transformers import transform_object


def ensure_timer_running():
    if not bpy.app.timers.is_registered(animation_update):
        bpy.app.timers.register(animation_update, persistent=True)


def animation_update():
    context = bpy.context

    if not hasattr(context.scene, "universal_4d_settings"):
        return 1.0 / 60.0

    if not object_4d_data:
        return 1.0 / 60.0

    clear_missing_objects(bpy.data.objects.get)
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
            object_4d_data.pop(obj_name, None)
            continue

        data = object_4d_data[obj_name]
        if data.get("animation_running", False):
            try:
                transform_object(obj, data, settings, current_time)
            except Exception as exc:
                print(f"Error transforming {obj.name}: {exc}")

    return 1.0 / 60.0
