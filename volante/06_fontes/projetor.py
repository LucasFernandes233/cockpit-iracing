"""Projeção ortográfica com remoção de linhas ocultas (HLR) para desenhos técnicos."""
import math
import cadquery as cq
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Pnt2d
from OCP.BRepLib import BRepLib


def _norm(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


class Vista:
    """Direção = de onde se olha (câmera em +direção). Y do modelo aparece para cima."""

    def __init__(self, direcao):
        n = _norm(direcao)
        vx = _cross((0, 1, 0), n)
        if sum(c * c for c in vx) < 1e-9:
            vx = (1, 0, 0)
        vx = _norm(vx)
        self.ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(*n), gp_Dir(*vx))
        self.proj = HLRAlgo_Projector(self.ax)

    def ponto(self, p):
        p2 = gp_Pnt2d()
        self.proj.Project(gp_Pnt(*p), p2)
        return (p2.X(), p2.Y())

    def linhas(self, formas, ocultas=False):
        """formas: lista de cq.Workplane/Shape. Retorna lista de polilinhas 2D."""
        solidos = []
        for f in formas:
            if isinstance(f, cq.Workplane):
                solidos += [s for s in f.vals() if isinstance(s, cq.Shape)]
            else:
                solidos.append(f)
        comp = cq.Compound.makeCompound(solidos)
        hlr = HLRBRep_Algo()
        hlr.Add(comp.wrapped)
        hlr.Projector(self.proj)
        hlr.Update()
        hlr.Hide()
        h = HLRBRep_HLRToShape(hlr)
        if ocultas:
            comps = [h.HCompound(), h.OutLineHCompound()]
        else:
            comps = [h.VCompound(), h.Rg1LineVCompound(), h.OutLineVCompound()]
        polis = []
        for c in comps:
            if c.IsNull():
                continue
            BRepLib.BuildCurves3d_s(c, 1e-6)
            for e in cq.Shape.cast(c).Edges():
                if e.geomType() == "LINE":
                    a, b = e.startPoint(), e.endPoint()
                    polis.append([(a.x, a.y), (b.x, b.y)])
                else:
                    L = e.Length()
                    n = max(4, min(80, int(L / 0.6)))
                    pts = [e.positionAt(i / n) for i in range(n + 1)]
                    polis.append([(p.x, p.y) for p in pts])
        return polis


def caixa_limites(polis, extras=()):
    xs = [x for p in polis for x, _ in p] + [x for x, _ in extras]
    ys = [y for p in polis for _, y in p] + [y for _, y in extras]
    return min(xs), min(ys), max(xs), max(ys)


class Encaixe:
    """Mapeia coordenadas projetadas (mm do modelo) para a folha (pontos)."""

    def __init__(self, limites, x, y, w, h, margem=0.08, escala_max=None):
        x0, y0, x1, y1 = limites
        bw, bh = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
        s = min(w / bw, h / bh) * (1 - 2 * margem)
        if escala_max:
            s = min(s, escala_max)
        self.s = s
        self.ox = x + w / 2 - (x0 + x1) / 2 * s
        self.oy = y + h / 2 - (y0 + y1) / 2 * s

    def __call__(self, p):
        return self.ox + p[0] * self.s, self.oy + p[1] * self.s
