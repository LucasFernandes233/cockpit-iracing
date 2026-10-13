# 🛒 Lista de compras — Fase 1 (volante, rev01)

**Objetivo da Fase 1:** pedir agora o que demora a chegar, para não travar as fases
seguintes. Roda em paralelo com a Fase 2 (maquete). Preencher **Gasto**, **Fornecedor**
e **Status** conforme comprar (esta é a planilha de custos). Registrar a data prevista de chegada.

### ⚠️ Cuidados (erros comuns)
- **Cabo USB tem que ter DADOS** — cabo só de carga não funciona.
- **Ímã N52**, nunca N35 (força bem menor).
- **Set screw M8 em AÇO** (não inox/latão): o ímã de retorno precisa atrair aço.
- Comprar **com reserva** (não 1 de cada) — já previsto nas quantidades abaixo.

---

## A. Eletrônica (protótipo em protoboard) — ~R$ 195–320

| Item | Qtd | Previsto (R$) | Gasto (R$) | Fornecedor / link | Status |
|------|-----|--------------:|-----------:|-------------------|--------|
| Raspberry Pi Pico (RP2040), com pinos soldados | 2 (1 reserva) | 80–100 | | | ☐ |
| Botão tátil 12 × 12 mm | 15 | 15–30¹ | | | ☐ |
| Diodo 1N4148 | 15 | ¹ | | | ☐ |
| Encoder rotativo EC11 (20 pulsos, com clique) | 5 (1 reserva) | 40–75 | | | ☐ |
| Sensor Hall linear SS49E | 3 (1 reserva) | 10–25 | | | ☐ |
| Protoboard 830 pontos | 2 | 50–90² | | | ☐ |
| Kit de jumpers macho-macho | 1 | ² | | | ☐ |
| Cabo USB-A → micro-USB **com dados** | 1 | ² | | | ☐ |

¹ botões + diodos juntos · ² protoboards + jumpers + cabo juntos

## B. Ímãs de neodímio N52 — (ímãs + ferragem ~R$ 115–250)

| Item | Qtd | Previsto (R$) | Gasto (R$) | Fornecedor / link | Status |
|------|-----|--------------:|-----------:|-------------------|--------|
| Ímã N52 Ø10 × 5 mm (retorno da aleta) ⚠️ rev01 | 2 | 25–60³ | | | ☐ |
| Ímã N52 Ø5 × 3 mm (sensor Hall) | 6⁴ | ³ | | | ☐ |

³ todos os ímãs juntos · ⁴ 2 reais + simulação no protoboard + reserva

## C. Ferragem / mecânica — (incluso nos ~R$ 115–250)

| Item | Qtd | Previsto (R$) | Gasto (R$) | Fornecedor / link | Status |
|------|-----|--------------:|-----------:|-------------------|--------|
| Eixo de aço Ø4 × ~44 mm (giro da aleta) | 2 | 30–70⁵ | | | ☐ |
| Bucha de bronze Ø4 × Ø6 × 4 mm | 4 | ⁵ | | | ☐ |
| Set screw M8 × 10 ponta plana, **aço** | 2 | 60–120⁶ | | | ☐ |
| Inserto roscado M3 a quente (suportes/carregadores) | ~10 | ⁶ | | | ☐ |
| Inserto roscado M4 a quente (pegadas) | ~4 | ⁶ | | | ☐ |
| Parafuso M3 × 8 | ~10 | ⁶ | | | ☐ |
| Parafuso M4 × ~10 | ~4 | ⁶ | | | ☐ |
| Parafuso M5 (interface base 6 furos × 70 mm)⁷ | 6 | ⁶ | | | ☐ |
| Porcas M3 / M4 / M5 (kit) | 1 kit | ⁶ | | | ☐ |

⁵ eixos + buchas · ⁶ parafusos/porcas/insertos (kits) · ⁷ só usados na Fase 7, mas baratos — comprar junto

## ❌ NÃO comprar agora (dependem da maquete / fases posteriores)

- **12 botões de painel** — 10× Ø16 + 2× Ø19 — corpo **≤ 25 mm** atrás da placa (vale p/ B1–B4). → definir **após a maquete (Fase 2)**.
- **4 knobs Ø26** → após a maquete.
- **Base Moza R3 + adaptador quick release** → só na **Fase 7**.

---

## 💰 Resumo de custo da Fase 1

| Bloco | Mín (R$) | Máx (R$) |
|-------|---------:|---------:|
| Eletrônica do protótipo | 195 | 320 |
| Ímãs e ferragem | 115 | 250 |
| **Total Fase 1** | **310** | **570** |

## 🏪 Onde comprar no Brasil (sugestões, confirmar preço real)
- **Pico e eletrônica:** RoboCore, Usinainfo, Eletrogate, Baú da Eletrônica, Mercado Livre (Pico ~R$ 42–50).
- **Ímãs N52:** Mercado Livre, AliExpress (buscar "ímã neodímio N52").
- **Eixo Ø4 aço, buchas de bronze:** Mercado Livre, lojas de rolamentos/metais (ou barra Ø4 e cortar).
- **Insertos a quente M3/M4, parafusos, set screw M8:** Mercado Livre, AliExpress, parafusarias.

> **Portão da Fase 1:** kit eletrônico recebido e conferido (confere item por item e mede
> ímãs/eixos com paquímetro). Isso libera a Fase 3.
