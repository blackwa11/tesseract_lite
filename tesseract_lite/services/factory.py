import bpy

from ..core.geometry import Hypercube4D
from ..core.transforms import proj4to3
from ..core.state import object_4d_data
from .materials import get_or_create_material


def _apply_material(obj, material):
    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material


def _select_created_object(context, obj):
    for o in context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def create_tesseract_object(context, size):
    settings = context.scene.universal_4d_settings
    vertices_4d, edges = Hypercube4D.generate_tesseract(size)
    vertices_3d = [proj4to3(v, settings.w_depth) for v in vertices_4d]
    material = get_or_create_material()

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

    _apply_material(obj, material)
    _select_created_object(context, obj)

    object_4d_data[obj.name] = {
        "type": data_type,
        "vertices_4d": [v[:] for v in vertices_4d],
        "original_vertices_4d": [v[:] for v in vertices_4d],
        "edges": edges,
        "animation_running": False,
    }

    return obj, data_type
