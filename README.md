# 🏎️ Cockpit iRacing

Projeto de criação de um **cockpit de simulador de corrida do zero** — da modelagem 3D
até o firmware/software. A primeira frente é o **volante**; o repositório é organizado
**por frente** (depois virão pedais, câmbio, estrutura e software).

> Pacote vigente: **rev01 (12/10/2026)** — projeto **100% impressão 3D**.
> Documentos mestres em [`volante/01_documentos/`](volante/01_documentos/).

## 📁 Estrutura (`volante/` — pacote `projeto_main`)

| Pasta | Conteúdo | Fase |
|-------|----------|------|
| `01_documentos/` | Requisitos e Inventário · Roteiro do Projeto (fases, portões, orçamento) | Todas |
| `02_maquete/` | Desenho 1:1 da placa frontal (A3 / 2×A4) para a maquete de papelão | 2 |
| `03_firmware/` | Firmware do Raspberry Pi Pico (`volante_mvp/volante_mvp.ino`) | 3, 5 |
| `04_cad/` | Modelo 3D rev01: montagem + peças STEP, STL de impressão, relatório, prévia | 4 |
| `05_manual/` | Manual de montagem rev01 (18 folhas, blueprint) | 5, 7 |
| `06_fontes/` | Scripts que geram o modelo 3D, o desenho da placa e o manual (CadQuery) | — |

## 🗺️ As 9 fases do volante (Roteiro)

| Fase | Nome | Portão |
|------|------|--------|
| **0** | Organização do projeto | Qualquer arquivo achado em < 1 min + orçamento escrito |
| 1 | Compras de longo prazo | Kit eletrônico recebido e conferido |
| 2 | Validação ergonômica (maquete) | Nenhum comando de alta frequência fora de alcance → rev01 |
| 3 | Protótipo em protoboard | 22 botões no Windows + 1 volta no iRacing |
| 4 | Fabricação do protótipo P1 | Peças dentro de ±0,3 mm |
| 5 | Montagem do P1 | Folha 17 do manual marcada |
| 6 | Testes e validação | Requisitos do MVP aprovados |
| 7 | Base Moza R3 + iRacing | 1 h de corrida sem falha |
| 8 | Versão final P2 | Passa nos testes da Fase 6 + telemetria em 2 sims |

## 💰 Orçamento (rev01, do documento de Requisitos)

| Bloco | Mín (R$) | Máx (R$) |
|-------|---------:|---------:|
| Protótipo P1 (Fases 0 a 6) | 960 | 2.170 |
| Base Moza R3 (kit) + adaptador | 4.450 | 4.650 |
| Versão final P2 | 760 | 1.720 |
| Reserva (15%) | 926 | 1.281 |
| **Total** | **7.096** | **9.821** |

> A base (~60% do custo) é o único item acima da premissa original. Decisão fica para
> antes da **Fase 7** (aumentar teto, comprar usada, ou outra base com volante destacável).

## ✅ Status

**Fase 0 (Organização) concluída:** repositório organizado por frente, pacote rev01
versionado, requisitos lidos. Próximo: Fases 1 (compras) e 2 (maquete), que correm em paralelo.

> **Regra de revisão:** todo arquivo enviado a fornecedor leva `_revNN` no nome e fica
> registrado no Git. Nunca sobrescrever — criar revisão nova.
