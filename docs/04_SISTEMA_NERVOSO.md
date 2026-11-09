# 04 · Sistema nervoso (`sm`)

Pacote Python em `sistema_nervoso/sm/` (Typer, pytest). Atalho na raiz: `./sm`. Cada comando é um reflexo: roda sem gastar token. Testes: `cd sistema_nervoso && ../.venv/bin/python -m pytest -q`.

| Comando | O que faz |
|---|---|
| `sm status` | próximo micro-passo, passos [VOCÊ] pendentes, custo e saldo (≤ 5 linhas) |
| `sm proximo` | descreve o próximo passo e quem executa (script, agente, VOCÊ) |
| `sm validar <passo> [--id X]` | roda o validador; check automático se passar; 2 falhas → PARE |
| `sm aprovar <passo> [nota] [--reprovar]` · `sm pendente <passo>` | registra o seu check (o painel chama o mesmo) · marca um portão como aguardando você |
| `sm fato <chave> [--completo]` · `sm fatos [prefixo]` | lê a memória (valor, ou valor + fonte + data) |
| `sm lint <arquivo> [--rodape]` | proibidos, fatos divergentes, data/valor/SUSEP errados, rodapé ausente; determinístico, com testes |
| `sm calibrar [audio]` | palavras/s do Apresentador (Whisper local) → `memoria/calibracao.json`; sem gravação usa a estimativa marcada |
| `sm partitura validar <id>` · `sm decupagem validar <id>` | definição de pronto de P03 e P04 |
| `sm banco buscar <id>` | REUSO ou GERAR em cada take, pelo catálogo |
| `sm quadro gerar <id> <take> [--fim] [--seco\|--confirmar]` | Nano Banana com o pacote de estilo e as referências; nomes `<take>_inicio.png` / `_fim.png` |
| `sm veo gerar <id> <take> --modo teste\|final [--confirmar\|--seco] [--tentativa N]` | único caminho de gasto em vídeo; registra custo nos dois ledgers; respeita teto e regra de 2 testes |
| `sm folha <id> [quadros\|tomadas]` · `sm tira-moeda <id>` | folhas reduzidas; recortes da moeda ao lado das referências |
| `sm inspecionar <id> [--etapa teste\|final]` | dimensão, fps, duração, áudio ausente, quadros pretos, OCR (se houver tesseract) + folhas → `esteira/inspetor_<etapa>.json` |
| `sm padronizar <id> <take> [--trecho a-b]` · `sm ultimo-quadro` · `sm emendar` | FFmpeg |
| `sm animar-foto <foto> <saida>` | zoom e deslize sem IA generativa |
| `sm tratar-celular <arquivo> [saida] [--intensidade leve\|media]` · `sm comparar <a> <b>… --referencia <r>` | textura de celular (tremor, curva, nitidez, grão, ciclo de compressão; `estilos/<estilo>/pos.json`) · folha antes × depois × referência com métricas |
| `sm montar <id>` | sequência sem e com copies (título ouro 3D, apoio, rodapé via Pillow + overlay) + `copies.txt` para o lint |
| `sm ponte <id>` | `ponte_capcut/<id>/`: NN_take, sequencia, partitura.srt, guia_copies.srt, rodape_legal.png, LEIA-ME (5 linhas) |
| `sm publicar <id> [--seco] [--conjunto-completo]` | biblioteca: só com G4; catálogo com tags, README, commit, push (seco → `_seco/biblioteca/`) |
| `sm custo` · `sm custo ver <id>` · `sm custo fechar <id>` · `sm custo tokens <id> <n>` | US$ e tokens por criativo; alerta a 80% |
| `sm importar-roteiro <md> [--id X]` · `sm validar roteiro <id>` · `sm validar coerencia` | roteiro quadro a quadro → partitura + decupagem; relatório ≤10 linhas (duração, ritmo, função, lint, pessoas, dependências, reuso, custo estimado) · fatos únicos e sem contradição |
| `sm liberar-geracao <id>` · `sm travar-geracao` | trava de geração (só o usuário libera; um criativo por vez) |
| `sm novo <id> "título" [--teto]` · `sm inventario` · `sm painel` · `sm vertex` | abrir criativo · mapa de arquivos · painel local · teste de acesso sem custo |

## Validadores (`sm/validadores.py`)
Um por passo (`r01_…`, `p01_…`), devolvem lista de erros. O validador de P-passo recebe o id do criativo; o de R-passo não recebe nada. Novo passo = nova função + linha no YAML.

## Como promover um reflexo
1. A tarefa foi feita à mão pelo modelo pela 2ª vez → anote em `sistema_nervoso/REFLEXOS.md` (candidato).
2. Na 3ª, escreva a função em `sm/`, exponha no `cli.py`, escreva um teste em `tests/`.
3. Registre em REFLEXOS.md: comando, o que substitui, tokens economizados (estimativa por execução).
4. Atualize este documento e, se o agente deixar de fazer a tarefa, o `.claude/agents/<estacao>.md`.

## Modo --seco
`sm quadro gerar --seco` cria um PNG placeholder; `sm veo gerar --seco` cria um MP4 de cor sólida de 8 s; ambos registram custo 0 marcado "SECO". `sm publicar --seco` espelha em `_seco/biblioteca/` sem commit. Serve para testar a esteira inteira sem gasto (R15).
