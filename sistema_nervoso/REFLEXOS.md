# REFLEXOS · o que roda sem token

Regra (CLAUDE.md §3): tarefa feita à mão pela 2ª vez vira candidato; na 3ª vira comando aqui, com teste. Estimativa de tokens = o que o modelo gastava lendo arquivos, raciocinando e escrevendo a saída por execução, observado na esteira v1 de 21/10/2026.

| Comando | Substitui (feito à mão na v1) | Tokens/execução (estim.) | Data |
|---|---|---|---|
| `sm status` / `sm proximo` | chefe reler estado.json, fichas e decisoes.md para saber onde está | ~3.000 | 21/10 |
| `sm validar <passo>` | conferência manual de "está pronto?" por agente e pelo chefe (arquivos existem, dimensões, soma de tempos) | ~2.000 por passo | 21/10 |
| `sm aprovar` / `sm pendente` | edição à mão de estado.json e eventos nos portões | ~800 | 21/10 |
| `sm fato` | reler PLAYBOOK/regulamento/decisoes.md para achar um valor | ~1.500 por consulta (agente lia o PLAYBOOK inteiro: ~4.000) | 21/10 |
| `sm lint` | o auditor varrer proibidos, datas, valor do prêmio e SUSEP linha a linha | ~4.000 por artefato | 21/10 |
| `sm partitura validar` / `sm decupagem validar` | roteirista e diretor conferirem soma de tempos, palavras/s, cobertura, ligações, tags | ~2.500 | 21/10 |
| `sm banco buscar` | procurar no catálogo se já existe take parecido | ~2.000 | 21/10 |
| `sm quadro gerar` | montar prompt do Nano Banana a partir de bloco + refs + take, chamar o script, copiar linha de custo nos dois ledgers | ~2.500 | 21/10 |
| `sm veo gerar` | idem para o Veo, mais checar teto, 2ª tomada, nomes de arquivo | ~3.000 | 21/10 |
| `sm folha` / `sm tira-moeda` | o inspetor escrever comandos ffmpeg/Pillow para folhas e recortes (na v1 ~15 chamadas de ferramenta por tomada) | ~6.000 | 21/10 |
| `sm inspecionar` | checagens de dimensão, fps, duração, áudio, quadros pretos, OCR, e a ficha JSON | ~3.000 | 21/10 |
| `sm padronizar` / `sm ultimo-quadro` / `sm emendar` | finalizador escrever e conferir comandos ffmpeg (encadear.py v1 exigia leitura do código) | ~2.500 | 21/10 |
| `sm montar` | composição HyperFrames à mão por take (na v1: ~45 chamadas, 190k tokens no T1) | ~40.000 | 21/10 |
| `sm ponte` | copiar arquivos, escrever SRT e LEIA-ME | ~2.000 | 21/10 |
| `sm publicar` | publicar.sh + catalogar.py + FICHA à mão + commit/push (bibliotecário v1: ~127k tokens) | ~20.000 | 21/10 |
| `sm custo` | somar custos.md e comparar com o teto | ~800 | 21/10 |
| `sm calibrar` | medir palavras/s com Whisper e registrar | ~2.000 | 21/10 |
| `sm inventario` | listar arquivos e propor destino (R01 à mão: ~8.000) | ~8.000 | 21/10 |
| `sm vertex` | teste_acesso.py + interpretação | ~500 | 21/10 |
| `sm painel` | subir o servidor | ~200 | 21/10 |

## Candidatos (feitos à mão 1–2 vezes; viram reflexo na 3ª)
- Levantar sombras de roupa escura com curva por canal e máscara elíptica no rosto (feito 1× no T1): candidato a `sm corrigir-sombras <id> <take>`.
- Folha de comparação rosto gerado × prints do Apresentador (feito 1×): candidato a `sm folha-rosto`.
- Reauth do ADC com `--no-launch-browser` e código colado (feito 3× em 21/10, mas é interativo por natureza): documentado em decisoes.md; não automatizável sem navegador.
- Migrar estado v1 (takes em lista, portões G1–G4) para o formato P01–P18: feito 1× no R18.

## Como medir
Tokens por criativo: `sm custo tokens <id> <n> "nota"` ao fim de cada acionamento de agente (o chefe lê o `usage` da notificação do subagente). `sm custo fechar <id>` grava US$ + tokens.

## 22/10/2026
| `sm tratar-celular <arquivo> [--intensidade leve\|media]` | pós-processamento de celular à mão (ffmpeg por tentativa e erro no finalizador) | ~6.000 por take | 22/10 |
| `sm comparar a b … --referencia r` | folha antes × depois × referência + saturação, realces, alta frequência e tremor medidos | ~4.000 | 22/10 |

## Reflexos pendentes (especificação; não implementar enquanto exigir reprocessar clipes)
- **`sm tratar-celular` por meta, malha fechada completa** (22/10): hoje só a saturação é fechada em malha (3 iterações). Especificação: medir `sm comparar` após cada passada e ajustar até cair nas metas de `pos.json → metas`: realces >0,97 entre 2% e 4% (ajustar o joelho da curva e o ganho dos realces), alta frequência 7–9 (ajustar `unsharp` para baixo e `mbps` para baixo quando acima; subir `unsharp` quando abaixo), tremor 4–5 px por 0,25 s (ajustar `tremor_px` e `rotacao_graus`). Máximo 4 passadas; registrar os parâmetros finais no `estado.json` do criativo. Economia estimada: ~6.000 tokens por take (hoje a leitura da tabela e o ajuste são do finalizador).
- `sm importar-roteiro` com tags por sinônimo (feito 22/10): ampliar o dicionário de sinônimos a partir dos roteiros reais que o usuário entregar.
| `sm importar-roteiro` / `sm validar roteiro` | roteirista + diretor + auditor lerem o roteiro à mão e escreverem partitura/decupagem/ficha | ~25.000 por criativo | 22/10 |
| `sm liberar-geracao` / trava em `sm quadro`/`sm veo` | conferência humana de 'pode gastar?' antes de cada comando | ~500 | 22/10 |
| `sm validar coerencia` | reler RESUMO, PLAYBOOK, estilos e agentes procurando contradição | ~12.000 | 22/10 |
