# Sala de Roteiro

Módulo **isolado** de idealização de cascas de roteiro (gancho + estrutura, com lugar e câmera decididos desde o 1º segundo). Não gera imagem nem vídeo. Custo em US$: zero. Não importa nem chama o `sm`.

## Como usar
```
./sala sincronizar [--corpus <pasta>]   # copia os insumos de leitura da produção, com hash e data
./sala pedido "segmento popular, ângulo solidário, destino grupo, 30 s, 3 cascas"
# idealizador (.claude/agents/idealizador.md) escreve cascas/rascunho/<id>.md
./sala validar [<id>…]                  # definição de pronto; sem id = todo o rascunho
./sala aprovar <id>                     # SÓ o usuário: rascunho/ → aprovadas/
./sala para-roteiro <id>                # aprovada → saida/<id>_ROTEIRO.md (formato do modelo da produção)
./sala estado                           # ≤ 5 linhas
./sala verificar-isolamento             # roda antes de cada commit
```
Testes: `python3 -m pytest sala_de_roteiro/tests -q` (da raiz do repositório).

## Fluxo
pedido → cascas (rascunho) → **[você escolhe: ./sala aprovar]** → saida/ → a produção importa com `./sm importar-roteiro` e `./sm validar roteiro` (a sala nunca roda esses comandos).

## Isolamento (inegociável)
- **Escreve só** em `sala_de_roteiro/`, no novo `.claude/agents/idealizador.md` e no lançador `./sala` da raiz (exceção declarada: arquivo novo de 2 linhas, sem lógica).
- **Lê** da produção só: `memoria/*.json`, `docs/01_PLAYBOOK_RESUMO.md`, `estilos/*/{bloco,negativos,licoes}`, `planejamento/segmentos/`, `planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md`, `biblioteca/catalogo.json`, `fontes/corpus/`.
- **Nunca toca**: `sistema_nervoso/`, `fluxo/`, `criativos/`, `biblioteca/`, `ponte_capcut/`, `painel/`, `estilos/`, `memoria/`, `fontes/`, os agentes existentes, `custos.md`, `decisoes.md`, `achados-para-o-time.md`, `creditos.md`.
- **Nunca roda**: `./sm quadro`, `./sm veo`, `./sm liberar-geracao`, `./sm publicar`, `./sm tratar-celular`, Vertex, Nano Banana, Veo.
- Mudança em arquivo compartilhado é **proposta** (diff em `propostas/`), nunca aplicada pela sala.
- `ferramentas/verificar_isolamento.py` compara o branch com `main` e falha com qualquer arquivo fora das áreas acima.

## Como a produção alimenta a sala
Cada casca grava o `insumos_hash` que usou. Quando a produção muda (lição nova, fato novo), `./sala sincronizar` muda o hash e `./sala validar` marca a casca **DESATUALIZADA**, com a lista do que mudou.

## Pastas
`insumos/` snapshots + `MANIFESTO.json` + `historico/` · `hooks/` biblioteca de ganchos e léxico · `pedidos/` · `cascas/{rascunho,aprovadas}/` · `saida/` · `propostas/` · `ferramentas/` · `tests/`. Contrato: `CONTRATO.md`.
