import math


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
