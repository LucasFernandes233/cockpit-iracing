# 🏎️ Cockpit iRacing

Projeto de criação de um **cockpit de simulador de corrida do zero** — da modelagem 3D
até o firmware/software. A primeira frente é o **volante**; depois vêm pedais, câmbio,
estrutura e software de integração, cada um seguindo as mesmas 9 fases (0 a 8).

> Documento mestre do projeto: **[`Roteiro_Projeto_Volante.pdf`](Roteiro_Projeto_Volante.pdf)**
> (ordem das fases, portões e testes).

## 🗺️ As 9 fases do volante

| Fase | Nome | Portão (libera a próxima) |
|------|------|---------------------------|
| **0** | Organização do projeto | Qualquer arquivo achado em < 1 min + orçamento escrito |
| 1 | Compras de longo prazo | Kit eletrônico recebido e conferido |
| 2 | Validação ergonômica (maquete) | Nenhum comando de alta frequência fora de alcance → gera rev01 |
| 3 | Protótipo em protoboard | 22 botões no Windows + 1 volta no iRacing |
| 4 | Fabricação do protótipo P1 | Peças dentro de ±0,3 mm |
| 5 | Montagem do P1 | Folha 17 do manual marcada |
| 6 | Testes e validação | Requisitos do MVP aprovados |
| 7 | Base Moza R3 + iRacing | 1 h de corrida sem falha |
| 8 | Versão final P2 (carbono, PCB, telemetria) | Passa nos testes da Fase 6 + telemetria em 2 sims |

Fases 1 e 2 correm em paralelo; a partir da Fase 5 é uma linha só.

## 📁 Organização do repositório

```
cockpit-iracing/
├── Roteiro_Projeto_Volante.pdf     # documento mestre (todas as fases)
├── volante/
│   ├── orcamento.md                # orçamento escrito (Fase 0)
│   ├── planilha_custos.csv         # item · previsto · gasto (Fase 0)
│   ├── requisitos/                 # requisitos, decisões, pinagem, lista de compras
│   ├── mecanica/                   # modelo 3D, pacote CAD, desenho da placa, aletas
│   ├── eletronica/                 # esquemas, pinagem detalhada, componentes
│   ├── firmware/                   # código do Raspberry Pi Pico (.ino)
│   ├── fabricacao/                 # STL/DXF, orçamentos de fornecedor, manual de montagem
│   └── testes/                     # tabelas de teste (Fases 6 e 7)
```

## 📇 Índice de arquivos do projeto

Status: ✅ no repositório · ⏳ pendente (gerado na conversa de projeto, falta adicionar)

| Arquivo | O que é | Pasta destino | Fase | Status |
|---------|---------|---------------|------|--------|
| `Roteiro_Projeto_Volante.pdf` | Ordem das fases, portões e testes | *(raiz)* | Todas | ✅ |
| Volante de Simulação — Requisitos e Inventário | Requisitos, decisões, layout de comandos, pinagem, lista de compras | `volante/requisitos/` | Todas | ⏳ |
| `placa_frontal_layout_MVP_rev00` (A3 e 2× A4) | Desenho 1:1 da placa para a maquete | `volante/mecanica/` | 2 | ⏳ |
| `volante_mvp.ino` | Firmware do Raspberry Pi Pico | `volante/firmware/` | 3, 5 | ⏳ |
| `aleta_mecanismo_rev00.pdf` | Conceito e cálculos das aletas | `volante/mecanica/` | Consulta | ⏳ |
| `volante_P1_rev00_CAD.zip` | STEP, STL, DXF da chapa, relatório de folgas | `volante/mecanica/` (STL/DXF → `fabricacao/`) | 4 | ⏳ |
| `manual_montagem_volante_P1.pdf` | Manual de montagem (18 folhas) | `volante/fabricacao/` | 5, 7 | ⏳ |

> **Regra de revisão:** todo arquivo enviado a fornecedor leva número de revisão no nome
> (`_rev01`). Nunca sobrescrever — criar revisão nova. Quando a rev01 sair (Fase 2), os
> arquivos `rev00` são substituídos e esta tabela é atualizada.

---

> Projeto em desenvolvimento — **Fase 0 (Organização)** em andamento. 🚧
