"""Manual de montagem do volante P1 - estilo blueprint, desenhos gerados do modelo 3D."""
import math
import sys

_SAIDA = sys.argv[1] if len(sys.argv) > 1 else "manual_montagem_volante_P1.pdf"
_TMP = sys.argv[2] if len(sys.argv) > 2 else "/tmp/cadtmp"
sys.argv = ["x", _TMP]
sys.path.insert(0, "/home/claude/volante/cad")

import cadquery as cq  # noqa: E402
import modelo_volante as m  # noqa: E402
from projetor import Vista, caixa_limites, Encaixe  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.lib.utils import simpleSplit  # noqa: E402

REV = "rev01"
W, H = 297 * mm, 210 * mm

# ------------------------------------------------------------------ cores
BG = (0.055, 0.19, 0.40)
GRID = (0.10, 0.27, 0.52)
BRANCO = (1, 1, 1)
FRACO = (0.50, 0.64, 0.82)
NOVO = (0.40, 0.90, 1.00)
ALERTA = (1.00, 0.74, 0.28)
OK = (0.52, 0.95, 0.62)
PAINEL = (0.04, 0.15, 0.33)

# ------------------------------------------------------------------ geometria auxiliar
def cil_z(x, y, z0, d, h):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def cil_y(x, z, y0, d, h):
    return cq.Workplane("XZ").circle(d / 2).extrude(-h).translate((x, y0, z))


def caixa(x0, x1, y0, y1, z0, z1):
    return m.caixa(x0, x1, y0, y1, z0, z1)


def parafuso_z(x, y, z_cabeca, d, L, sentido):
    """Cabeça em z_cabeca, corpo segue no sentido (-1: para trás, +1: para frente)."""
    hc = 0.6 * d
    if sentido < 0:
        cab = cil_z(x, y, z_cabeca, 1.9 * d, hc)
        corpo = cil_z(x, y, z_cabeca - L, d, L)
    else:
        cab = cil_z(x, y, z_cabeca - hc, 1.9 * d, hc)
        corpo = cil_z(x, y, z_cabeca, d, L)
    return cab.union(corpo)


def porca_z(x, y, z0, d):
    return cq.Workplane("XY").polygon(6, 1.8 * d * 1.155).extrude(0.8 * d).translate((x, y, z0))


def mover(w, dx=0, dy=0, dz=0):
    return w.translate((dx, dy, dz))


def centro(w):
    bb = w.val().BoundingBox() if not isinstance(w, list) else None
    return ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)


# Peças do lado direito, na posição final
YA, XE, ZE = m.Y_ALETA, m.X_EIXO, m.Z_EIXO
A_placa = m.placa_frontal()
B_peg = m.pegada_direita()
C_peg = m.espelhar(B_peg)
D_sup = m.suporte_direito()
E_sup = m.espelhar(D_sup)
F_car = m.carregador()
G_chapa = m.chapa_aleta()
H_bat = m.batente()
J_eixo = cil_y(XE, ZE, YA - 22, 4, 44)
K_buchas = [cil_y(XE, ZE, YA - 15, 6, 4), cil_y(XE, ZE, YA + 11, 6, 4)]
L_ima = m.ref_ima_retorno()
M_ima = m.ref_ima_sensor()
N_paraf = m.ref_parafuso_m8()
P_sensor = m.ref_sensor()
Q_ins = [cil_z(m.s_para_x(s), YA + y, -m.Z_CHAPA, 4.6, 5) for s, y in m.FUROS_M3]
R_ins = [cil_z(m.X_FURO_PEG, y, -6, 5.6, 6) for y in m.FURO_PEG_Y]
S_paraf = [parafuso_z(m.s_para_x(s), YA + y, -m.Z_CHAPA - m.T_CHAPA, 3, 8, +1) for s, y in m.FUROS_M3]
T_paraf = [parafuso_z(50, y, m.T_PLACA, 3, 12, -1) for y in (12, 28)]
T_porca = [porca_z(50, y, -8.4, 3) for y in (12, 28)]
U_paraf = [parafuso_z(m.X_FURO_PEG, y, m.T_PLACA, 4, 10, -1) for y in m.FURO_PEG_Y]


def furos_cubo():
    pts = []
    for k in range(6):
        a = math.radians(90 + 60 * k)
        pts.append((m.HUB[0] + m.PCD / 2 * math.cos(a), m.HUB[1] + m.PCD / 2 * math.sin(a)))
    return pts


Z_paraf = [parafuso_z(x, y, m.T_PLACA, 5, 12, -1) for x, y in furos_cubo()]
ADAPT = m.ref_adaptador()
PICO = caixa(-25.5, 25.5, 55.5, 76.5, -2.6, -1.0)


def grupo_movel(dx=0, dy=0, dz=0, lado=1):
    pecas = [F_car, G_chapa, L_ima, M_ima] + K_buchas + S_paraf
    if lado < 0:
        pecas = [m.espelhar(p) for p in pecas]
    return [mover(p, dx, dy, dz) for p in pecas]


def conj_suporte(lado=1, dz=0):
    pecas = [D_sup, H_bat, N_paraf, P_sensor, J_eixo] + grupo_movel()
    if lado < 0:
        pecas = [m.espelhar(p) for p in pecas]
    return [mover(p, dz=dz) for p in pecas]


# ------------------------------------------------------------------ desenho
class Manual:
    def __init__(self, caminho, total):
        self.c = canvas.Canvas(caminho, pagesize=(W, H))
        self.c.setTitle("Manual de montagem - Volante P1")
        self.c.setAuthor("Jarvis - Projeto Cockpit iRacing")
        self.pag = 0
        self.total = total

    # ---- fundo e moldura
    def nova_pagina(self, titulo_curto):
        c = self.c
        if self.pag:
            c.showPage()
        self.pag += 1
        c.setFillColorRGB(*BG)
        c.rect(0, 0, W, H, stroke=0, fill=1)
        c.setStrokeColorRGB(*GRID)
        c.setLineWidth(0.25)
        for i in range(0, 298, 10):
            c.line(i * mm, 0, i * mm, H)
        for j in range(0, 211, 10):
            c.line(0, j * mm, W, j * mm)
        c.setStrokeColorRGB(*BRANCO)
        c.setLineWidth(0.8)
        c.rect(6 * mm, 6 * mm, W - 12 * mm, H - 12 * mm)
        # carimbo
        x0, y0, bw, bh = 191, 6, 100, 13
        c.setFillColorRGB(*BG)
        c.rect(x0 * mm, y0 * mm, bw * mm, bh * mm, stroke=1, fill=1)
        c.line((x0 + 72) * mm, y0 * mm, (x0 + 72) * mm, (y0 + bh) * mm)
        c.line(x0 * mm, (y0 + 6.5) * mm, (x0 + 72) * mm, (y0 + 6.5) * mm)
        self.txt(x0 + 2, y0 + 8.4, "MANUAL DE MONTAGEM — VOLANTE P1", 7, bold=True)
        self.txt(x0 + 2, y0 + 2, f"{titulo_curto}", 6.5, cor=FRACO)
        self.txt(x0 + 86, y0 + 7.5, f"FOLHA {self.pag}/{self.total}", 7.5, bold=True, al="c")
        self.txt(x0 + 86, y0 + 2.5, REV, 6.5, cor=FRACO, al="c")

    def txt(self, x, y, s, size=8, cor=BRANCO, bold=False, al="l", fonte=None):
        c = self.c
        c.setFillColorRGB(*cor)
        c.setFont(fonte or ("Helvetica-Bold" if bold else "Helvetica"), size)
        {"l": c.drawString, "c": c.drawCentredString, "r": c.drawRightString}[al](x * mm, y * mm, s)

    def paragrafo(self, x, y, largura, s, size=8, cor=BRANCO, bold=False, entre=1.25):
        fonte = "Helvetica-Bold" if bold else "Helvetica"
        linhas = simpleSplit(s, fonte, size, largura * mm)
        for i, l in enumerate(linhas):
            self.txt(x, y - i * size * entre * 0.3528, l, size, cor, bold)
        return y - len(linhas) * size * entre * 0.3528

    # ---- linhas projetadas
    def polis(self, polis, f, cor, larg=0.55, tracejado=None):
        c = self.c
        c.setStrokeColorRGB(*cor)
        c.setLineWidth(larg)
        c.setLineCap(1)
        c.setLineJoin(1)
        if tracejado:
            c.setDash(*tracejado)
        for p in polis:
            path = c.beginPath()
            path.moveTo(*f(p[0]))
            for q in p[1:]:
                path.lineTo(*f(q))
            c.drawPath(path)
        c.setDash()

    def cena(self, area, direcao, contexto, novas, extras_pts=(), ocultas_novas=False):
        """Desenha contexto (fraco) e peças novas (destaque). Retorna (vista, encaixe)."""
        v = Vista(direcao)
        todas = contexto + novas
        L_all = v.linhas(todas)
        L_new = v.linhas(novas) if novas else []
        lim = caixa_limites(L_all, [v.ponto(p) for p in extras_pts])
        x, y, w, h = area
        f = Encaixe(lim, x * mm, y * mm, w * mm, h * mm)
        if contexto and novas:
            self.polis(L_all, f, FRACO, 0.4)
            self.polis(L_new, f, NOVO, 0.75)
        else:
            self.polis(L_all, f, NOVO if novas else BRANCO, 0.6)
        if ocultas_novas and novas:
            self.polis(v.linhas(novas, ocultas=True), f, NOVO, 0.3, (1.2, 1.2))
        return v, f

    def balao(self, v, f, p3, letra, dx, dy, cor=BRANCO):
        """Balão com letra da peça, deslocado (dx, dy) mm na folha a partir do ponto."""
        c = self.c
        px, py = f(v.ponto(p3))
        bx, by = px + dx * mm, py + dy * mm
        c.setStrokeColorRGB(*cor)
        c.setLineWidth(0.4)
        c.line(px, py, bx, by)
        c.setFillColorRGB(*cor)
        c.circle(px, py, 0.6 * mm, stroke=0, fill=1)
        c.setFillColorRGB(*BG)
        c.circle(bx, by, 3.4 * mm, stroke=1, fill=1)
        c.setFillColorRGB(*cor)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(bx, by - 1.1 * mm, letra)

    def seta(self, v, f, p_de, p_para, cor=NOVO):
        c = self.c
        a = f(v.ponto(p_de))
        b = f(v.ponto(p_para))
        c.setStrokeColorRGB(*cor)
        c.setLineWidth(0.5)
        c.setDash(2.2, 1.6)
        c.line(*a, *b)
        c.setDash()
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        L = 2.6 * mm
        c.setFillColorRGB(*cor)
        p = c.beginPath()
        p.moveTo(*b)
        p.lineTo(b[0] - L * math.cos(ang - 0.4), b[1] - L * math.sin(ang - 0.4))
        p.lineTo(b[0] - L * math.cos(ang + 0.4), b[1] - L * math.sin(ang + 0.4))
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    def rotulo(self, v, f, p3, texto, dx, dy, cor=ALERTA, size=7):
        c = self.c
        px, py = f(v.ponto(p3))
        bx, by = px + dx * mm, py + dy * mm
        c.setStrokeColorRGB(*cor)
        c.setLineWidth(0.4)
        c.line(px, py, bx, by)
        c.setFillColorRGB(*cor)
        c.circle(px, py, 0.6 * mm, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", size)
        if dx >= 0:
            c.drawString(bx + 1 * mm, by - 1 * mm, texto)
        else:
            c.drawRightString(bx - 1 * mm, by - 1 * mm, texto)

    # ---- painel lateral de instruções
    def cabecalho_passo(self, n, titulo, tempo):
        self.txt(12, 194, f"PASSO {n:02d}", 18, bold=True)
        self.txt(46, 194, titulo.upper(), 13, bold=True, cor=NOVO)
        self.txt(12, 188, f"tempo estimado: {tempo}", 7.5, cor=FRACO)

    def painel(self, pecas, acoes, atencao=None, confere=None, x=192, y_topo=192, largura=95):
        c = self.c
        c.setFillColorRGB(*PAINEL)
        c.setStrokeColorRGB(*FRACO)
        c.setLineWidth(0.4)
        c.rect((x - 2) * mm, 22 * mm, (largura + 3) * mm, (y_topo - 18) * mm, stroke=1, fill=1)
        y = y_topo - 4
        self.txt(x, y, "PEÇAS DESTE PASSO", 8, bold=True, cor=FRACO)
        y -= 5.5
        for letra, qtd, nome in pecas:
            c.setStrokeColorRGB(*NOVO)
            c.setFillColorRGB(*BG)
            c.setLineWidth(0.5)
            c.circle((x + 3) * mm, (y + 1) * mm, 2.6 * mm, stroke=1, fill=1)
            self.txt(x + 3, y - 0.2, letra, 7.5, cor=NOVO, bold=True, al="c")
            q = f"{qtd}×" if qtd else ""
            self.txt(x + 7.5, y, q, 7.5, bold=True)
            dxq = max(13, 7.5 + self.c.stringWidth(q, "Helvetica-Bold", 7.5) / mm + 2)
            self.paragrafo(x + dxq, y, largura - dxq - 2, nome, 7.5)
            y -= 6
        y -= 2
        self.txt(x, y, "FAÇA", 8, bold=True, cor=FRACO)
        y -= 5
        for i, a in enumerate(acoes, 1):
            c.setFillColorRGB(*BRANCO)
            c.circle((x + 2.2) * mm, (y + 1) * mm, 2.2 * mm, stroke=0, fill=1)
            self.txt(x + 2.2, y + 0.1, str(i), 7, cor=BG, bold=True, al="c")
            y = self.paragrafo(x + 6, y, largura - 8, a, 8) - 2
        if atencao:
            y -= 1
            y = self.caixa_aviso(x, y, largura - 2, "ATENÇÃO", atencao, ALERTA)
        if confere:
            y -= 2
            y = self.caixa_aviso(x, y, largura - 2, "CONFERE ANTES DE SEGUIR", confere, OK)
        return y

    def caixa_aviso(self, x, y, largura, titulo, texto, cor):
        c = self.c
        linhas = simpleSplit(texto, "Helvetica", 7.5, (largura - 5) * mm)
        alt = 6 + len(linhas) * 3.3
        c.setStrokeColorRGB(*cor)
        c.setLineWidth(0.8)
        c.rect(x * mm, (y - alt) * mm, largura * mm, alt * mm, stroke=1, fill=0)
        c.setFillColorRGB(*cor)
        c.rect(x * mm, (y - alt) * mm, 1.6 * mm, alt * mm, stroke=0, fill=1)
        self.txt(x + 3.5, y - 4, titulo, 7.5, cor=cor, bold=True)
        for i, l in enumerate(linhas):
            self.txt(x + 3.5, y - 7.6 - i * 3.3, l, 7.5)
        return y - alt

    def salvar(self):
        self.c.showPage()
        self.c.save()


# ================================================================== páginas
TOTAL = 18


def capa(M):
    M.nova_pagina("Capa")
    c = M.c
    M.txt(14, 186, "VOLANTE DE SIMULAÇÃO", 26, bold=True)
    M.txt(14, 176, "PROTÓTIPO P1 — MANUAL DE MONTAGEM", 14, bold=True, cor=NOVO)
    M.txt(14, 169, "Fórmula · 12 botões · 4 encoders · 2 aletas magnéticas · USB · base Moza R3", 9, cor=FRACO)
    todas = ([A_placa, B_peg, C_peg] + conj_suporte(1) + conj_suporte(-1) + [m.ref_botoes(), m.ref_encoders()])
    M.cena((10, 22, 180, 140), (0.45, 0.35, 1), todas, [])
    y = 160
    M.txt(196, y, "CONTEÚDO", 9, bold=True, cor=FRACO)
    itens = [
        ("2", "Ferramentas e segurança"), ("3–4", "Lista de peças"),
        ("5", "P01 · Insertos roscados"), ("6", "P02 · Conjunto móvel da aleta"),
        ("7", "P03 · Suporte da aleta"), ("8", "P04 · Aleta no suporte"),
        ("9", "P05 · Botões e encoders"), ("10", "P06 · Suportes na placa"),
        ("11", "P07 · Raspberry Pi Pico"), ("12", "P08 · Fiação"),
        ("13", "P09 · Firmware e teste de bancada"), ("14", "P10 · Ajuste das aletas"),
        ("15", "P11 · Pegadas"), ("16", "P12 · Montagem na base"),
        ("17", "Verificação final"), ("18", "Solução de problemas"),
    ]
    for i, (p, t) in enumerate(itens):
        M.txt(196, y - 7 - i * 6, p, 8, bold=True, cor=NOVO)
        M.txt(208, y - 7 - i * 6, t, 8)
    M.paragrafo(14, 30, 170,
                "Como ler este manual: em cada passo, as peças em AZUL-CLARO são as que você "
                "monta agora; as peças em linha fraca já estão montadas. As letras nos balões "
                "correspondem à lista de peças. Setas tracejadas mostram o caminho de montagem.",
                8, cor=FRACO)


def ferramentas(M):
    M.nova_pagina("Ferramentas e segurança")
    M.txt(12, 194, "ANTES DE COMEÇAR", 18, bold=True)
    M.txt(12, 188, "Separe tudo na bancada. Tempo total de montagem: cerca de 5 horas.", 8, cor=FRACO)
    colunas = [
        ("MECÂNICA", [
            "Jogo de chaves Allen 2 / 2,5 / 3 / 4 mm",
            "Chave de fenda Phillips pequena",
            "Macho de rosca M8 com desandador",
            "Paquímetro",
            "Lixa grão 400 e lima pequena",
            "Cartão de visita (≈ 0,3 mm) — calibre de folga",
            "Balança de bagagem ou dinamômetro (até 5 kg)",
        ]),
        ("ELETRÔNICA", [
            "Ferro de solda 40–60 W com ponta cônica",
            "Ponta para insertos (ou ponta cônica velha)",
            "Estanho 0,8 mm com fluxo",
            "Fio flexível 26 AWG em 4 cores",
            "Tubo termo-retrátil 2 mm",
            "Alicate de corte e desencapador",
            "Multímetro",
        ]),
        ("CONSUMÍVEIS", [
            "Cola epóxi 5 minutos",
            "Cola cianoacrilato (super cola)",
            "Fita dupla face VHB 1 mm",
            "Abraçadeiras de nylon pequenas",
            "Trava-rosca média (azul)",
            "Cabo USB com dados (micro-USB)",
            "Computador com Windows e Arduino IDE",
        ]),
    ]
    for k, (titulo, itens) in enumerate(colunas):
        x = 12 + k * 62
        M.txt(x, 174, titulo, 9, bold=True, cor=NOVO)
        for i, t in enumerate(itens):
            M.c.setStrokeColorRGB(*BRANCO)
            M.c.rect(x * mm, (166.6 - i * 7.5) * mm, 3 * mm, 3 * mm)
            M.paragrafo(x + 5, 167.2 - i * 7.5, 55, t, 8)
    y = 100
    M.caixa_aviso(12, y, 175, "SEGURANÇA — ÍMÃS DE NEODÍMIO",
                  "Ímãs N52 se atraem com muita força e podem beliscar a pele ou quebrar ao bater um "
                  "no outro. Mantenha-os separados, longe de cartões, celulares e marca-passos.", ALERTA)
    M.caixa_aviso(12, y - 20, 175, "SEGURANÇA — CALOR",
                  "A ponta do ferro e os insertos passam de 220 °C. Trabalhe em superfície que não "
                  "derrete, com ventilação para a fumaça da solda.", ALERTA)
    M.caixa_aviso(12, y - 40, 175, "REGRA DE OURO",
                  "Não aperte nada com força em plástico impresso. Parafuso em peça impressa é "
                  "\"encostou, mais um quarto de volta\". Rosca espanada no plástico não tem conserto fácil.", OK)
    M.txt(196, 174, "SEQUÊNCIA", 9, bold=True, cor=NOVO)
    seq = ["Preparar peças impressas", "Montar as duas aletas", "Botões e encoders",
           "Aletas na placa", "Eletrônica e fiação", "Teste no Windows",
           "Ajuste fino das aletas", "Pegadas", "Instalar na base"]
    for i, s in enumerate(seq):
        y0 = 165 - i * 14.5
        M.c.setStrokeColorRGB(*NOVO)
        M.c.setFillColorRGB(*BG)
        M.c.rect(196 * mm, (y0 - 4) * mm, 88 * mm, 9 * mm, stroke=1, fill=1)
        M.txt(200, y0 - 0.5, f"{i + 1}", 10, bold=True, cor=NOVO)
        M.txt(208, y0 - 0.5, s, 8.5)
        if i < len(seq) - 1:
            M.c.line(240 * mm, (y0 - 4) * mm, 240 * mm, (y0 - 5.5) * mm)


def bom_fabricadas(M):
    M.nova_pagina("Lista de peças — fabricadas")
    M.txt(12, 194, "LISTA DE PEÇAS · FABRICADAS", 18, bold=True)
    M.txt(12, 188, "Todas impressas em 3D (arquivos STL no pacote CAD rev01).", 8, cor=FRACO)
    itens = [
        ("A", "Placa frontal", "PETG, 5 mm", "1", A_placa, (0.4, 0.3, 1)),
        ("B", "Pegada direita", "PETG", "1", B_peg, (0.7, 0.3, 1)),
        ("C", "Pegada esquerda", "PETG", "1", C_peg, (-0.7, 0.3, 1)),
        ("D", "Suporte da aleta dir.", "PA-CF ou PETG", "1", D_sup, (0.6, 0.5, -1)),
        ("E", "Suporte da aleta esq.", "PA-CF ou PETG", "1", E_sup, (-0.6, 0.5, -1)),
        ("F", "Carregador da aleta", "PA-CF ou PETG", "2", F_car, (0.6, 0.5, -1)),
        ("G", "Chapa da aleta", "PA-CF, 5 mm, 100% preench.", "2", G_chapa, (0.3, 0.4, -1)),
        ("H", "Batente", "TPU 95A", "2", H_bat, (0.6, 0.5, -1)),
    ]
    for i, (L, nome, mat, q, w, d) in enumerate(itens):
        col, lin = i % 4, i // 4
        x, y = 12 + col * 69, 105 - lin * 80
        M.c.setStrokeColorRGB(*FRACO)
        M.c.setLineWidth(0.4)
        M.c.rect(x * mm, y * mm, 65 * mm, 76 * mm)
        v = Vista(d)
        Ls = v.linhas([w])
        f = Encaixe(caixa_limites(Ls), x * mm, (y + 20) * mm, 65 * mm, 52 * mm, margem=0.1)
        M.polis(Ls, f, BRANCO, 0.5)
        M.c.setStrokeColorRGB(*NOVO)
        M.c.setFillColorRGB(*BG)
        M.c.circle((x + 6) * mm, (y + 70) * mm, 3.6 * mm, stroke=1, fill=1)
        M.txt(x + 6, y + 68.8, L, 9, cor=NOVO, bold=True, al="c")
        M.txt(x + 3, y + 13, nome, 8.5, bold=True)
        M.txt(x + 3, y + 8, mat, 7.5, cor=FRACO)
        M.txt(x + 62, y + 3.5, f"QTD {q}", 9, bold=True, cor=NOVO, al="r")
    M.txt(12, 15, "F, G e H são iguais para os dois lados: fabrique 2 de cada. D/E e B/C são espelhadas.",
          7.5, cor=ALERTA)


def bom_compradas(M):
    M.nova_pagina("Lista de peças — compradas")
    M.txt(12, 194, "LISTA DE PEÇAS · COMPRADAS", 18, bold=True)
    M.txt(12, 188, "Componentes de catálogo. Quantidades para o volante completo.", 8, cor=FRACO)
    linhas = [
        ("J", "Eixo de aço Ø4 × 44 mm (pino retificado)", "2", "aletas"),
        ("K", "Bucha de bronze Ø4 × Ø6 × 4 mm", "4", "aletas"),
        ("L", "Ímã de neodímio N52 Ø10 × 5 mm", "2", "retorno da aleta"),
        ("M", "Ímã de neodímio N52 Ø5 × 3 mm", "2", "sensor da aleta"),
        ("N", "Parafuso sem cabeça M8 × 10, ponta plana (aço)", "2", "contraface do ímã"),
        ("P", "Sensor Hall linear SS49E", "2", "aletas"),
        ("Q", "Inserto roscado M3 (instalação a quente)", "8", "carregadores"),
        ("R", "Inserto roscado M4 (instalação a quente)", "8", "pegadas"),
        ("S", "Parafuso M3 × 8 cabeça cilíndrica", "8", "chapa → carregador"),
        ("T", "Parafuso M3 × 12 escareado + porca M3", "4 + 4", "suporte → placa"),
        ("U", "Parafuso M4 × 10 escareado", "8", "placa → pegada"),
        ("V", "Botão de painel Ø16 (×10) e Ø19 (×2), corpo ≤ 25 mm", "12", "B1 a B12"),
        ("W", "Encoder EC11 com clique + knob Ø26", "4", "E1 a E4"),
        ("X", "Raspberry Pi Pico (RP2040) com pinos", "1", "controlador"),
        ("Y", "Diodo 1N4148", "12", "matriz de botões"),
        ("Z", "Parafuso M5 × 12 escareado", "6", "placa → adaptador"),
        ("—", "Adaptador quick release Moza → PCD 70 mm (6 furos M5)", "1", "fixação na base"),
    ]
    xs = [12, 24, 170, 192]
    y = 176
    M.c.setFillColorRGB(*PAINEL)
    M.c.rect(10 * mm, (y - 2) * mm, 228 * mm, 7 * mm, stroke=0, fill=1)
    for x, h in zip(xs, ["", "COMPONENTE", "QTD", "ONDE"]):
        M.txt(x, y, h, 8, bold=True, cor=FRACO)
    for i, (L, nome, q, onde) in enumerate(linhas):
        yy = y - 8 - i * 8.2
        M.c.setStrokeColorRGB(*GRID)
        M.c.line(10 * mm, (yy - 2.6) * mm, 238 * mm, (yy - 2.6) * mm)
        if L != "—":
            M.c.setStrokeColorRGB(*NOVO)
            M.c.setFillColorRGB(*BG)
            M.c.circle((xs[0] + 3) * mm, (yy + 1) * mm, 2.8 * mm, stroke=1, fill=1)
            M.txt(xs[0] + 3, yy - 0.1, L, 7.5, cor=NOVO, bold=True, al="c")
        M.txt(xs[1], yy, nome, 8.5)
        M.txt(xs[2], yy, q, 8.5, bold=True)
        M.txt(xs[3], yy, onde, 8, cor=FRACO)
    M.caixa_aviso(244, 176, 45, "DICA",
                  "Compre 20% a mais de parafusos, insertos e diodos. Peças pequenas somem na bancada.", OK)
    M.caixa_aviso(244, 140, 45, "BOTÕES",
                  "Antes de comprar, confira no anúncio a profundidade do corpo: no máximo 25 mm.",
                  ALERTA)


# ------------------------------------------------------------------ passos
def p01_insertos(M):
    M.nova_pagina("P01 · Insertos roscados")
    M.cabecalho_passo(1, "Insertos roscados", "30 min")
    # carregador, vista por trás
    dz = -14
    novos = [mover(q, dz=dz) for q in Q_ins]
    v, f = M.cena((10, 105, 88, 78), (0.55, 0.5, -1), [F_car], novos)
    for q in Q_ins:
        M.seta(v, f, centro(mover(q, dz=dz)), centro(q))
    M.balao(v, f, centro(F_car), "F", -16, 14)
    M.balao(v, f, centro(novos[0]), "Q", 10, 10, NOVO)
    M.txt(14, 103, "Carregador F — face traseira (4 insertos M3)", 7.5, cor=FRACO)
    # pegada, vista pela frente
    dzr = 14
    novosr = [mover(r, dz=dzr) for r in R_ins]
    v2, f2 = M.cena((96, 28, 92, 155), (0.9, 0.35, 1), [B_peg], novosr)
    for r in R_ins:
        M.seta(v2, f2, centro(mover(r, dz=dzr)), centro(r))
    M.balao(v2, f2, centro(B_peg), "B", 14, -20)
    M.balao(v2, f2, centro(novosr[0]), "R", -14, 6, NOVO)
    M.txt(100, 26, "Pegadas B e C — aba de fixação (4 insertos M4 cada)", 7.5, cor=FRACO)
    # detalhe do inserto
    x0, y0 = 22, 40
    M.txt(14, 92, "COMO INSTALAR UM INSERTO", 8, bold=True, cor=FRACO)
    for k, (titulo, prof) in enumerate([("apoie", 0), ("aqueça e empurre", 3), ("nivelado", 5)]):
        xx = x0 + k * 24
        c = M.c
        c.setStrokeColorRGB(*BRANCO)
        c.setLineWidth(0.5)
        c.rect((xx - 8) * mm, (y0) * mm, 16 * mm, 30 * mm)
        c.setFillColorRGB(*BG)
        c.rect((xx - 2.3) * mm, (y0 + 18) * mm, 4.6 * mm, 12 * mm, stroke=1, fill=1)
        c.setStrokeColorRGB(*NOVO)
        c.setFillColorRGB(*NOVO)
        top = y0 + 30 + 5 - prof
        c.rect((xx - 2.5) * mm, (top - 5) * mm, 5 * mm, 5 * mm, stroke=1, fill=0)
        if k < 2:
            c.setStrokeColorRGB(*ALERTA)
            c.setLineWidth(1.2)
            c.line(xx * mm, top * mm, xx * mm, (top + 9) * mm)
        M.txt(xx, y0 - 5, titulo, 7, al="c")
    M.painel(
        [("Q", "8", "Inserto M3 (4 em cada carregador F)"),
         ("R", "8", "Inserto M4 (4 em cada pegada B e C)"),
         ("F", "2", "Carregador"), ("B/C", "1+1", "Pegadas")],
        ["Ajuste o ferro de solda para 220 °C (PETG) ou 260 °C (PA-CF).",
         "Apoie o inserto no furo, com o lado serrilhado para baixo.",
         "Encoste a ponta do ferro e deixe o inserto descer pelo próprio peso, sem forçar.",
         "Pare quando o inserto ficar nivelado com a superfície. Retire o ferro reto, sem girar.",
         "Repita nos 16 furos e espere 2 minutos para esfriar."],
        atencao="Inserto torto não endireita depois de frio. Se entortar, reaqueça e corrija na hora.",
        confere="Rosqueie um parafuso em cada inserto: deve entrar até o fim com os dedos.")


def p02_conjunto_movel(M):
    M.nova_pagina("P02 · Conjunto móvel da aleta")
    M.cabecalho_passo(2, "Conjunto móvel da aleta", "25 min por aleta")
    off = {
        "K0": (0, -16, 0), "K1": (0, 16, 0), "M": (0, 0, 18), "G": (0, 0, -22),
        "L": (0, 0, -48), "S": (0, 0, -36),
    }
    K0 = mover(K_buchas[0], *off["K0"]); K1 = mover(K_buchas[1], *off["K1"])
    Mm = mover(M_ima, *off["M"]); Gg = mover(G_chapa, *off["G"]); Ll = mover(L_ima, *off["L"])
    Ss = [mover(s, *off["S"]) for s in S_paraf]
    novos = [K0, K1, Mm, Gg, Ll] + Ss
    v, f = M.cena((10, 24, 178, 160), (0.55, 0.75, -0.75), [F_car], novos)
    M.seta(v, f, centro(K0), centro(K_buchas[0]))
    M.seta(v, f, centro(K1), centro(K_buchas[1]))
    M.seta(v, f, centro(Mm), centro(M_ima))
    M.seta(v, f, centro(Ll), centro(Gg))
    M.seta(v, f, centro(Ss[2]), centro(S_paraf[2]))
    M.balao(v, f, centro(F_car), "F", 20, 18)
    M.balao(v, f, centro(K1), "K", -12, 8, NOVO)
    M.balao(v, f, centro(K0), "K", -12, -8, NOVO)
    M.balao(v, f, centro(Mm), "M", 12, 8, NOVO)
    M.balao(v, f, centro(Gg), "G", -18, -10, NOVO)
    M.balao(v, f, centro(Ll), "L", 14, -8, NOVO)
    M.balao(v, f, centro(Ss[0]), "S", -14, -6, NOVO)
    M.painel(
        [("F", "1", "Carregador (com insertos)"), ("K", "2", "Bucha de bronze"),
         ("M", "1", "Ímã Ø5×3 (sensor)"), ("G", "1", "Chapa da aleta"),
         ("S", "4", "Parafuso M3×8"), ("L", "1", "Ímã Ø10×5 (retorno)")],
        ["Prense uma bucha K em cada ponta do furo do carregador. Use uma morsa ou bata leve com um bloco de madeira.",
         "Cole o ímã M no rebaixo da face frontal com uma gota de cianoacrilato.",
         "Encoste a chapa G na face traseira e prenda com 4 parafusos S.",
         "Passe o ímã L pelo furo Ø11 da chapa até encostar no carregador; cole com epóxi.",
         "Repita tudo para a segunda aleta."],
        atencao="O ímã L precisa ficar NIVELADO com a face traseira da chapa. Saliente ou afundado, "
                "a força da aleta muda.",
        confere="Um pino Ø4 passa pelas duas buchas e gira sem prender.")


def p03_suporte(M):
    M.nova_pagina("P03 · Suporte da aleta")
    M.cabecalho_passo(3, "Suporte da aleta", "20 min por lado")
    Pp = mover(P_sensor, dz=-18); Hh = mover(H_bat, dz=-18); Nn = mover(N_paraf, dz=-28)
    v, f = M.cena((10, 24, 178, 160), (0.6, 0.55, -1), [D_sup], [Pp, Hh, Nn])
    M.seta(v, f, centro(Pp), centro(P_sensor))
    M.seta(v, f, centro(Hh), centro(H_bat))
    M.seta(v, f, centro(Nn), centro(N_paraf))
    M.balao(v, f, centro(D_sup), "D", -22, 16)
    M.balao(v, f, centro(Pp), "P", -14, -10, NOVO)
    M.balao(v, f, centro(Hh), "H", 12, -10, NOVO)
    M.balao(v, f, centro(Nn), "N", 14, 6, NOVO)
    M.rotulo(v, f, (m.s_para_x(m.L_SENS), YA, -26), "face marcada do sensor virada para o ímã", 34, -30)
    M.painel(
        [("D", "1", "Suporte direito (E = esquerdo)"), ("P", "1", "Sensor Hall SS49E"),
         ("H", "1", "Batente de TPU"), ("N", "1", "Parafuso M8×10 ponta plana")],
        ["Solde 3 fios de 15 cm no sensor P: vermelho no pino 1 (VCC), preto no 2 (GND), "
         "branco no 3 (saída). Isole com termo-retrátil.",
         "Encaixe o sensor na fenda do braço com a face marcada para fora e fixe com uma gota de epóxi.",
         "Cole o batente H na ponta do braço, sob o sensor.",
         "Abra a rosca M8 no furo da aba traseira com o macho.",
         "Rosqueie o parafuso N por trás, só até a ponta aparecer do outro lado."],
        atencao="Pinos do SS49E vistos pela face marcada, da esquerda para a direita: 1-VCC, 2-GND, 3-SAÍDA.",
        confere="O parafuso N gira com a chave Allen, firme mas sem esforço.")


def p04_aleta_no_suporte(M):
    M.nova_pagina("P04 · Aleta no suporte")
    M.cabecalho_passo(4, "Aleta no suporte", "10 min por lado")
    grupo = grupo_movel(dx=70)
    Jj = mover(J_eixo, dy=55)
    ctx = [D_sup, H_bat, N_paraf, P_sensor]
    v, f = M.cena((10, 24, 178, 160), (0.6, 0.6, -1), ctx, grupo + [Jj])
    M.seta(v, f, centro(grupo[0]), centro(F_car))
    M.seta(v, f, centro(Jj), centro(J_eixo))
    M.balao(v, f, centro(D_sup), "D", -24, -12)
    M.balao(v, f, centro(grupo[1]), "P2", 16, -16, NOVO)
    M.balao(v, f, centro(Jj), "J", -12, 8, NOVO)
    M.painel(
        [("J", "1", "Eixo de aço Ø4×44"),
         ("P2", "1", "Conjunto móvel do passo 2"), ("P3", "1", "Suporte do passo 3")],
        ["Afrouxe o parafuso N até ele recuar dentro da aba.",
         "Deslize o conjunto móvel por fora, encaixando o cubo do carregador entre as duas orelhas do suporte.",
         "Alinhe os furos e passe o eixo J pela orelha de cima, pelas buchas e pela orelha de baixo.",
         "Se o eixo ficar folgado nas orelhas, trave com uma gota de cianoacrilato só nas pontas.",
         "Monte o lado esquerdo do mesmo jeito, com o suporte E."],
        atencao="Não cole o eixo nas buchas: ele precisa girar livre. A cola vai só nas orelhas.",
        confere="Empurrando a ponta da aleta, ela gira até o batente e volta sem raspar em nada.")


def p05_botoes(M):
    M.nova_pagina("P05 · Botões e encoders")
    M.cabecalho_passo(5, "Botões e encoders", "40 min")
    v = Vista((0, 0, 1))
    L = v.linhas([A_placa])
    f = Encaixe(caixa_limites(L), 10 * mm, 24 * mm, 178 * mm, 160 * mm)
    M.polis(L, f, BRANCO, 0.6)
    funcoes = {"B1": "DRS / farol", "B2": "Rádio", "B3": "BB próx.", "B4": "BB ant.",
               "B5": "Limitador", "B6": "Neutro", "B7": "Ignição", "B8": "Overtake",
               "B9": "Limpador", "B10": "Pedir pit", "B11": "Chat", "B12": "Livre"}
    for n, (x, y, d) in m.BOTOES.items():
        px, py = f(v.ponto((x, y, m.T_PLACA)))
        cor = ALERTA if d > 16 else NOVO
        M.c.setStrokeColorRGB(*cor)
        M.c.setLineWidth(1.0)
        M.c.circle(px, py, (d / 2 + 2) * f.s, stroke=1, fill=0)
        M.c.setFillColorRGB(*cor)
        M.c.setFont("Helvetica-Bold", 8)
        M.c.drawCentredString(px, py - 1 * mm, n)
        M.c.setFont("Helvetica", 6)
        M.c.setFillColorRGB(*BRANCO)
        M.c.drawCentredString(px, py - (d / 2 + 4.5) * f.s, funcoes[n])
    func_e = {"E1": "Freio", "E2": "TC / Dif.", "E3": "ABS / ERS", "E4": "Black box"}
    for n, (x, y) in m.ENCODERS.items():
        px, py = f(v.ponto((x, y, m.T_PLACA)))
        M.c.setStrokeColorRGB(*OK)
        M.c.setLineWidth(1.0)
        M.c.setDash(2, 1.5)
        M.c.circle(px, py, 13 * f.s, stroke=1, fill=0)
        M.c.setDash()
        M.c.setFillColorRGB(*OK)
        M.c.setFont("Helvetica-Bold", 8)
        M.c.drawCentredString(px, py - 1 * mm, n)
        M.c.setFont("Helvetica", 6)
        M.c.setFillColorRGB(*BRANCO)
        M.c.drawCentredString(px, py - 15.5 * f.s, func_e[n])
    M.txt(14, 183, "Vista pela FRENTE (lado do piloto)", 7.5, cor=FRACO)
    M.painel(
        [("A", "1", "Placa frontal"), ("V", "12", "Botões (10× Ø16, 2× Ø19)"),
         ("W", "4", "Encoders EC11 + knobs")],
        ["Coloque a placa com a frente para cima, sobre um pano.",
         "Encaixe cada botão pela frente, na posição do desenho, e aperte a porca por trás.",
         "Os dois botões Ø19 (laranja) vão em B5 e B6, nos cantos de cima.",
         "Encaixe os encoders pela frente, com os 3 pinos (A-C-B) voltados para o centro "
         "da placa; aperte a porca e coloque os knobs.",
         "Gire todos os terminais dos botões para o centro da placa: facilita a fiação."],
        atencao="Porca de botão em plástico: aperte com a mão e dê só mais 1/8 de volta com a chave.",
        confere="Nenhum botão gira na placa ao ser apertado; todos os knobs giram livres.")


def p06_suportes_placa(M):
    M.nova_pagina("P06 · Suportes na placa")
    M.cabecalho_passo(6, "Aletas na placa", "15 min")
    dz = -45
    dir_ = conj_suporte(1, dz=dz)
    esq_ = conj_suporte(-1, dz=dz)
    paraf = [mover(t, dz=25) for t in T_paraf] + [m.espelhar(mover(t, dz=25)) for t in T_paraf]
    porcas = [mover(t, dz=dz - 2) for t in T_porca] + [m.espelhar(mover(t, dz=dz - 2)) for t in T_porca]
    ctx = [A_placa, m.ref_botoes(), m.ref_encoders()]
    v, f = M.cena((10, 24, 178, 160), (0.35, 0.55, -1), ctx, dir_ + esq_ + paraf + porcas)
    M.seta(v, f, centro(dir_[0]), centro(D_sup))
    M.seta(v, f, centro(esq_[0]), centro(E_sup))
    M.balao(v, f, centro(dir_[0]), "D", -14, 14, NOVO)
    M.balao(v, f, centro(esq_[0]), "E", 14, 14, NOVO)
    M.balao(v, f, centro(paraf[0]), "T", 12, -10, NOVO)
    M.balao(v, f, centro(A_placa), "A", 0, -40)
    M.txt(14, 183, "Vista por TRÁS", 7.5, cor=FRACO)
    M.painel(
        [("D/E", "1+1", "Aletas montadas nos suportes"),
         ("T", "4+4", "Parafuso M3×12 escareado + porca")],
        ["Vire a placa com a traseira para cima.",
         "Posicione o suporte D (aleta direita) à DIREITA de quem olha a placa pela frente, "
         "com o braço do sensor para fora.",
         "Passe 2 parafusos T pela frente da placa e aperte as porcas por trás.",
         "Repita com o suporte E do lado esquerdo."],
        atencao="Pela traseira, direita e esquerda se invertem. Confira olhando pela frente antes de apertar.",
        confere="As duas aletas giram livres e nenhuma encosta nos corpos dos botões B1 a B4.")


def p07_pico(M):
    M.nova_pagina("P07 · Raspberry Pi Pico")
    M.cabecalho_passo(7, "Raspberry Pi Pico", "10 min")
    ctx = [A_placa, m.ref_botoes(), m.ref_encoders()] + conj_suporte(1) + conj_suporte(-1)
    v, f = M.cena((10, 24, 178, 160), (0, 0, -1), ctx, [PICO])
    M.balao(v, f, centro(PICO), "X", 0, 22, NOVO)
    M.rotulo(v, f, (25.5, 66, -2), "conector USB", 18, 14, OK)
    M.rotulo(v, f, (0, -5, -1), "área do adaptador da base: manter livre (Ø90)", -30, -40, ALERTA)
    M.c.setStrokeColorRGB(*ALERTA)
    M.c.setDash(2, 1.5)
    cx, cy = f(v.ponto((0, -5, 0)))
    M.c.circle(cx, cy, 45 * f.s, stroke=1, fill=0)
    M.c.setDash()
    M.txt(14, 183, "Vista por TRÁS — o lado direito do desenho é a ESQUERDA do piloto", 7.5, cor=FRACO)
    M.painel(
        [("X", "1", "Raspberry Pi Pico"), ("—", "1", "Fita VHB 20 × 50 mm")],
        ["Grave o firmware no Pico ANTES de colar (passo 9, item 1). É mais fácil testar solto.",
         "Limpe a área com álcool.",
         "Cole o Pico com fita VHB na área livre acima do centro, com os componentes para cima "
         "e o conector USB apontando para a direita do piloto.",
         "Deixe pelo menos 10 mm livres em volta do conector para o cabo."],
        atencao="Não cole nada dentro do círculo do adaptador: ali a placa encosta no quick release.",
        confere="O botão BOOTSEL e o conector USB continuam acessíveis.")


def p08_fiacao(M):
    M.nova_pagina("P08 · Fiação")
    M.cabecalho_passo(8, "Fiação", "90 min")
    c = M.c
    # Pico
    px, py, pw, ph = 112, 40, 26, 140
    c.setStrokeColorRGB(*BRANCO)
    c.setLineWidth(0.8)
    c.setFillColorRGB(*PAINEL)
    c.rect(px * mm, py * mm, pw * mm, ph * mm, stroke=1, fill=1)
    M.txt(px + pw / 2, py + ph + 3, "RASPBERRY PI PICO", 8, bold=True, al="c")
    esq = [("GP2", 4), ("GP3", 5), ("GP4", 6), ("GP5", 7), ("GP6", 9), ("GP7", 10), ("GP8", 11),
           ("GND", 13), ("GP10", 14), ("GP11", 15), ("GP12", 16), ("GP13", 17), ("GP14", 19),
           ("GP15", 20), ("GP16", 21), ("GP17", 22)]
    dir_ = [("GP26", 31), ("GP27", 32), ("AGND", 33), ("3V3", 36)]
    pos = {}
    for i, (n, pino) in enumerate(esq):
        y = py + ph - 8 - i * 8.2
        pos[n] = (px, y)
        c.setFillColorRGB(*BRANCO)
        c.circle(px * mm, y * mm, 0.9 * mm, stroke=0, fill=1)
        M.txt(px + 2, y - 1, f"{n}", 7, bold=True)
        M.txt(px + pw - 2, y - 1, f"p{pino}", 6, cor=FRACO, al="r")
    for i, (n, pino) in enumerate(dir_):
        y = py + ph - 8 - i * 8.2
        pos[n] = (px + pw, y)
        c.setFillColorRGB(*BRANCO)
        c.circle((px + pw) * mm, y * mm, 0.9 * mm, stroke=0, fill=1)
        M.txt(px + pw - 2, y - 1, n, 7, bold=True, al="r")

    # matriz 4x3
    mx, my = 20, 112
    linhas = ["GP2", "GP3", "GP4", "GP5"]
    colunas = ["GP6", "GP7", "GP8"]
    M.txt(mx, my + 66, "MATRIZ DE BOTÕES 4 × 3", 8, bold=True, cor=NOVO)
    for r in range(4):
        yr = my + 50 - r * 15
        c.setStrokeColorRGB(*NOVO)
        c.setLineWidth(0.7)
        c.line(mx * mm, yr * mm, (mx + 72) * mm, yr * mm)
        M.txt(mx - 2, yr - 1, f"L{r + 1}", 7, bold=True, al="r", cor=NOVO)
        # liga linha ao pico
        c.line((mx + 72) * mm, yr * mm, (mx + 78 + r * 2) * mm, yr * mm)
        c.line((mx + 78 + r * 2) * mm, yr * mm, (mx + 78 + r * 2) * mm, pos[linhas[r]][1] * mm)
        c.line((mx + 78 + r * 2) * mm, pos[linhas[r]][1] * mm, px * mm, pos[linhas[r]][1] * mm)
    for k in range(3):
        xc = mx + 12 + k * 22
        c.setStrokeColorRGB(*ALERTA)
        c.line(xc * mm, (my + 58) * mm, xc * mm, (my + 2) * mm)
        M.txt(xc, my + 60, f"C{k + 1}", 7, bold=True, al="c", cor=ALERTA)
        yb = my + 2 - 4 - k * 4
        c.line(xc * mm, (my + 2) * mm, xc * mm, yb * mm)
        c.line(xc * mm, yb * mm, (mx + 86 + k * 2) * mm, yb * mm)
        c.line((mx + 86 + k * 2) * mm, yb * mm, (mx + 86 + k * 2) * mm, pos[colunas[k]][1] * mm)
        c.line((mx + 86 + k * 2) * mm, pos[colunas[k]][1] * mm, px * mm, pos[colunas[k]][1] * mm)
        for r in range(4):
            yr = my + 50 - r * 15
            # botão + diodo entre coluna e linha
            bx = xc + 7
            c.setStrokeColorRGB(*BRANCO)
            c.setLineWidth(0.5)
            c.line(xc * mm, (yr + 6) * mm, bx * mm, (yr + 6) * mm)
            c.circle(bx * mm, (yr + 6) * mm, 0.6 * mm)
            c.line(bx * mm, (yr + 6) * mm, (bx + 3) * mm, (yr + 7.6) * mm)
            c.circle((bx + 3.5) * mm, (yr + 6) * mm, 0.6 * mm)
            # diodo apontando para a linha
            dx0 = bx + 3.5
            c.line(dx0 * mm, (yr + 6) * mm, dx0 * mm, (yr + 4) * mm)
            p = c.beginPath()
            p.moveTo((dx0 - 1.3) * mm, (yr + 4) * mm)
            p.lineTo((dx0 + 1.3) * mm, (yr + 4) * mm)
            p.lineTo(dx0 * mm, (yr + 2) * mm)
            p.close()
            c.setFillColorRGB(*BRANCO)
            c.drawPath(p, stroke=0, fill=1)
            c.line((dx0 - 1.3) * mm, (yr + 2) * mm, (dx0 + 1.3) * mm, (yr + 2) * mm)
            c.line(dx0 * mm, (yr + 2) * mm, dx0 * mm, yr * mm)
            M.txt(bx - 1, yr + 9, f"B{r * 3 + k + 1}", 6.5, bold=True)
    M.txt(mx, my - 18, "faixa do diodo (catodo) sempre do lado da LINHA", 7, cor=ALERTA)

    # encoders
    ex, ey = 20, 52
    M.txt(ex, ey + 32, "ENCODERS (pinos A · C · B)", 8, bold=True, cor=OK)
    enc_pinos = [("E1", "GP10", "GP11"), ("E2", "GP12", "GP13"), ("E3", "GP14", "GP15"), ("E4", "GP16", "GP17")]
    for i, (n, a, b) in enumerate(enc_pinos):
        xe = ex + i * 21
        c.setStrokeColorRGB(*OK)
        c.setLineWidth(0.6)
        c.rect(xe * mm, ey * mm, 14 * mm, 14 * mm)
        M.txt(xe + 7, ey + 16, n, 7, bold=True, al="c", cor=OK)
        for j, lab in enumerate(["A", "C", "B"]):
            xp = xe + 2.5 + j * 4.5
            c.line(xp * mm, ey * mm, xp * mm, (ey - 3) * mm)
            M.txt(xp, ey - 6, lab, 6, al="c")
        for j, gp in ((0, a), (2, b)):
            xp = xe + 2.5 + j * 4.5
            yy = ey - 9 - j * 1.2 - i * 0.6
            c.setStrokeColorRGB(*OK)
            c.line(xp * mm, (ey - 7.5) * mm, xp * mm, yy * mm)
            tx = px - 4 - i * 2 - j * 0.6
            c.line(xp * mm, yy * mm, tx * mm, yy * mm)
            c.line(tx * mm, yy * mm, tx * mm, pos[gp][1] * mm)
            c.line(tx * mm, pos[gp][1] * mm, px * mm, pos[gp][1] * mm)
        M.txt(xe + 7, ey - 22, "C → GND", 6, al="c", cor=FRACO)
    # halls
    hx, hy = 152, 118
    M.txt(hx - 8, hy + 16, "SENSORES DAS ALETAS", 8, bold=True, cor=NOVO)
    for i, (lado, gp) in enumerate([("esquerda", "GP26"), ("direita", "GP27")]):
        yy = hy - i * 22
        c.setStrokeColorRGB(*NOVO)
        c.rect(hx * mm, yy * mm, 12 * mm, 8 * mm)
        M.txt(hx + 6, yy + 3, "SS49E", 6, al="c")
        M.txt(hx + 6, yy - 4, f"aleta {lado}", 7, al="c")
        for j, (lab, alvo) in enumerate([("1 VCC", "3V3"), ("2 GND", "AGND"), ("3 OUT", gp)]):
            ypin = yy + 6.5 - j * 2.5
            c.line(hx * mm, ypin * mm, (hx - 4 - j * 1.5 - i * 5) * mm, ypin * mm)
            xr = hx - 4 - j * 1.5 - i * 5
            c.line(xr * mm, ypin * mm, xr * mm, pos[alvo][1] * mm)
            c.line(xr * mm, pos[alvo][1] * mm, (px + pw) * mm, pos[alvo][1] * mm)
    M.painel(
        [("Y", "12", "Diodo 1N4148"), ("—", "", "Fio 26 AWG: azul = linhas, laranja = colunas, "
                                       "verde = encoders, branco = sensores")],
        ["Solde um diodo em um terminal de cada botão, com a faixa voltada para a LINHA.",
         "Ligue as linhas L1–L4: um fio passa pelos diodos dos 3 botões da mesma linha.",
         "Ligue as colunas C1–C3: um fio passa pelo outro terminal dos 4 botões da coluna.",
         "Encoders: pino C de todos no GND do Pico; A e B nos GPs indicados.",
         "Sensores: VCC no 3V3 (pino 36), GND no AGND (pino 33), saída no GP26 / GP27.",
         "Prenda os fios na placa com abraçadeiras, longe do eixo das aletas."],
        atencao="Antes de ligar o USB, meça com o multímetro: 3V3 e GND não podem estar em curto.",
        confere="Cada fio está identificado e nenhum passa no caminho das aletas.", largura=95)


def p09_firmware(M):
    M.nova_pagina("P09 · Firmware e teste")
    M.cabecalho_passo(9, "Firmware e teste de bancada", "30 min")
    c = M.c
    # janela simulada do Windows
    x0, y0, w0, h0 = 14, 70, 110, 105
    c.setFillColorRGB(*PAINEL)
    c.setStrokeColorRGB(*BRANCO)
    c.setLineWidth(0.7)
    c.rect(x0 * mm, y0 * mm, w0 * mm, h0 * mm, stroke=1, fill=1)
    c.rect(x0 * mm, (y0 + h0 - 7) * mm, w0 * mm, 7 * mm, stroke=1, fill=0)
    M.txt(x0 + 3, y0 + h0 - 5, "Propriedades de Pico — Testar", 7.5, bold=True)
    M.txt(x0 + 4, y0 + h0 - 13, "Botões", 7.5, cor=FRACO)
    for i in range(22):
        r, k = i // 8, i % 8
        bx, by = x0 + 8 + k * 12.5, y0 + h0 - 22 - r * 13
        acesos = {0, 12, 20}
        c.setStrokeColorRGB(*BRANCO)
        c.setFillColorRGB(*(NOVO if i in acesos else BG))
        c.circle(bx * mm, by * mm, 4 * mm, stroke=1, fill=1)
        M.txt(bx, by - 1.2, str(i + 1), 7, cor=BG if i in acesos else BRANCO, bold=True, al="c")
    M.txt(x0 + 4, y0 + 22, "Botão aceso = entrada recebida. Exemplo: B1 (1),", 7.5)
    M.txt(x0 + 4, y0 + 17, "E1 girado (13) e aleta esquerda puxada (21).", 7.5)
    # tabela mapa
    tx, ty = 132, 175
    M.txt(tx, ty, "MAPA DE BOTÕES", 8, bold=True, cor=FRACO)
    mapa = [("1–12", "B1 a B12"), ("13 / 14", "E1 horário / anti"), ("15 / 16", "E2 horário / anti"),
            ("17 / 18", "E3 horário / anti"), ("19 / 20", "E4 horário / anti"),
            ("21", "Aleta esquerda (descer)"), ("22", "Aleta direita (subir)")]
    for i, (a, b) in enumerate(mapa):
        yy = ty - 7 - i * 6.5
        c.setStrokeColorRGB(*GRID)
        c.line(tx * mm, (yy - 2) * mm, (tx + 55) * mm, (yy - 2) * mm)
        M.txt(tx, yy, a, 8, bold=True, cor=NOVO)
        M.txt(tx + 16, yy, b, 8)
    M.caixa_aviso(132, 112, 55, "ENCODER AO CONTRÁRIO?",
                  "Troque false por true no item correspondente de ENC_INVERT no firmware e grave de novo.", ALERTA)
    M.caixa_aviso(14, 62, 110, "ARDUINO IDE",
                  "Gerenciador de placas: \"Raspberry Pi Pico/RP2040\" (Earle Philhower). "
                  "Placa: Raspberry Pi Pico. Ferramentas > USB Stack: \"Pico SDK\".", OK)
    M.painel(
        [("X", "1", "Pico com a fiação pronta"), ("—", "1", "Cabo USB com dados")],
        ["Segure o BOOTSEL, conecte o USB e solte: o Pico aparece como pendrive. "
         "Grave o volante_mvp.ino pela Arduino IDE.",
         "No Windows, abra \"Configurar controladores de jogo USB\" > Pico > Propriedades.",
         "Aperte B1 a B12 um por um e confira o número aceso com o mapa.",
         "Gire cada encoder um clique para cada lado: deve piscar o botão do par.",
         "Ligue o USB com as aletas soltas. Depois puxe cada aleta até o batente uma vez para calibrar."],
        atencao="A calibração das aletas acontece a cada vez que o USB é conectado. Nunca conecte "
                "com uma aleta puxada.",
        confere="Os 22 botões acendem certo, sem nenhum aceso sozinho.")


def p10_ajuste(M):
    M.nova_pagina("P10 · Ajuste das aletas")
    M.cabecalho_passo(10, "Ajuste fino das aletas", "15 min")
    c = M.c
    # detalhe ampliado: chapa + ímã + parafuso (vista de cima, 3,5:1)
    K = 3.5
    ox, oy = 40, 118

    def R(x0, z0, x1, z1, cor, fill=None, larg=0.7):
        c.setStrokeColorRGB(*cor)
        c.setLineWidth(larg)
        if fill:
            c.setFillColorRGB(*fill)
        c.rect((ox + K * x0) * mm, (oy + K * z0) * mm, K * (x1 - x0) * mm, K * (z1 - z0) * mm,
               stroke=1, fill=1 if fill else 0)
    M.txt(14, 183, "DETALHE DA FOLGA — ESCALA 3,5:1 (vista de cima, aleta em repouso)", 7.5, cor=FRACO)
    R(0, 5, 30, 13, FRACO)                                  # carregador (parcial)
    R(0, 0, 30, 5, BRANCO, fill=PAINEL)                     # chapa 5 mm
    R(10, -0.0, 20, 5.0, NOVO, fill=NOVO)                   # ímã L Ø10×5 (nivelado com a chapa)
    R(4, -12, 26, -5, BRANCO)                               # aba do suporte
    R(11, -12.8, 19, -0.3, BRANCO, fill=(0.35, 0.45, 0.6))  # parafuso N
    M.txt(ox + K * 31, oy + K * 8.5, "carregador F", 7.5)
    M.txt(ox + K * 31, oy + K * 2.0, "chapa G (5 mm)", 7.5)
    M.txt(ox + K * 27, oy + K * -9, "aba do suporte D", 7.5)
    M.txt(ox - 2, oy + K * 2.0, "ímã L", 7.5, cor=NOVO, bold=True, al="r")
    M.txt(ox - 2, oy + K * -7, "parafuso N", 7.5, al="r")
    M.txt(ox - 2, oy + K * -9.5, "(chave Allen por trás)", 6.5, cor=FRACO, al="r")
    # chamada da folga
    c.setStrokeColorRGB(*ALERTA)
    c.setLineWidth(0.8)
    gx, gy = ox + K * 20, oy + K * -0.15
    c.circle(gx * mm, gy * mm, 3.5 * mm, stroke=1, fill=0)
    c.line((gx + 3.5) * mm, gy * mm, (gx + 22) * mm, (gy - 12) * mm)
    M.txt(gx + 23, gy - 13, "FOLGA 0,3 mm", 9, bold=True, cor=ALERTA)
    M.txt(gx + 23, gy - 17, "entre o ímã e a ponta do parafuso", 7, cor=ALERTA)
    # seta do puxão
    c.setStrokeColorRGB(*OK)
    c.setLineWidth(1.2)
    xa = ox + K * 15
    c.line(xa * mm, (oy + K * 13.5) * mm, xa * mm, (oy + K * 13.5 + 12) * mm)
    p = c.beginPath()
    p.moveTo(xa * mm, (oy + K * 13.5 + 14) * mm)
    p.lineTo((xa - 1.6) * mm, (oy + K * 13.5 + 10.5) * mm)
    p.lineTo((xa + 1.6) * mm, (oy + K * 13.5 + 10.5) * mm)
    p.close()
    c.setFillColorRGB(*OK)
    c.drawPath(p, stroke=0, fill=1)
    M.txt(xa + 3, oy + K * 13.5 + 8, "ao puxar, a aleta vem para este lado (piloto)", 7, cor=OK)
    # calibre improvisado
    M.txt(14, 58, "CALIBRE IMPROVISADO", 8, bold=True, cor=FRACO)
    for i, (t, e) in enumerate([("cartão de visita", "≈ 0,3 mm"), ("3 folhas de papel A4", "≈ 0,3 mm"),
                                ("1 folha de papel A4", "≈ 0,1 mm")]):
        c.setStrokeColorRGB(*BRANCO)
        c.setLineWidth(0.5)
        c.rect(14 * mm, (48 - i * 8) * mm, 18 * mm, 5 * mm)
        M.txt(36, 49.5 - i * 8, t, 8)
        M.txt(82, 49.5 - i * 8, e, 8, bold=True, cor=NOVO)
    # medição de força
    M.txt(112, 58, "MEDIR A FORÇA", 8, bold=True, cor=FRACO)
    c.setStrokeColorRGB(*BRANCO)
    c.setLineWidth(0.6)
    c.rect(112 * mm, 30 * mm, 60 * mm, 6 * mm)
    M.txt(132, 32, "aleta (vista de trás)", 7, al="c")
    c.circle(160 * mm, 33 * mm, 1.2 * mm)
    c.setStrokeColorRGB(*NOVO)
    c.line(160 * mm, 34.2 * mm, 160 * mm, 44 * mm)
    c.rect(154 * mm, 44 * mm, 12 * mm, 9 * mm)
    M.txt(160, 47, "kg", 8, bold=True, cor=NOVO, al="c")
    M.txt(168, 48, "balança", 7)
    M.txt(112, 25, "laço de linha a 70 mm do eixo (zona do dedo)", 7, cor=FRACO)
    M.painel(
        [("—", "1", "Cartão de visita"), ("—", "1", "Balança de bagagem"),
         ("—", "1", "Chave Allen 4 mm")],
        ["Com a aleta solta, avance o parafuso N até encostar no ímã L.",
         "Coloque o cartão entre os dois e recue o parafuso até o cartão sair justo.",
         "Passe um laço de linha na aleta, a 70 mm do eixo, e puxe com a balança na direção do piloto.",
         "Leia o pico no momento do clique. Alvo: 0,6 a 0,9 kg.",
         "Mais pesado: recue o parafuso. Mais leve: avance. Ajuste em 1/8 de volta.",
         "Achou o ponto: uma gota de trava-rosca no parafuso."],
        atencao="O parafuso NUNCA pode encostar no ímã com a aleta em repouso: o clique some e o ímã pode trincar.",
        confere="As duas aletas têm a mesma força (diferença menor que 0,1 kg) e o clique é seco.")


def p11_pegadas(M):
    M.nova_pagina("P11 · Pegadas")
    M.cabecalho_passo(11, "Pegadas", "10 min")
    ctx = [A_placa, m.ref_botoes(), m.ref_encoders()] + conj_suporte(1) + conj_suporte(-1)
    Bb = mover(B_peg, dx=45)
    Cc = mover(C_peg, dx=-45)
    paraf = [mover(u, dz=28) for u in U_paraf] + [m.espelhar(mover(u, dz=28)) for u in U_paraf]
    v, f = M.cena((10, 24, 178, 160), (0.35, 0.3, 1), ctx, [Bb, Cc] + paraf)
    M.seta(v, f, centro(Bb), centro(B_peg))
    M.seta(v, f, centro(Cc), centro(C_peg))
    M.seta(v, f, centro(paraf[0]), centro(U_paraf[0]))
    M.balao(v, f, centro(Bb), "B", 14, 22, NOVO)
    M.balao(v, f, centro(Cc), "C", -14, 22, NOVO)
    M.balao(v, f, centro(paraf[1]), "U", 16, 4, NOVO)
    M.painel(
        [("B", "1", "Pegada direita"), ("C", "1", "Pegada esquerda"),
         ("U", "8", "Parafuso M4×10 escareado")],
        ["Vire a placa com a frente para cima.",
         "Deslize a pegada B pela lateral direita: a aba entra atrás da placa e o degrau abraça a borda.",
         "Prenda com 4 parafusos U pela frente da placa, de cima para baixo.",
         "Repita com a pegada C do lado esquerdo."],
        atencao="Aperte os 4 parafusos de cada pegada em cruz, aos poucos, para a aba não empenar.",
        confere="Os dedos alcançam as aletas por trás da pegada e o polegar alcança E1/E2 sem soltar a mão.")


def p12_base(M):
    M.nova_pagina("P12 · Montagem na base")
    M.cabecalho_passo(12, "Montagem na base", "15 min")
    ctx = [A_placa, B_peg, C_peg, m.ref_botoes(), m.ref_encoders()] + conj_suporte(1) + conj_suporte(-1)
    ad = mover(ADAPT, dz=-45)
    base = mover(caixa(-45, 45, -55, 40, -140, -40).union(cil_z(0, -5, -40, 60, 25)), dz=-60)
    paraf = [mover(z, dz=30) for z in Z_paraf]
    v, f = M.cena((10, 24, 178, 160), (1, 0.45, 0.55), ctx + [base], [ad] + paraf)
    M.seta(v, f, centro(ad), centro(ADAPT))
    M.seta(v, f, centro(paraf[0]), centro(Z_paraf[0]))
    M.rotulo(v, f, centro(ad), "adaptador quick release", 30, -14, NOVO)
    M.balao(v, f, centro(paraf[0]), "Z", 14, 10, NOVO)
    M.rotulo(v, f, centro(base), "base Moza R3", 20, -20, FRACO)
    M.painel(
        [("Z", "6", "Parafuso M5×12 escareado"), ("—", "1", "Adaptador quick release PCD 70")],
        ["Encoste o adaptador na traseira da placa, alinhando os 6 furos.",
         "Passe os 6 parafusos Z pela frente e aperte em estrela, com trava-rosca.",
         "Encaixe o volante no quick release da base.",
         "Passe o cabo USB com uma volta frouxa em torno do eixo e prenda-o na base.",
         "No Pit House, limite o ângulo de giro a 540° ou menos."],
        atencao="A base R3 gira sem limite e o cabo não. Sem limitar o ângulo no Pit House, "
                "o cabo enrola e arranca o conector.",
        confere="Gire o volante de batente a batente: o cabo acompanha sem esticar.")


def verificacao(M):
    M.nova_pagina("Verificação final")
    M.txt(12, 194, "VERIFICAÇÃO FINAL", 18, bold=True)
    M.txt(12, 188, "Marque cada item antes da primeira corrida.", 8, cor=FRACO)
    grupos = [
        ("MECÂNICA", ["Todos os parafusos apertados (placa, pegadas, suportes, adaptador)",
                      "Aletas giram livres e voltam sozinhas ao soltar",
                      "Clique das duas aletas igual (0,6 a 0,9 kg)",
                      "Nenhuma folga entre volante e quick release",
                      "Massa total abaixo de 1,0 kg (pesar sem a base)"]),
        ("ELETRÔNICA", ["Nenhum fio encosta nas aletas em todo o curso",
                        "Pico firme na fita VHB",
                        "Cabo USB com folga em todo o giro",
                        "Os 22 botões aparecem certos no Windows"]),
        ("SIMULADOR", ["iRacing: marchas nos botões 21 e 22",
                       "Encoders: balanço de freio, TC e ABS mapeados (+ e −)",
                       "Limitador, neutro e ignição testados com o carro parado",
                       "Uma volta completa sem tirar as mãos do volante"]),
    ]
    y = 176
    for titulo, itens in grupos:
        M.txt(14, y, titulo, 10, bold=True, cor=NOVO)
        y -= 7
        for it in itens:
            M.c.setStrokeColorRGB(*BRANCO)
            M.c.setLineWidth(0.6)
            M.c.rect(16 * mm, (y - 0.8) * mm, 4 * mm, 4 * mm)
            M.txt(24, y, it, 9)
            y -= 7.5
        y -= 4
    M.caixa_aviso(196, 176, 92, "QUANDO TUDO ESTIVER MARCADO",
                  "Anote a força medida das aletas e qualquer ajuste feito. Esses dados entram na "
                  "revisão rev01 do projeto.", OK)


def problemas(M):
    M.nova_pagina("Solução de problemas")
    M.txt(12, 194, "SOLUÇÃO DE PROBLEMAS", 18, bold=True)
    linhas = [
        ("O Windows não reconhece o volante", "Cabo só de carga; USB Stack errado",
         "Use cabo com dados; regrave com USB Stack = Pico SDK"),
        ("Um botão não acende", "Solda fria ou diodo invertido",
         "Refaça a solda; faixa do diodo para o lado da linha"),
        ("Três botões de uma linha não acendem", "Fio da linha solto",
         "Confira a ligação da linha L ao GP correspondente"),
        ("Apertar um botão acende outro", "Fios de linha ou coluna trocados",
         "Compare a fiação com o esquema do passo 8"),
        ("Encoder pula ou anda ao contrário", "A e B trocados",
         "Troque os fios A e B, ou ajuste ENC_INVERT no firmware"),
        ("Aleta troca de marcha duas vezes", "Folga do ímã muito grande ou sensor solto",
         "Refaça o ajuste do passo 10; cole o sensor de novo"),
        ("Aleta não responde", "Volante ligado com a aleta puxada; sensor invertido",
         "Desconecte, solte as aletas e conecte; face marcada do SS49E para o ímã"),
        ("Aleta pesada demais ou sem clique", "Parafuso N muito perto ou encostado",
         "Recue o parafuso e reajuste a folga com o cartão"),
        ("Aleta raspa ao girar", "Eixo torto ou bucha fora do lugar",
         "Retire o eixo, confira as buchas e monte de novo"),
        ("Volante balança na base", "Parafusos do adaptador frouxos",
         "Reaperte em estrela, com trava-rosca"),
    ]
    xs = [12, 92, 170]
    y = 180
    M.c.setFillColorRGB(*PAINEL)
    M.c.rect(10 * mm, (y - 2) * mm, 278 * mm, 7 * mm, stroke=0, fill=1)
    for x, h in zip(xs, ["SINTOMA", "CAUSA PROVÁVEL", "O QUE FAZER"]):
        M.txt(x, y, h, 8, bold=True, cor=FRACO)
    for i, (a, b, s) in enumerate(linhas):
        yy = y - 10 - i * 14.5
        M.c.setStrokeColorRGB(*GRID)
        M.c.line(10 * mm, (yy - 8) * mm, 288 * mm, (yy - 8) * mm)
        M.paragrafo(xs[0], yy, 76, a, 8.5, bold=True)
        M.paragrafo(xs[1], yy, 74, b, 8.5, cor=FRACO)
        M.paragrafo(xs[2], yy, 115, s, 8.5, cor=NOVO)


if __name__ == "__main__":
    M = Manual(_SAIDA, TOTAL)
    for fn in (capa, ferramentas, bom_fabricadas, bom_compradas, p01_insertos, p02_conjunto_movel,
               p03_suporte, p04_aleta_no_suporte, p05_botoes, p06_suportes_placa, p07_pico,
               p08_fiacao, p09_firmware, p10_ajuste, p11_pegadas, p12_base, verificacao, problemas):
        fn(M)
        print("ok", fn.__name__, flush=True)
    M.salvar()
