"""Modelo 3D do volante - protótipo P1 (rev00).

Sistema de coordenadas (igual ao 'Frontal' do SolidWorks visto pelo piloto):
  X para a direita, Y para cima, Z na direção do piloto.
  Origem: eixo da base no plano da FACE TRASEIRA da placa frontal.
  Tudo que fica atrás da placa tem Z negativo.

Gera STEP de cada peça, a montagem completa em STEP, STL das peças impressas
e um relatório de interferências (aleta em repouso e acionada).
"""
import math
import os
import sys
import cadquery as cq

OUT = sys.argv[1] if len(sys.argv) > 1 else "saida"
os.makedirs(f"{OUT}/pecas_step", exist_ok=True)
os.makedirs(f"{OUT}/impressao_stl", exist_ok=True)

# ============================================================ parâmetros
T_PLACA = 5.0          # protótipo impresso (final em carbono: 3 mm)
HUB = (0.0, -5.0)
PCD = 70.0

BOTOES = {  # nome: (x, y, diâmetro do furo)
    "B1": (84, 34, 16), "B2": (-84, 34, 16), "B3": (84, 8, 16), "B4": (-84, 8, 16),
    "B5": (-78, 88, 19), "B6": (78, 88, 19), "B7": (-60, 60, 16), "B8": (60, 60, 16),
    "B9": (-82, -22, 16), "B10": (-26, -56, 16), "B11": (26, -56, 16), "B12": (82, -22, 16),
}
ENCODERS = {"E1": (-98, 62), "E2": (98, 62), "E3": (-56, -38), "E4": (56, -38)}
PROF_BOTAO = 25.0      # requisito: corpo dos botões <= 25 mm atrás da placa

# Aleta (lado direito; o esquerdo é espelhado)
X_EIXO = 60.0          # eixo de giro
Y_ALETA = 20.0         # centro vertical da aleta
Z_CHAPA = 40.0         # face frontal da chapa da aleta, atrás da placa
T_CHAPA = 3.0
T_CARR = 8.0           # espessura do carregador
Z_EIXO = -(Z_CHAPA - T_CARR / 2)          # -36
L_RET, L_SENS, L_DEDO = 25.0, 40.0, 70.0
GAP_SENS = 6.0
GAP_RET = 0.3
CURSO_BATENTE = 3.4

CONTORNO_ALETA = [(10, -15), (50, -15), (68, -24), (92, -24), (100, -16),
                  (100, 16), (92, 24), (68, 24), (50, 15), (10, 15)]
FUROS_M3 = [(16, 10), (16, -10), (46, 10), (46, -10)]

# Pegada
PEG_X = (120.0, 146.0)
PEG_Y = (-82.0, 94.0)
PEG_Z = (-29.0, 8.0)
FURO_PEG_Y = [80, 40, 0, -30]
X_FURO_PEG = 112.0


def caixa(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def furo_z(peca, x, y, d, z0=-200, z1=200):
    cil = cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))
    return peca.cut(cil)


# ============================================================ placa frontal
def placa_frontal():
    pts = [(-120, 108), (120, 108), (120, -72), (-120, -72)]
    s = (cq.Sketch().polygon(pts + [pts[0]])
         .vertices(">Y").fillet(18)
         .vertices("<Y").fillet(36))
    p = cq.Workplane("XY").placeSketch(s).extrude(T_PLACA)
    for (x, y, d) in BOTOES.values():
        p = furo_z(p, x, y, d)
    for (x, y) in ENCODERS.values():
        p = furo_z(p, x, y, 7.2)
    for k in range(6):
        a = math.radians(90 + 60 * k)
        p = furo_z(p, HUB[0] + PCD / 2 * math.cos(a), HUB[1] + PCD / 2 * math.sin(a), 5.5)
    for sx in (-1, 1):
        for y in FURO_PEG_Y:
            p = furo_z(p, sx * X_FURO_PEG, y, 4.5)       # M4 da pegada
        for y in (12, 28):
            p = furo_z(p, sx * 50, y, 3.4)               # M3 do suporte da aleta
    return p


# ============================================================ pegada
def pegada_direita():
    corpo = caixa(PEG_X[0], PEG_X[1], PEG_Y[0], PEG_Y[1], PEG_Z[0], PEG_Z[1])
    corpo = corpo.edges("|Y").fillet(12)
    corpo = corpo.faces(">Y or <Y").edges().fillet(5)
    aba = caixa(106, PEG_X[0] + 1, -40, 88, -8, 0)   # começa em 106: livra o corpo de E1/E2
    p = corpo.union(aba)
    # recorte para a placa frontal encaixar (degrau)
    p = p.cut(caixa(100, 120.2, PEG_Y[0] - 1, PEG_Y[1] + 1, 0, T_PLACA + 0.2))
    for y in FURO_PEG_Y:
        p = furo_z(p, X_FURO_PEG, y, 5.6, -6, 0.1)    # inserto M4 a quente
    return p


# ============================================================ aleta
def s_para_x(s):
    return X_EIXO + s


def chapa_aleta():
    """Chapa da aleta direita (a mesma peça serve à esquerda, girada 180°)."""
    pts = [(s_para_x(s), Y_ALETA + y) for s, y in CONTORNO_ALETA]
    z0 = -(Z_CHAPA + T_CHAPA)
    p = cq.Workplane("XY").polyline(pts).close().extrude(T_CHAPA).translate((0, 0, z0))
    for s, y in FUROS_M3:
        p = furo_z(p, s_para_x(s), Y_ALETA + y, 3.4)
    p = furo_z(p, s_para_x(L_RET), Y_ALETA, 11.0)
    return p


def carregador():
    z0, z1 = -Z_CHAPA, -Z_CHAPA + T_CARR
    p = caixa(X_EIXO, X_EIXO + 50, Y_ALETA - 15, Y_ALETA + 15, z0, z1)
    cubo = (cq.Workplane("XZ").circle(6).extrude(-30)
            .translate((X_EIXO, Y_ALETA - 15, Z_EIXO)))
    p = p.union(cubo)
    furo = cq.Workplane("XZ").circle(3.0).extrude(-40).translate((X_EIXO, Y_ALETA - 20, Z_EIXO))
    p = p.cut(furo)                                          # buchas Ø6
    for s, y in FUROS_M3:
        p = furo_z(p, s_para_x(s), Y_ALETA + y, 4.2, z0 - 1, z0 + 6)   # insertos M3
    p = furo_z(p, s_para_x(L_RET), Y_ALETA, 10.2, z0 - 1, z0 + 1)      # ímã retorno
    p = furo_z(p, s_para_x(L_SENS), Y_ALETA, 5.2, z1 - 3, z1 + 1)      # ímã sensor
    return p


def suporte_direito():
    zc = -Z_CHAPA - T_CHAPA            # face traseira da chapa (-43)
    base = caixa(46, 74, Y_ALETA - 21.5, Y_ALETA + 21.5, -6, 0)
    orelha_sup = caixa(54, 66, Y_ALETA + 15.5, Y_ALETA + 21.5, zc - 9, -6)
    orelha_inf = caixa(54, 66, Y_ALETA - 21.5, Y_ALETA - 15.5, Z_EIXO - 6, -6)
    braco = caixa(54, 91, Y_ALETA + 15.5, Y_ALETA + 21.5, zc - 9, zc - 2)
    aba = caixa(79, 91, Y_ALETA - 7, Y_ALETA + 21.5, zc - 9, zc - 2)
    z_sens = -Z_CHAPA + T_CARR + GAP_SENS    # face do sensor (-26)
    poste = caixa(64, 70, Y_ALETA - 3, Y_ALETA + 3, z_sens, -6)
    braco_s = caixa(64, 112, Y_ALETA - 3, Y_ALETA + 3, z_sens, z_sens + 5)
    p = base.union(orelha_sup).union(orelha_inf).union(braco).union(aba).union(poste).union(braco_s)
    pino = cq.Workplane("XZ").circle(2.05).extrude(-60).translate((X_EIXO, Y_ALETA - 30, Z_EIXO))
    p = p.cut(pino)
    p = furo_z(p, s_para_x(L_RET), Y_ALETA, 6.8, zc - 10, zc - 1)      # rosca M8
    p = p.cut(caixa(s_para_x(L_SENS) - 2, s_para_x(L_SENS) + 2, Y_ALETA - 1.5,
                    Y_ALETA + 1.5, z_sens, z_sens + 1.5))              # SS49E
    for y in (12, 28):
        p = furo_z(p, 50, y, 3.4)
    return p


def batente():
    z_face = -Z_CHAPA + T_CARR + CURSO_BATENTE   # -28.6
    z_sens = -Z_CHAPA + T_CARR + GAP_SENS
    return caixa(104, 112, Y_ALETA - 3, Y_ALETA + 3, z_face, z_sens)


# ---- peças compradas (referência, não fabricar)
def ref_ima_retorno():
    zc = -Z_CHAPA - T_CHAPA
    return cq.Workplane("XY").circle(5).extrude(4).translate((s_para_x(L_RET), Y_ALETA, zc))


def ref_ima_sensor():
    z1 = -Z_CHAPA + T_CARR
    return cq.Workplane("XY").circle(2.5).extrude(3).translate((s_para_x(L_SENS), Y_ALETA, z1 - 3))


def ref_parafuso_m8():
    zc = -Z_CHAPA - T_CHAPA - GAP_RET
    return cq.Workplane("XY").circle(4).extrude(10).translate((s_para_x(L_RET), Y_ALETA, zc - 10))


def ref_eixo():
    return cq.Workplane("XZ").circle(2).extrude(-45).translate((X_EIXO, Y_ALETA - 22.5, Z_EIXO))


def ref_sensor():
    z_sens = -Z_CHAPA + T_CARR + GAP_SENS
    return caixa(s_para_x(L_SENS) - 2, s_para_x(L_SENS) + 2, Y_ALETA - 1.5, Y_ALETA + 1.5,
                 z_sens, z_sens + 1.5)


def ref_botoes():
    r = None
    for (x, y, d) in BOTOES.values():
        corpo = cq.Workplane("XY").circle(d / 2).extrude(PROF_BOTAO).translate((x, y, -PROF_BOTAO))
        capa = cq.Workplane("XY").circle(d / 2 + 2).extrude(4).translate((x, y, T_PLACA))
        b = corpo.union(capa)
        r = b if r is None else r.union(b)
    return r


def ref_encoders():
    r = None
    for (x, y) in ENCODERS.values():
        corpo = caixa(x - 6.25, x + 6.25, y - 6.75, y + 6.75, -7, 0)
        knob = cq.Workplane("XY").circle(13).extrude(15).translate((x, y, T_PLACA + 2))
        e = corpo.union(knob)
        r = e if r is None else r.union(e)
    return r


def ref_adaptador():
    a = cq.Workplane("XY").circle(45).extrude(10).translate((HUB[0], HUB[1], -10))
    return a


# ============================================================ utilidades
def espelhar(w):
    return w.mirror("YZ")


def girar_aleta(w, lado, graus):
    """Gira o conjunto da aleta em torno do eixo; positivo = puxar para o piloto."""
    sx = 1 if lado == "dir" else -1
    a = -graus * sx
    return w.rotate((sx * X_EIXO, 0, Z_EIXO), (sx * X_EIXO, 1, Z_EIXO), a)


def volume(w):
    try:
        return sum(s.Volume() for s in w.solids().vals())
    except Exception:
        return 0.0


# ============================================================ montagem
def montar(angulo_aleta=0.0):
    pecas = {}
    pecas["placa_frontal"] = (placa_frontal(), "fab", (0.15, 0.15, 0.15))
    peg = pegada_direita()
    pecas["pegada_dir"] = (peg, "fab", (0.25, 0.25, 0.25))
    pecas["pegada_esq"] = (espelhar(peg), "fab", (0.25, 0.25, 0.25))
    sup = suporte_direito()
    pecas["suporte_aleta_dir"] = (sup, "fab", (0.2, 0.6, 0.3))
    pecas["suporte_aleta_esq"] = (espelhar(sup), "fab", (0.2, 0.6, 0.3))
    bat = batente()
    pecas["batente_dir"] = (bat, "fab", (0.95, 0.55, 0.1))
    pecas["batente_esq"] = (espelhar(bat), "fab", (0.95, 0.55, 0.1))
    pecas["sensor_dir"] = (ref_sensor(), "ref", (0.05, 0.05, 0.05))
    pecas["sensor_esq"] = (espelhar(ref_sensor()), "ref", (0.05, 0.05, 0.05))
    pecas["parafuso_m8_dir"] = (ref_parafuso_m8(), "ref", (0.5, 0.5, 0.5))
    pecas["parafuso_m8_esq"] = (espelhar(ref_parafuso_m8()), "ref", (0.5, 0.5, 0.5))
    pecas["eixo_dir"] = (ref_eixo(), "ref", (0.7, 0.7, 0.7))
    pecas["eixo_esq"] = (espelhar(ref_eixo()), "ref", (0.7, 0.7, 0.7))

    # conjunto móvel
    moveis = {
        "chapa_aleta": (chapa_aleta(), "fab", (0.75, 0.78, 0.82)),
        "carregador": (carregador(), "fab", (0.2, 0.4, 0.8)),
        "ima_retorno": (ref_ima_retorno(), "ref", (0.8, 0.15, 0.15)),
        "ima_sensor": (ref_ima_sensor(), "ref", (0.8, 0.15, 0.15)),
    }
    for nome, (w, tipo, cor) in moveis.items():
        pecas[f"{nome}_dir"] = (girar_aleta(w, "dir", angulo_aleta), tipo, cor)
        pecas[f"{nome}_esq"] = (girar_aleta(espelhar(w), "esq", angulo_aleta), tipo, cor)

    pecas["REF_botoes"] = (ref_botoes(), "ref", (0.1, 0.3, 0.8))
    pecas["REF_encoders"] = (ref_encoders(), "ref", (0.1, 0.55, 0.3))
    pecas["REF_adaptador_QR"] = (ref_adaptador(), "ref", (0.6, 0.1, 0.1))
    return pecas


# Pares que se tocam por projeto (encaixes, roscas, peças coladas)
ESPERADOS = {
    frozenset(p) for lado in ("dir", "esq") for p in [
        (f"parafuso_m8_{lado}", f"suporte_aleta_{lado}"),
        (f"eixo_{lado}", f"carregador_{lado}"),
        (f"eixo_{lado}", f"suporte_aleta_{lado}"),
        (f"sensor_{lado}", f"suporte_aleta_{lado}"),
        (f"batente_{lado}", f"suporte_aleta_{lado}"),
        (f"ima_retorno_{lado}", f"carregador_{lado}"),
        (f"ima_retorno_{lado}", f"chapa_aleta_{lado}"),
        (f"ima_sensor_{lado}", f"carregador_{lado}"),
        (f"chapa_aleta_{lado}", f"carregador_{lado}"),
        (f"suporte_aleta_{lado}", "placa_frontal"),
        (f"pegada_{lado}", "placa_frontal"),
    ]
} | {frozenset(("REF_botoes", "placa_frontal")), frozenset(("REF_encoders", "placa_frontal")),
     frozenset(("REF_adaptador_QR", "placa_frontal"))}


def interferencias(pecas, limite=0.5):
    nomes = list(pecas)
    achados = []
    bbs = {n: pecas[n][0].val().BoundingBox() for n in nomes}
    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            a, b = nomes[i], nomes[j]
            if frozenset((a, b)) in ESPERADOS:
                continue
            A, B = bbs[a], bbs[b]
            if (A.xmax < B.xmin or B.xmax < A.xmin or A.ymax < B.ymin or B.ymax < A.ymin
                    or A.zmax < B.zmin or B.zmax < A.zmin):
                continue
            try:
                v = volume(pecas[a][0].intersect(pecas[b][0]))
            except Exception:
                v = -1
            if v > limite or v < 0:
                achados.append((a, b, v))
    return achados


def folga_minima(w1, w2):
    return w1.val().distance(w2.val()) if hasattr(w1.val(), "distance") else None


if __name__ == "__main__":
    pecas = montar(0.0)

    # STEP de cada peça fabricada (lado direito + esquerdo quando diferente)
    fabricar = {
        "placa_frontal_P1": pecas["placa_frontal"][0],
        "pegada_dir": pecas["pegada_dir"][0],
        "pegada_esq": pecas["pegada_esq"][0],
        "suporte_aleta_dir": pecas["suporte_aleta_dir"][0],
        "suporte_aleta_esq": pecas["suporte_aleta_esq"][0],
        "carregador_aleta_x2": carregador(),
        "chapa_aleta_x2": chapa_aleta(),
        "batente_TPU_x2": batente(),
    }
    for nome, w in fabricar.items():
        cq.exporters.export(w, f"{OUT}/pecas_step/{nome}.step")
    for nome in ("placa_frontal_P1", "pegada_dir", "pegada_esq", "suporte_aleta_dir",
                 "suporte_aleta_esq", "carregador_aleta_x2", "batente_TPU_x2"):
        cq.exporters.export(fabricar[nome], f"{OUT}/impressao_stl/{nome}.stl", tolerance=0.05,
                            angularTolerance=0.1)

    # Montagem
    asm = cq.Assembly(name="volante_P1")
    for nome, (w, tipo, cor) in pecas.items():
        asm.add(w, name=nome, color=cq.Color(*cor))
    asm.save(f"{OUT}/volante_P1_montagem.step")

    # Interferências
    linhas = []
    for ang, rot in ((0.0, "repouso"), (3.85, "acionada (encosta no batente)")):
        pc = pecas if ang == 0 else montar(ang)
        ach = interferencias(pc)
        linhas.append(f"Aleta {rot} ({ang:.2f}°): " + ("nenhuma interferência" if not ach else ""))
        for a, b, v in ach:
            linhas.append(f"   {a} × {b}: {v:.1f} mm³")
        # folgas críticas
        for lado in ("dir",):
            for alvo in ("REF_botoes", f"pegada_{lado}", f"batente_{lado}", f"sensor_{lado}"):
                orig = "ima_sensor_dir" if alvo.startswith("sensor") else (
                    "carregador_dir" if alvo != f"pegada_{lado}" else "chapa_aleta_dir")
                try:
                    d = pc[orig][0].val().distance(pc[alvo][0].val())
                    d = d[0] if isinstance(d, tuple) else d
                except Exception:
                    d = float("nan")
                linhas.append(f"   folga {orig} ↔ {alvo}: {d:.2f} mm")

    # Massas (densidades: PETG 1,27 com 40% de preenchimento efetivo ~0,6; Al 2,70)
    rel_massa = []
    dens = {"placa_frontal_P1": 1.27 * 0.6, "pegada_dir": 1.27 * 0.5, "pegada_esq": 1.27 * 0.5,
            "suporte_aleta_dir": 1.15 * 0.7, "suporte_aleta_esq": 1.15 * 0.7,
            "carregador_aleta_x2": 1.15 * 0.7 * 2, "chapa_aleta_x2": 2.70 * 2,
            "batente_TPU_x2": 1.2 * 2}
    total = 0
    for n, w in fabricar.items():
        m = volume(w) / 1000 * dens[n]
        total += m
        rel_massa.append(f"   {n}: {volume(w)/1000:.1f} cm³ → {m:.0f} g")
    rel_massa.append(f"   TOTAL impresso + chapas: ~{total:.0f} g "
                     "(sem eletrônica, botões, ímãs e parafusos)")

    with open(f"{OUT}/relatorio_verificacao.txt", "w") as f:
        f.write("VERIFICAÇÃO DO MODELO 3D — protótipo P1 rev00\n\n")
        f.write("\n".join(linhas) + "\n\nMASSAS ESTIMADAS\n" + "\n".join(rel_massa) + "\n")
    print("\n".join(linhas))
    print("\n".join(rel_massa))
