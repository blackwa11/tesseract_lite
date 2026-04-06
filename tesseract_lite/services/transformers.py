from ..core.transforms import apply_4d_transform, proj4to3


def transform_mesh_object(obj, data, angles, w_depth, scale):
    mesh = obj.data
    original_vertices_4d = data["original_vertices_4d"]

    for index, vert in enumerate(mesh.vertices):
        if index < len(original_vertices_4d):
            transformed = apply_4d_transform(original_vertices_4d[index], angles, scale)
            proj = proj4to3(transformed, w_depth)
            vert.co.x = proj[0]
            vert.co.y = proj[1]
            vert.co.z = proj[2]

    mesh.update()


def transform_curve_object(obj, data, angles, w_depth, scale):
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


def reset_object_to_original(obj, data, w_depth):
    original_vertices_4d = data["original_vertices_4d"]

    if data.get("type") == "CURVE":
        curve = obj.data
        edges = data["edges"]
        original_vertices_3d = [proj4to3(vertex, w_depth) for vertex in original_vertices_4d]

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
        for index, vert in enumerate(mesh.vertices):
            if index < len(original_vertices_4d):
                proj = proj4to3(original_vertices_4d[index], w_depth)
                vert.co.x = proj[0]
                vert.co.y = proj[1]
                vert.co.z = proj[2]
        mesh.update()
