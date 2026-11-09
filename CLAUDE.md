# seu-milhao-video · máquina de criativos do Seu Milhão

Comece por `./sm status` e `./sm proximo`. Este arquivo é só o roteador.

## Princípios
1. **Fonte única de verdade.** Todo fato (valores, datas, redações, regras, preços, pendências) mora em `memoria/fatos.json`, com fonte e data. Os MDs explicam e apontam; nunca duplicam valores. Consulte com `./sm fato <chave>`.
2. **Reflexo antes de raciocínio.** Tarefa repetitiva ou mecânica é um comando `sm` (Python, sem token). O modelo só julga: redação, direção, nuance de política, avaliação visual final.
3. **Promoção de reflexo.** Tarefa feita à mão pela 2ª vez vira script na 3ª, registrada em `sistema_nervoso/REFLEXOS.md` com o que substitui e a economia estimada de tokens.
4. **Micro-passo com definição de pronto.** Cada passo tem validador (`./sm validar <passo>`). Passou: check automático, siga. Passo **[VOCÊ]**: PARE e espere o check (`./sm aprovar <passo>`). Falhou 2 vezes: PARE e mostre o erro em até 3 linhas.
5. **Economia de contexto.** Agente lê só `docs/01_PLAYBOOK_RESUMO.md` e o cartão; fatos via `sm fato`; saída ao usuário em até 5 linhas; visão só sobre folhas reduzidas.
6. **Nada se apaga.** O que sai vai para `_arquivo/` com nota de motivo; mover é `git mv`.
7. **Gasto só com confirmação.** Toda geração paga exige `--confirmar`; `--seco` simula a custo zero.

## Mapa (detalhe em docs/00_MAPA.md)
| Pasta | O que é |
|---|---|
| `docs/` | 01_PLAYBOOK (regras) · 01_PLAYBOOK_RESUMO (o que os agentes leem) · 02_MACROSSISTEMA · 03_ESTEIRA · 04_SISTEMA_NERVOSO · 05_BIBLIOTECA · 06_EXPEDICAO |
| `memoria/` | fatos.json (verdade) · glossario.json (taxonomia, movimentos, personas, tags) · calibracao.json |
| `fluxo/` | passos.yaml (P01–P18) · reestruturacao.yaml (R01–R18) · estado.json |
| `planejamento/` | matriz.json · cartoes/<id>.json · segmentos/ |
| `estilos/<nome>/` | bloco.txt · negativos.txt · paleta.md · modelos.md · licoes.md |
| `criativos/<id>/` | estado.json · custos.md · partitura.json · decupagem.json · esteira/ · prompts/ · quadros/ · tomadas/ · aprovados/ |
| `sistema_nervoso/` | pacote `sm` + tests/ + REFLEXOS.md · `./sm` na raiz é o atalho |
| `painel/` · `biblioteca/` · `ponte_capcut/` | aprovação local · clone do repositório privado (LFS) · entrega CapCut |
| `fontes/` | regulamento, marca, instituição, referência, calibracao/, **autorizacoes/ (fora de qualquer git)** |
| `.claude/agents/` | o squad (docs/03_ESTEIRA.md) · `_arquivo/` | descartados, com motivo |

## Sessão principal = chefe de linha
Roda `./sm status` / `./sm proximo`, aciona a estação indicada (subagente) passando só o id do criativo, o passo e a ficha anterior; apresenta os portões; nunca gera nem pula portão. Quando o usuário digita **"painel"**, lê as decisões (`fluxo/estado.json`, `criativos/<id>/estado.json`) e segue só o próximo passo.

## Regras de sessão
- Dinheiro só por `sm quadro gerar --confirmar` e `sm veo gerar --confirmar`, sempre com ordem do usuário no portão; o diretor-de-quadros e o operador entram quando há prompt novo ou imagem a avaliar; comando sem julgamento (prompt já carimbado) o chefe roda. Teto por criativo, alerta a 80%.
- Nunca exiba chaves; `.env` e `fontes/autorizacoes/` nunca saem da máquina.
- Decisões com o porquê em `decisoes.md` (privado; resumo público em `docs/DECISIONS.md`); custos em `custos.md` (global) e `criativos/<id>/custos.md`.
- Português do Brasil, simples. Relatório em cada PARE: feito · pendente · próximo passo · custo (≤ 5 linhas).

Ambiente: Python 3.12 em `.venv/` (uv) · HyperFrames 0.8.181 em `node_modules` · Vertex AI por ADC (`./sm vertex` testa) · `whisper-cli` · Git LFS · `gh`. Histórico anterior em `_arquivo/`.
