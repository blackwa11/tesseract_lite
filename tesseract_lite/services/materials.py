import bpy


MATERIAL_NAME = "Blackwall_4D_Material"


def get_or_create_material():
    mat = bpy.data.materials.get(MATERIAL_NAME)
    if mat is None:
        mat = bpy.data.materials.new(name=MATERIAL_NAME)
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links

        for node in list(nodes):
            nodes.remove(node)

        output = nodes.new(type='ShaderNodeOutputMaterial')
        emission = nodes.new(type='ShaderNodeEmission')
        emission.inputs[0].default_value = (0.85, 0.92, 1.0, 1.0)
        emission.inputs[1].default_value = 2.0
        links.new(emission.outputs[0], output.inputs[0])

    return mat
