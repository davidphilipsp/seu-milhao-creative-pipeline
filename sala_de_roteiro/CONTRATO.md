# Contrato da Sala de Roteiro · versão 1.0 (22/10/2026)

## Entradas (somente leitura, via `./sala sincronizar`)
| Snapshot em `insumos/` | Origem na produção |
|---|---|
| `fatos.snapshot.json` · `glossario.snapshot.json` · `calibracao.snapshot.json` | `memoria/` |
| `modelo_roteiro.snapshot.md` | `planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md` |
| `playbook_resumo.snapshot.md` | `docs/01_PLAYBOOK_RESUMO.md` |
| `segmentos/*.md` · `estilos/<nome>/{bloco.txt,negativos.txt,licoes.md}` | `planejamento/segmentos/` · `estilos/` |
| `banco.snapshot.json` | `biblioteca/catalogo.json` (id, tipo, status, autorização, tags, nota) |
| `corpus/*.txt` | `fontes/corpus/` (texto extraído; hash do original no MANIFESTO) |
| `limites_producao.md` | **gerado** de fatos + lições + playbook (fora do hash) |

`MANIFESTO.json`: `hash` (12 caracteres, sobre todos os snapshots), `data`, hash por arquivo e origem. `historico/<hash>.json` guarda cada versão para apontar o que mudou.

## Saídas
| Saída | Quem consome |
|---|---|
| `cascas/rascunho/<id>.md` (+ `<id>.validacao.json`) | o usuário escolhe |
| `cascas/aprovadas/<id>.md` | `./sala para-roteiro` |
| `saida/<id>_ROTEIRO.md` | a produção: `./sm importar-roteiro` → `./sm validar roteiro <id>` |
| `propostas/NN-*.diff` | o usuário decide aplicar |

## Formato da casca (`cascas/rascunho/<id>.md`)
Cabeçalho entre `---`: `id`, `titulo`, `pedido`, `data`, `insumos_hash`, `segmento`, `persona`, `angulo`, `destino`, `duracao_alvo_s`, `familia`, `variacao_de` (id da biblioteca ou `nenhuma`), `confianca` (`alta` | `hipótese (…)`), `estilo`.

Seções (título `## <letra> · <nome>`), campos como `- Nome: valor`:
- **A · Conceito:** Frase · Tensão · Por que esta persona.
- **B · Gancho (0–3 s):** Ação física · Lugar · Hora e luz · Fundo (3 a 5 itens separados por `;`) · Não pode aparecer · Quem filma · Plano · Altura e ângulo · Lente (mm) · Distância · Profundidade de campo · Movimento · Obstrução · Figurino · Objeto principal · Primeira fala (≤ 10 palavras, presa ao que está em cena) · Texto na tela (≤ 6) · Som ambiente · Teste do mudo.
- **C · Esqueleto em batidas:** tabela `| # | mov | uso | intenção | fala-guia | quem | onde | ação | emoção | enquadramento | câmera | ligação | origem | tela |`. Uma linha por batida (vira um quadro na saída); todo movimento 1–6 aparece; `uso` = `usado` ou `suspenso: <porquê>`; fala-guia ≤ 15 palavras; origem = IA | Apresentador réplica | foto real da Instituição | banco: `<id do banco>` | gravação real; ligação = abertura | continuidade direta | corte casado | corte seco | fecho.
- **D · Matriz de coerência:** `| # | o que se vê | em cena | coerência |`, uma linha por fala-guia; `em cena` = `sim` ou `justificado: …`.
- **E · Ficha de produção:** Duração · Reuso × gerar · Pendências que travam · Custo estimado.
- **F · Taxonomia:** os 8 campos do glossário.
- **G · Variações de gancho:** `### G1` e `### G2`, cada um com Família · Ação física · Primeira fala · Texto na tela; famílias diferentes entre si e da principal.
- **H · Riscos:** versão que passa e o que mudou, em 1 linha. Única seção que pode citar o original proibido (fica fora do lint).

Famílias: objeto fora do lugar · contradição · atrito de dupla · cena em andamento · pergunta · ritual da rua · data como evento · convite · corrente.

## Estimativas
Duração por linha = palavras ÷ p/s da calibração (sem fala: 1,5 s; foto real sem fala: 4 s), igual à produção. Custo por linha gerada (IA ou Apresentador réplica) = quadro Nano Banana 1K + 1 teste Fast 720p 8 s + 1 final (padrão 1080p se rosto, mão, moeda, cheque ou close; senão Fast 1080p), com preços de `fatos.snapshot.json → tecnica.precos_usd`. Foto real, banco e gravação real: US$ 0 de geração.
