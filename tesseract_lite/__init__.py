bl_info = {
    "name": "tesseract_lite",
    "author": "blackwa11 / Blackwall",
    "version": (1, 1, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > 4D Transform",
    "description": "Lite Blender addon for real-time tesseract projection and 4D rotation",
    "category": "Object",
}

import bpy
from bpy.props import PointerProperty

from .properties import UNIVERSAL_PG_4d_settings
from .operators.create import UNIVERSAL_OT_create_tesseract
from .operators.playback import (
    UNIVERSAL_OT_reset_all,
    UNIVERSAL_OT_start_all,
    UNIVERSAL_OT_stop_all,
)
from .services.animation import animation_update
from .ui.panel import UNIVERSAL_PT_4d_panel
from .core.state import clear_state

CLASSES = (
    UNIVERSAL_PG_4d_settings,
    UNIVERSAL_OT_create_tesseract,
    UNIVERSAL_OT_start_all,
    UNIVERSAL_OT_stop_all,
    UNIVERSAL_OT_reset_all,
    UNIVERSAL_PT_4d_panel,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.universal_4d_settings = PointerProperty(type=UNIVERSAL_PG_4d_settings)


def unregister():
    if bpy.app.timers.is_registered(animation_update):
        try:
            bpy.app.timers.unregister(animation_update)
        except Exception:
            pass

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)

    try:
        del bpy.types.Scene.universal_4d_settings
    except Exception:
        pass

    clear_state()


if __name__ == "__main__":
    register()
