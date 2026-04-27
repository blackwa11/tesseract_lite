bl_info = {
    "name": "tesseract_lite",
    "author": "Blackwall",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > 4D Transform",
    "description": "Lite Blender addon for real-time tesseract projection and 4D rotation",
    "category": "Object",
}

import bpy
import math
from bpy.props import FloatProperty, PointerProperty, EnumProperty
from bpy.types import PropertyGroup, Panel, Operator

object_4d_data = {}


class UNIVERSAL_PG_4d_settings(PropertyGroup):
    object_type: EnumProperty(
        name="Object Type",
        items=[
            ('MESH', "Mesh", "Create tesseract as mesh"),
            ('CURVE', "Curve", "Create tesseract as curve"),
        ],
        default='MESH'
    )

    speed: FloatProperty(name="Speed", default=1.0, min=0.0, max=5.0)
    scale: FloatProperty(name="Scale", default=1.0, min=0.1, max=10.0)
    w_depth: FloatProperty(name="4D Depth", default=4.0, min=2.0, max=10.0)

    rotation_xy: FloatProperty(name="XY Rotation", default=0.0, min=0.0, max=2.0)
    rotation_xz: FloatProperty(name="XZ Rotation", default=0.0, min=0.0, max=2.0)
    rotation_xw: FloatProperty(name="XW Rotation", default=0.0, min=0.0, max=2.0)
    rotation_yz: FloatProperty(name="YZ Rotation", default=0.0, min=0.0, max=2.0)
    rotation_yw: FloatProperty(name="YW Rotation", default=0.0, min=0.0, max=2.0)
    rotation_zw: FloatProperty(name="ZW Rotation", default=0.0, min=0.0, max=2.0)


class Hypercube4D:
    @staticmethod
    def generate_tesseract(size=1.0):
        vertices = []
        edges = []

        for i in range(16):
            x = size * (1 if (i & 1) else -1)
            y = size * (1 if (i & 2) else -1)
            z = size * (1 if (i & 4) else -1)
            w = size * (1 if (i & 8) else -1)
            vertices.append([x, y, z, w])

        for i in range(16):
            for j in range(i + 1, 16):
                diff = i ^ j
                if diff & (diff - 1) == 0:
                    edges.append((i, j))

        return vertices, edges


def rot4(v, a, b, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    v_copy = v[:]
    va = v[a]
    vb = v[b]
    v_copy[a] = va * c - vb * s
    v_copy[b] = va * s + vb * c
    return v_copy


def proj4to3(p, w_depth=4.0):
    denom = (w_depth - p[3])
    if abs(denom) < 1e-9:
        denom = 1e-9
    k = w_depth / denom
    return [p[0] * k, p[1] * k, p[2] * k]


def apply_4d_transform(vertex_4d, angles, scale=1.0):
    p = [vertex_4d[i] * scale for i in range(4)]

    if abs(angles['xy']) > 1e-6:
        p = rot4(p, 0, 1, angles['xy'])
    if abs(angles['xz']) > 1e-6:
        p = rot4(p, 0, 2, angles['xz'])
    if abs(angles['yz']) > 1e-6:
        p = rot4(p, 1, 2, angles['yz'])
    if abs(angles['xw']) > 1e-6:
        p = rot4(p, 0, 3, angles['xw'])
    if abs(angles['yw']) > 1e-6:
        p = rot4(p, 1, 3, angles['yw'])
    if abs(angles['zw']) > 1e-6:
        p = rot4(p, 2, 3, angles['zw'])

    return p


def ensure_timer_running():
    if not bpy.app.timers.is_registered(animation_update):
        bpy.app.timers.register(animation_update, persistent=True)


def animation_update():
    context = bpy.context

    if not hasattr(context.scene, "universal_4d_settings"):
        return 1.0 / 60.0

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
            _transform_4d_object(obj, data, settings, current_time)

    return 1.0 / 60.0


def _transform_4d_object(obj, data, settings, current_time):
    try:
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
            _transform_curve_object(obj, data, angles, settings.w_depth, scale)
        else:
            _transform_mesh_object(obj, data, angles, settings.w_depth, scale)

    except Exception as e:
        print(f"Error transforming {obj.name}: {e}")


def _transform_mesh_object(obj, data, angles, w_depth, scale):
    try:
        mesh = obj.data
        original_vertices_4d = data["original_vertices_4d"]

        for i, vert in enumerate(mesh.vertices):
            if i < len(original_vertices_4d):
                transformed = apply_4d_transform(original_vertices_4d[i], angles, scale)
                proj = proj4to3(transformed, w_depth)
                vert.co.x = proj[0]
                vert.co.y = proj[1]
                vert.co.z = proj[2]

        mesh.update()

    except Exception as e:
        print(f"Error transforming mesh {obj.name}: {e}")


def _transform_curve_object(obj, data, angles, w_depth, scale):
    try:
        curve = obj.data
        edges = data["edges"]
        original_vertices_4d = data["original_vertices_4d"]

        transformed_vertices = []
        for vert_4d in original_vertices_4d:
            transformed = apply_4d_transform(vert_4d, angles, scale)
            proj = proj4to3(transformed, w_depth)
            transformed_vertices.append((proj[0], proj[1], proj[2]))

        while curve.splines and len(curve.splines) > 0:
            curve.splines.remove(curve.splines[-1])

        for edge in edges:
            if edge[0] < len(transformed_vertices) and edge[1] < len(transformed_vertices):
                spline = curve.splines.new('POLY')
                spline.points.add(1)
                a = (*transformed_vertices[edge[0]], 1.0)
                b = (*transformed_vertices[edge[1]], 1.0)
                spline.points[0].co = a
                spline.points[1].co = b
                spline.use_cyclic_u = False

    except Exception as e:
        print(f"Error transforming curve {obj.name}: {e}")


def _reset_object_to_original(obj, data, w_depth):
    try:
        original_vertices_4d = data["original_vertices_4d"]

        if data.get("type") == "CURVE":
            curve = obj.data
            edges = data["edges"]
            original_vertices_3d = [proj4to3(v, w_depth) for v in original_vertices_4d]

            while curve.splines and len(curve.splines) > 0:
                curve.splines.remove(curve.splines[-1])

            for edge in edges:
                if edge[0] < len(original_vertices_3d) and edge[1] < len(original_vertices_3d):
                    spline = curve.splines.new('POLY')
                    spline.points.add(1)
                    a = (*original_vertices_3d[edge[0]], 1.0)
                    b = (*original_vertices_3d[edge[1]], 1.0)
                    spline.points[0].co = a
                    spline.points[1].co = b
                    spline.use_cyclic_u = False
        else:
            mesh = obj.data
            for i, vert in enumerate(mesh.vertices):
                if i < len(original_vertices_4d):
                    proj = proj4to3(original_vertices_4d[i], w_depth)
                    vert.co.x = proj[0]
                    vert.co.y = proj[1]
                    vert.co.z = proj[2]
            mesh.update()

    except Exception as e:
        print(f"Error resetting {obj.name}: {e}")


class UNIVERSAL_OT_create_tesseract(Operator):
    bl_idname = "universal.create_tesseract"
    bl_label = "Create Tesseract"
    bl_description = "Create 4D hypercube"
    bl_options = {'REGISTER', 'UNDO'}

    size: FloatProperty(name="Size", default=1.0, min=0.1, max=5.0)

    def execute(self, context):
        try:
            settings = context.scene.universal_4d_settings
            vertices_4d, edges = Hypercube4D.generate_tesseract(self.size)
            vertices_3d = [proj4to3(v, settings.w_depth) for v in vertices_4d]

            mat = bpy.data.materials.get("Blackwall_4D_Material")
            if mat is None:
                mat = bpy.data.materials.new(name="Blackwall_4D_Material")
                mat.use_nodes = True
                nt = mat.node_tree
                nodes = nt.nodes
                links = nt.links
                for n in list(nodes):
                    nodes.remove(n)
                output = nodes.new(type='ShaderNodeOutputMaterial')
                emission = nodes.new(type='ShaderNodeEmission')
                emission.inputs[0].default_value = (0.85, 0.92, 1.0, 1.0)
                emission.inputs[1].default_value = 2.0
                links.new(emission.outputs[0], output.inputs[0])

            if settings.object_type == 'CURVE':
                curve = bpy.data.curves.new("Tesseract_Curve", 'CURVE')
                curve.dimensions = '3D'
                curve.bevel_depth = 0.02
                for edge in edges:
                    spline = curve.splines.new('POLY')
                    spline.points.add(1)
                    a = (*vertices_3d[edge[0]], 1.0)
                    b = (*vertices_3d[edge[1]], 1.0)
                    spline.points[0].co = a
                    spline.points[1].co = b
                    spline.use_cyclic_u = False
                obj = bpy.data.objects.new("Tesseract_Curve", curve)
                context.collection.objects.link(obj)
                data_type = "CURVE"
            else:
                mesh = bpy.data.meshes.new("Tesseract_Mesh")
                mesh.from_pydata(vertices_3d, edges, [])
                mesh.update()
                obj = bpy.data.objects.new("Tesseract_Mesh", mesh)
                context.collection.objects.link(obj)
                data_type = "MESH"

            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat

            for o in context.selected_objects:
                o.select_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj

            object_4d_data[obj.name] = {
                "type": data_type,
                "vertices_4d": [v[:] for v in vertices_4d],
                "original_vertices_4d": [v[:] for v in vertices_4d],
                "edges": edges,
                "animation_running": False,
            }

            self.report({'INFO'}, f"Tesseract {data_type.lower()} created")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}


class UNIVERSAL_OT_start_all(Operator):
    bl_idname = "universal.start_all"
    bl_label = "Start"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if not object_4d_data:
            self.report({'WARNING'}, "No tesseract created")
            return {'CANCELLED'}

        for _, data in object_4d_data.items():
            data["animation_running"] = True

        ensure_timer_running()
        self.report({'INFO'}, "Animation started")
        return {'FINISHED'}


class UNIVERSAL_OT_stop_all(Operator):
    bl_idname = "universal.stop_all"
    bl_label = "Stop"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if not object_4d_data:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

        for _, data in object_4d_data.items():
            data["animation_running"] = False

        self.report({'INFO'}, "Animation stopped")
        return {'FINISHED'}


class UNIVERSAL_OT_reset_all(Operator):
    bl_idname = "universal.reset_all"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.universal_4d_settings

        for _, data in object_4d_data.items():
            data["animation_running"] = False

        for obj_name in list(object_4d_data.keys()):
            obj = bpy.data.objects.get(obj_name)
            if obj is not None:
                _reset_object_to_original(obj, object_4d_data[obj_name], settings.w_depth)

        settings.speed = 1.0
        settings.scale = 1.0
        settings.w_depth = 4.0
        settings.rotation_xy = 0.0
        settings.rotation_xz = 0.0
        settings.rotation_xw = 0.0
        settings.rotation_yz = 0.0
        settings.rotation_yw = 0.0
        settings.rotation_zw = 0.0

        self.report({'INFO'}, "Reset complete")
        return {'FINISHED'}


class UNIVERSAL_PT_4d_panel(Panel):
    bl_label = "4D Transformer Lite"
    bl_idname = "UNIVERSAL_PT_4d_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "4D Transform"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.universal_4d_settings

        box = layout.box()
        box.label(text="Create")
        box.operator("universal.create_tesseract", text="Create Tesseract", icon='MESH_GRID')

        box = layout.box()
        box.label(text="Playback")
        row = box.row(align=True)
        row.operator("universal.start_all", text="Start", icon='PLAY')
        row.operator("universal.stop_all", text="Stop", icon='PAUSE')
        box.operator("universal.reset_all", text="Reset", icon='LOOP_BACK')

        box = layout.box()
        box.label(text="Settings")
        box.prop(settings, "object_type")
        box.prop(settings, "speed")
        box.prop(settings, "scale")
        box.prop(settings, "w_depth")

        box = layout.box()
        box.label(text="Rotation")
        box.prop(settings, "rotation_xy")
        box.prop(settings, "rotation_xz")
        box.prop(settings, "rotation_xw")
        box.prop(settings, "rotation_yz")
        box.prop(settings, "rotation_yw")
        box.prop(settings, "rotation_zw")


classes = [
    UNIVERSAL_PG_4d_settings,
    UNIVERSAL_OT_create_tesseract,
    UNIVERSAL_OT_start_all,
    UNIVERSAL_OT_stop_all,
    UNIVERSAL_OT_reset_all,
    UNIVERSAL_PT_4d_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.universal_4d_settings = PointerProperty(type=UNIVERSAL_PG_4d_settings)


def unregister():
    if bpy.app.timers.is_registered(animation_update):
        try:
            bpy.app.timers.unregister(animation_update)
        except Exception:
            pass

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    try:
        del bpy.types.Scene.universal_4d_settings
    except Exception:
        pass


if __name__ == "__main__":
    register()
