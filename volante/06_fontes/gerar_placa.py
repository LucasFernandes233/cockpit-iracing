"""Placa frontal do volante - layout de comandos do MVP, rev00.
Gera desenho em escala 1:1 (A3 paisagem) e versão em 2 folhas A4 para colar.
Coordenadas em mm, origem no centro do cubo (eixo da base), y para cima.
"""
import math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import Color, black

REV = "rev00"
A3 = (420 * mm, 297 * mm)
A4P = (210 * mm, 297 * mm)
ORIG = (210, 150)  # posição da origem do volante na folha A3 (mm)

AZUL = Color(0.10, 0.35, 0.75)
VERM = Color(0.80, 0.15, 0.15)
VERDE = Color(0.10, 0.55, 0.30)
CINZA = Color(0.55, 0.55, 0.55)
LARANJA = Color(0.90, 0.50, 0.05)

# --- Geometria ---------------------------------------------------------
HUB = (0, -5)
PCD = 70
FURO_PARAF = 5.5
BOTAO_FURO = 16      # furo para botão de painel 16 mm
BOTAO_FIRME = 19     # B5 e B6: botão maior e mais firme
ENC_FURO = 7         # eixo do encoder EC11 (rosca M7)
ENC_KNOB = 26        # diâmetro do knob

botoes = {
    "B1": ((84, 34), "DRS / farol"),
    "B2": ((-84, 34), "Rádio"),
    "B3": ((84, 8), "BB próx."),
    "B4": ((-84, 8), "BB ant."),
    "B5": ((-78, 88), "Limitador"),
    "B6": ((78, 88), "Neutro"),
    "B7": ((-60, 60), "Ignição"),
    "B8": ((60, 60), "Overtake/farol"),
    "B9": ((-82, -22), "Limpador"),
    "B10": ((-26, -56), "Pedir pit"),
    "B11": ((26, -56), "Chat"),
    "B12": ((82, -22), "Livre"),
}
encoders = {
    "E1": ((-98, 62), "Freio"),
    "E2": ((98, 62), "TC / Dif."),
    "E3": ((-56, -38), "ABS / ERS"),
    "E4": ((56, -38), "Black box"),
}


def furos_cubo():
    pts = []
    for k in range(6):
        a = math.radians(90 + 60 * k)
        pts.append((HUB[0] + PCD / 2 * math.cos(a), HUB[1] + PCD / 2 * math.sin(a)))
    return pts


def desenhar(c, ox, oy):
    """Desenha o volante com a origem em (ox, oy) mm da folha."""
    def P(x, y):
        return (ox + x) * mm, (oy + y) * mm

    def circ(x, y, d, stroke=black, dash=None, w=0.35, fill=None):
        c.setStrokeColor(stroke)
        c.setLineWidth(w)
        c.setDash(*dash) if dash else c.setDash()
        if fill is not None:
            c.setFillColor(fill)
        X, Y = P(x, y)
        c.circle(X, Y, d / 2 * mm, stroke=1, fill=1 if fill is not None else 0)
        c.setDash()

    def cruz(x, y, s=3, color=black):
        c.setStrokeColor(color)
        c.setLineWidth(0.2)
        c.line(*P(x - s, y), *P(x + s, y))
        c.line(*P(x, y - s), *P(x, y + s))

    def texto(x, y, s, size=6.5, color=black, bold=False, align="c"):
        c.setFillColor(color)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        X, Y = P(x, y)
        {"c": c.drawCentredString, "l": c.drawString, "r": c.drawRightString}[align](X, Y, s)

    # Pegadas (fantasma, peça impressa separada)
    c.setStrokeColor(CINZA); c.setLineWidth(0.3); c.setDash(3, 2)
    for sx in (-1, 1):
        x0 = 116 if sx > 0 else -146
        X, Y = P(x0, -82)
        c.roundRect(X, Y, 30 * mm, 176 * mm, 12 * mm, stroke=1, fill=0)
    c.setDash()
    texto(-131, 100, "pegada", 6, CINZA)
    texto(-131, 96, "(peça 3D)", 6, CINZA)
    texto(131, 100, "pegada", 6, CINZA)
    texto(131, 96, "(peça 3D)", 6, CINZA)

    # Contorno da placa frontal
    c.setStrokeColor(black); c.setLineWidth(0.6)
    p = c.beginPath()
    p.moveTo(*P(-100, 108))
    p.lineTo(*P(100, 108))
    p.curveTo(*P(112, 108), *P(120, 102), *P(120, 92))
    p.lineTo(*P(120, -32))
    p.curveTo(*P(120, -55), *P(108, -72), *P(84, -72))
    p.lineTo(*P(-84, -72))
    p.curveTo(*P(-108, -72), *P(-120, -55), *P(-120, -32))
    p.lineTo(*P(-120, 92))
    p.curveTo(*P(-120, 102), *P(-112, 108), *P(-100, 108))
    p.close()
    c.drawPath(p, stroke=1, fill=0)

    # Furos de fixação das pegadas (4 por lado)
    for sx in (-1, 1):
        for y in (80, 40, 0, -30):
            circ(sx * 112, y, 4.5, black, w=0.3)

    # Eixos de simetria
    c.setStrokeColor(CINZA); c.setLineWidth(0.15); c.setDash([6, 1.5, 1, 1.5])
    c.line(*P(0, -80), *P(0, 116))
    c.line(*P(-125, HUB[1]), *P(125, HUB[1]))
    c.setDash()

    # Display e LEDs (v2, só reserva de espaço)
    c.setStrokeColor(LARANJA); c.setLineWidth(0.35); c.setDash(2, 1.5)
    X, Y = P(-50, 38)
    c.rect(X, Y, 100 * mm, 56 * mm, stroke=1, fill=0)
    c.setDash()
    texto(0, 68, "RESERVA v2: display 4,3\"", 7, LARANJA, True)
    texto(0, 63, "100 × 56 mm (área livre no MVP)", 6, LARANJA)
    for i in range(15):
        circ(-56 + 8 * i, 100, 5, LARANJA, dash=(1, 1), w=0.25)
    texto(0, 103.5, "reserva v2: 15 LEDs de giro (passo 8 mm)", 5.5, LARANJA)

    # Cubo: PCD 70, 6 furos
    circ(*HUB, PCD, VERM, dash=(4, 1.5), w=0.2)
    circ(*HUB, 50, VERM, dash=(1.5, 1.5), w=0.25)
    for (x, y) in furos_cubo():
        circ(x, y, FURO_PARAF, VERM, w=0.4)
        circ(x, y, 12, VERM, dash=(1, 1), w=0.2)
        cruz(x, y, 2.5, VERM)
    texto(0, -11, "eixo da base", 5.5, VERM)
    texto(0, -18, "6× Ø5,5 em PCD 70", 6, VERM, True)
    texto(0, -23, "Ø50 = folga do adaptador", 5.5, VERM)

    # Encoders
    for nome, ((x, y), fun) in encoders.items():
        circ(x, y, ENC_KNOB, VERDE, dash=(2, 1), w=0.3)
        circ(x, y, ENC_FURO, VERDE, w=0.5)
        cruz(x, y, 4, VERDE)
        texto(x, y + 15.5, nome, 7, VERDE, True)
        texto(x, y - 18, fun, 6, VERDE)

    # Botões
    for nome, ((x, y), fun) in botoes.items():
        d = BOTAO_FIRME if nome in ("B5", "B6") else BOTAO_FURO
        circ(x, y, d, AZUL, w=0.5)
        cruz(x, y, 3, AZUL)
        texto(x, y + d / 2 + 2, nome, 7, AZUL, True)
        texto(x, y - d / 2 - 4.5, fun, 5.8, AZUL)



def moldura_a3(c):
    W, H = 420, 297
    c.setStrokeColor(black); c.setLineWidth(0.5)
    c.rect(8 * mm, 8 * mm, (W - 16) * mm, (H - 16) * mm)

    # Título
    c.setFont("Helvetica-Bold", 14); c.setFillColor(black)
    c.drawString(14 * mm, (H - 18) * mm, "PLACA FRONTAL — LAYOUT DE COMANDOS DO MVP")
    c.setFont("Helvetica", 9)
    c.drawString(14 * mm, (H - 24) * mm,
                 "Vista frontal (lado do piloto) · escala 1:1 · cotas em mm · origem no eixo da base")

    # Escala de verificação
    x0, y0 = 14, 20
    c.setLineWidth(0.6)
    c.line(x0 * mm, y0 * mm, (x0 + 100) * mm, y0 * mm)
    for i in range(11):
        h = 3 if i % 5 == 0 else 1.5
        c.line((x0 + 10 * i) * mm, y0 * mm, (x0 + 10 * i) * mm, (y0 + h) * mm)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x0 * mm, (y0 + 5) * mm, "CONFIRA A ESCALA: esta barra deve medir 100 mm")
    c.setFont("Helvetica", 7)
    c.drawString(x0 * mm, (y0 - 5) * mm, "Imprimir em \"tamanho real / 100%\", nunca \"ajustar à página\".")

    # Legenda
    lx, ly = 14, 62
    c.setFont("Helvetica-Bold", 8); c.drawString(lx * mm, ly * mm, "LEGENDA")
    itens = [
        (AZUL, "Botão — furo Ø16 (B5, B6: Ø19, mais firme)"),
        (VERDE, "Encoder EC11 — furo Ø7; tracejado = knob Ø26"),
        (VERM, "Fixação na base — 6× Ø5,5 em PCD 70"),
        (LARANJA, "Reserva para a v2 (display e LEDs)"),
        (CINZA, "Pegadas (peça separada, impressa em 3D)"),
    ]
    c.setFont("Helvetica", 7)
    for i, (col, t) in enumerate(itens):
        y = ly - 5 - 4.5 * i
        c.setFillColor(col); c.rect(lx * mm, (y - 0.5) * mm, 3 * mm, 3 * mm, stroke=0, fill=1)
        c.setFillColor(black); c.drawString((lx + 5) * mm, y * mm, t)

    # Notas
    nx, ny = 150, 62
    c.setFont("Helvetica-Bold", 8); c.drawString(nx * mm, ny * mm, "NOTAS")
    notas = [
        "1. Placa: 236 × 180 mm; com pegadas: ~292 mm.",
        "2. Furos Ø16/Ø19 assumem botões de painel;",
        "   ajustar após escolher o componente.",
        "3. Parafusos do cubo exigem chave livre:",
        "   nada dentro dos círculos de Ø12.",
        "4. Aletas e embreagem: montadas atrás",
        "   (desenho próprio, próxima revisão).",
        "5. Posições a validar na maquete 1:1.",
    ]
    c.setFont("Helvetica", 7)
    for i, t in enumerate(notas):
        c.drawString(nx * mm, (ny - 5 - 4 * i) * mm, t)

    # Carimbo
    bx, by, bw, bh = 300, 10, 110, 22
    c.setLineWidth(0.5); c.rect(bx * mm, by * mm, bw * mm, bh * mm)
    c.line(bx * mm, (by + 11) * mm, (bx + bw) * mm, (by + 11) * mm)
    c.line((bx + 70) * mm, by * mm, (bx + 70) * mm, (by + bh) * mm)
    c.setFont("Helvetica-Bold", 8)
    c.drawString((bx + 2) * mm, (by + 15) * mm, "VOL-MEC — Placa frontal")
    c.setFont("Helvetica", 7)
    c.drawString((bx + 2) * mm, (by + 4) * mm, "Projeto Cockpit iRacing · Jarvis")
    c.drawString((bx + 72) * mm, (by + 15) * mm, f"Revisão: {REV}")
    c.drawString((bx + 72) * mm, (by + 4) * mm, "Data: 12/10/2026")


def gerar_a3(path):
    c = canvas.Canvas(path, pagesize=A3)
    c.setTitle(f"Placa frontal - layout MVP {REV}")
    moldura_a3(c)
    desenhar(c, *ORIG)
    c.showPage(); c.save()


def gerar_a4_duas_folhas(path):
    """Divide a folha A3 em duas A4 retrato; emenda na linha x = 200 mm da A3."""
    c = canvas.Canvas(path, pagesize=A4P)
    c.setTitle(f"Placa frontal - layout MVP {REV} (2x A4)")
    for pagina, desloc in ((1, 0), (2, 190)):
        c.saveState()
        c.translate(-desloc * mm, 0)
        moldura_a3(c)
        desenhar(c, *ORIG)
        c.restoreState()
        # marca de colagem
        c.setStrokeColor(VERM); c.setLineWidth(0.4); c.setDash(4, 2)
        xl = 200 if pagina == 1 else 10
        c.line(xl * mm, 0, xl * mm, 297 * mm)
        c.setDash()
        c.setFont("Helvetica-Bold", 8); c.setFillColor(VERM)
        if pagina == 1:
            c.drawRightString(198 * mm, 290 * mm, "FOLHA 1/2 — lado esquerdo")
            c.drawRightString(198 * mm, 285 * mm, "alinhe aqui a borda recortada da folha 2")
        else:
            c.drawString(24 * mm, 290 * mm, "FOLHA 2/2 — lado direito")
            c.drawString(24 * mm, 285 * mm, "recorte na linha vermelha e cole a borda")
            c.drawString(24 * mm, 280 * mm, "sobre a linha vermelha da folha 1")
        c.showPage()
    c.save()


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    gerar_a3(f"{out}/placa_frontal_layout_MVP_{REV}_A3.pdf")
    gerar_a4_duas_folhas(f"{out}/placa_frontal_layout_MVP_{REV}_2xA4.pdf")
    print("ok")
