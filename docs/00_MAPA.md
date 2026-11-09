# 00 · Mapa do projeto

Três camadas: **memória** (fatos), **sistema nervoso** (`sm`, reflexos sem token) e **cérebro** (agentes, só onde há julgamento).

| Caminho | O que é | Quem escreve |
|---|---|---|
| `CLAUDE.md` | roteador: princípios, mapa, "rode `sm status`" | reestruturação |
| `docs/01_PLAYBOOK.md` | regras completas; aponta para `memoria/fatos.json` | chefe de linha (com decisão do usuário) |
| `docs/01_PLAYBOOK_RESUMO.md` | 1 página; é o que os agentes leem | idem |
| `docs/02_MACROSSISTEMA.md` | matriz SEGMENTO × ÂNGULO × ESTILO × DURAÇÃO, segmentos, linhas paralelas, convergência | estrategista |
| `docs/03_ESTEIRA.md` | estações, portões, diagrama, fichas de passagem | chefe de linha |
| `docs/04_SISTEMA_NERVOSO.md` | comandos `sm`, validadores, como promover reflexos | quem cria um reflexo |
| `docs/05_BIBLIOTECA.md` | repositório, LFS, catálogo, banco de takes | bibliotecário |
| `docs/06_EXPEDICAO.md` | ponte CapCut, partitura .srt, painel | finalizador |
| `memoria/fatos.json` | fonte única de verdade (valor, fonte, data, status) | só com decisão registrada em `decisoes.md` |
| `memoria/glossario.json` | taxonomia de 8 campos, 6 movimentos, personas, tags do banco | estrategista |
| `memoria/calibracao.json` | palavras/s do Apresentador (`sm calibrar`) | script |
| `fluxo/passos.yaml` | micro-passos de produção P01–P18 | reestruturação |
| `fluxo/reestruturacao.yaml` | micro-passos R01–R18 desta missão | reestruturação |
| `fluxo/estado.json` | estado global: criativo atual, passos R | `sm` |
| `planejamento/matriz.json` | a mesa: células segmento × ângulo com o cartão de cada uma | estrategista |
| `planejamento/cartoes/<id>.json` | um cartão por criativo (P01) | estrategista |
| `planejamento/segmentos/*.md` | popular (confiança alta), classe_media e alto_ticket (hipóteses) | estrategista |
| `estilos/<nome>/` | bloco.txt (prompt fixo), negativos.txt, paleta.md, modelos.md, licoes.md | diretor + chefe |
| `criativos/<id>/` | worktree do criativo: estado.json, custos.md, partitura.json, decupagem.json, esteira/ (fichas), prompts/, quadros/, tomadas/{teste,final}/, inspecao/, aprovados/ | estações, via `sm` |
| `sistema_nervoso/sm/` | o pacote (ver 04) · `tests/` (pytest) · `REFLEXOS.md` | reestruturação |
| `painel/` | app local (127.0.0.1:8765): matriz, micro-passos, checks [VOCÊ], quadros, tomadas, sequência, custo, biblioteca | — |
| `biblioteca/` | clone de `seu-milhao-biblioteca` (privado, LFS): referências + só G4 | bibliotecário |
| `ponte_capcut/<id>/` | entrega para o CapCut (06) | finalizador |
| `fontes/` | regulamento/, marca/, instituicao/, referencia/ (só local), calibracao/, **autorizacoes/** (nunca em remoto) | usuário |
| `.claude/agents/` | estrategista, roteirista, diretor, auditor, diretor-de-quadros, operador-de-video, inspetor, finalizador, bibliotecario | reestruturação |
| `decisoes.md` · `achados-para-o-time.md` · `creditos.md` · `custos.md` | registros cronológicos | todos |
| `_arquivo/` | pilotos N1-01, exploração TK-03 de 21/10, docs anteriores, scripts v1 (`scripts-v1/MOTIVO.md`) | ninguém apaga |
| `inventario.md` | mapa gerado por `sm inventario` | script |
