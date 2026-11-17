import bpy #disponibiliza a API Python do Blender
import bmesh #mesh: vértices, arestas e faces
import math #execução de cálculos matematicos
import random #aleatoriedade: distribuição de elementos
from mathutils import Vector #vetores em 3d

random.seed(7)

#LIMPA A CENA
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for blk in (bpy.data.meshes, bpy.data.materials):
    for item in list(blk):
        blk.remove(item)

#FUNÇAÕ QUE DEFINE AS CARACTERÍSTICAS (NÓS)
def make_mat(name, color, rough=0.95, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True

    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Alpha"].default_value = alpha

    return m

MATS = {
    "grass1": make_mat("grass1", (0.18, 0.55, 0.10)),
    "grass2": make_mat("grass2", (0.24, 0.62, 0.13)),
    "grass3": make_mat("grass3", (0.14, 0.47, 0.09)),
    "dirt":   make_mat("dirt",   (0.35, 0.22, 0.12)),
    "stone":  make_mat("stone",  (0.45, 0.33, 0.28)),
    "stone2": make_mat("stone2", (0.52, 0.42, 0.37)),
    "snow":   make_mat("snow",   (0.92, 0.94, 0.98)),
    "sand":   make_mat("sand",   (0.55, 0.45, 0.28)),
    "log":    make_mat("log",    (0.30, 0.19, 0.09)),
    "plank":  make_mat("plank",  (0.55, 0.38, 0.18)),
    "plank2": make_mat("plank2", (0.48, 0.33, 0.15)),
    "roof":   make_mat("roof",   (0.42, 0.26, 0.12)),
    "roof2":  make_mat("roof2",  (0.50, 0.32, 0.15)),
    "wall":   make_mat("wall",   (0.88, 0.88, 0.84)),
    "glass":  make_mat("glass",  (0.65, 0.80, 0.90), rough=0.1, alpha=0.2),
    "leaf1":  make_mat("leaf1",  (0.08, 0.38, 0.07)),
    "leaf2":  make_mat("leaf2",  (0.12, 0.45, 0.09)),
    "leaf3":  make_mat("leaf3",  (0.06, 0.30, 0.06)),
    "path":   make_mat("path",   (0.50, 0.50, 0.52)),
    "wh":     make_mat("wh",     (0.95, 0.95, 0.95)),
    "pink":   make_mat("pink",   (0.90, 0.40, 0.60)),
    "yellow": make_mat("yellow", (0.95, 0.85, 0.15)),
    "red":    make_mat("red",    (0.85, 0.12, 0.10)),
    "water":  make_mat("water",  (0.05, 0.30, 0.85), rough=0.05, alpha=0.7),
}
# agua com um pouco mais de brilho
_w = MATS["water"].node_tree.nodes.get("Principled BSDF")
try:
    _w.inputs["Specular IOR Level"].default_value = 0.8
except Exception:
    pass
