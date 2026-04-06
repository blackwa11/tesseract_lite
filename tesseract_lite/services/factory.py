import bpy

from ..core.geometry import Hypercube4D
from ..core.state import object_4d_data
from ..core.transforms import proj4to3
from .materials import ensure_material


def create_tesseract_object(context, size, object_type, w_depth):
    vertices_4d, edges = Hypercube4D.generate_tesseract(size)
    vertices_3d = [proj4to3(vertex, w_depth) for vertex in vertices_4d]
    material = ensure_material()

    if object_type == 'CURVE':
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
        data_type = "CURVE"
    else:
        mesh = bpy.data.meshes.new("Tesseract_Mesh")
        mesh.from_pydata(vertices_3d, edges, [])
        mesh.update()
        obj = bpy.data.objects.new("Tesseract_Mesh", mesh)
        data_type = "MESH"

    context.collection.objects.link(obj)

    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material

    for selected in context.selected_objects:
        selected.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj

    object_4d_data[obj.name] = {
        "type": data_type,
        "vertices_4d": [vertex[:] for vertex in vertices_4d],
        "original_vertices_4d": [vertex[:] for vertex in vertices_4d],
        "edges": edges,
        "animation_running": False,
    }

    return obj, data_type
