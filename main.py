import bpy
import bmesh
import math
import random
from mathutils import Vector

random.seed(7)

# 1. LIMPA A CENA DE FORMA SEGURA (sem bpy.ops)
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

for blk in (bpy.data.meshes, bpy.data.materials):
    for item in list(blk):
        if item.users == 0:
            blk.remove(item)

# 2. FUNÇÃO QUE DEFINE OS MATERIAIS
def make_mat(name, color, rough=0.95, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True

    nodes = m.node_tree.nodes
    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)

    if bsdf is None:
        nodes.clear()
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.new(type='ShaderNodeOutputMaterial')
        m.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

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

_w = next((n for n in MATS["water"].node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if _w and "Specular IOR Level" in _w.inputs:
    _w.inputs["Specular IOR Level"].default_value = 0.8

def criar_arvore(x, y, z_base, mesh_base, colecao):
    altura_tronco = random.randint(3, 4)

    for i in range(altura_tronco):
        m_tronco = mesh_base.copy()
        m_tronco.materials.append(MATS["log"])
        tronco = bpy.data.objects.new("Tronco", m_tronco)
        tronco.location = (x, y, z_base + 0.5 + i)
        colecao.objects.link(tronco)

    # 2. Constrói a COPA DE FOLHAS no topo do tronco
    z_copa = z_base + altura_tronco
    mat_folha = MATS[random.choice(["leaf1", "leaf2", "leaf3"])]

    # Camada inferior da copa (3x3 blocos ao redor do tronco)
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            for dz in range(0, 2):
                if dz == 1 and abs(dx) == 1 and abs(dy) == 1:
                    continue
                m_folha = mesh_base.copy()
                m_folha.materials.append(mat_folha)
                folha = bpy.data.objects.new("Folha", m_folha)
                folha.location = (x + dx, y + dy, z_copa + 0.5 + dz)
                colecao.objects.link(folha)

    # Topo da copa (1 bloco central no ponto mais alto)
    m_topo = mesh_base.copy()
    m_topo.materials.append(mat_folha)
    folha_topo = bpy.data.objects.new("Folha", m_topo)
    folha_topo.location = (x, y, z_copa + 2.5)
    colecao.objects.link(folha_topo)

# 3. CRIAÇÃO DO TERRENO GRAMADO (SEM bpy.ops)
def criar_terreno():
    tamanho = 30
    colecao = bpy.context.scene.collection

    # Parâmetros do lago em S
    largura_lago = 3.2
    nivel_agua = 2
    arvores_plantadas = []

    mesh_base = bpy.data.meshes.new("CuboBase")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh_base)
    bm.free()

    for x in range(tamanho):
        for y in range(tamanho):
            centro_x = (tamanho / 2) + math.sin(y * 0.25) * 6.5
            ruido = math.cos(y * 0.6) * 0.5

            dist_curva = abs(x - centro_x) + ruido

            dentro_y = 3 <= y <= (tamanho - 4)

            if dentro_y and dist_curva < largura_lago:
                altura = 1 if dist_curva > largura_lago - 1.2 else 0
            else:
                altura = max(2, int(3 + math.sin(x * 0.3) + math.cos(y * 0.3)))

            if altura > 0:
                m_terra = mesh_base.copy()
                m_terra.materials.append(MATS["dirt"])
                terra = bpy.data.objects.new("Terra", m_terra)
                terra.location = (x, y, (altura - 1) / 2)
                terra.scale.z = altura
                colecao.objects.link(terra)

            na_margem = (2 <= y <= tamanho - 3) and (dist_curva < largura_lago + 1.3)
            if (dentro_y and dist_curva < largura_lago) or (na_margem and altura <= nivel_agua):
                material_topo = MATS["sand"]
                nome_topo = "Areia"
            else:
                material_topo = MATS[random.choice(["grass1", "grass2", "grass3"])]
                nome_topo = "Grama"

            m_topo = mesh_base.copy()
            m_topo.materials.append(material_topo)
            topo = bpy.data.objects.new(nome_topo, m_topo)
            topo.location = (x, y, altura - 0.25)
            topo.scale.z = 0.5
            colecao.objects.link(topo)

            if altura < nivel_agua:
                altura_agua = (nivel_agua - altura) - 0.1
                m_agua = mesh_base.copy()
                m_agua.materials.append(MATS["water"])
                agua = bpy.data.objects.new("Agua", m_agua)
                agua.location = (x, y, altura + (altura_agua / 2))
                agua.scale.z = altura_agua
                colecao.objects.link(agua)

            longe_das_bordas = 2 <= x <= (tamanho - 3) and 2 <= y <= (tamanho - 3)
            if nome_topo == "Grama" and longe_das_bordas:
                if random.random() < 0.06:
                    muito_perto = any(math.hypot(x - ax, y - ay) < 4.0 for ax, ay in arvores_plantadas)
                    if not muito_perto:
                        criar_arvore(x, y, altura, mesh_base, colecao)
                        arvores_plantadas.append((x, y))

    bpy.data.meshes.remove(mesh_base)

criar_terreno()