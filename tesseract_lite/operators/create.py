from bpy.props import FloatProperty
from bpy.types import Operator

from ..services.factory import create_tesseract_object


class UNIVERSAL_OT_create_tesseract(Operator):
    bl_idname = "universal.create_tesseract"
    bl_label = "Create Tesseract"
    bl_description = "Create 4D hypercube"
    bl_options = {'REGISTER', 'UNDO'}

    size: FloatProperty(name="Size", default=1.0, min=0.1, max=5.0)

    def execute(self, context):
        try:
            settings = context.scene.universal_4d_settings
            _, data_type = create_tesseract_object(
                context=context,
                size=self.size,
                object_type=settings.object_type,
                w_depth=settings.w_depth,
            )
            self.report({'INFO'}, f"Tesseract {data_type.lower()} created")
            return {'FINISHED'}
        except Exception as exc:
            self.report({'ERROR'}, f"Error: {exc}")
            return {'CANCELLED'}
