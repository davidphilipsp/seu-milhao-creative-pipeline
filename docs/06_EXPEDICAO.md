# 06 · Expedição

## Ponte CapCut (`sm ponte <id>` → `ponte_capcut/<id>/`)
| Arquivo | O que é |
|---|---|
| `NN_take.mp4` | takes aprovados com nome estável (NN = posição na decupagem) |
| `sequencia.mp4` · `sequencia_copies.mp4` | emenda a seco sem e com copies (título ouro 3D, apoio, rodapé) |
| `partitura.srt` | as falas nos tempos da partitura, para gravar a narração do Apresentador e encaixar no CapCut |
| `guia_copies.srt` | tempo e texto de cada copy |
| `rodape_legal.png` | faixa 1080×92 pronta (texto de `redacoes_fixas.rodape`) |
| `LEIA-ME.txt` | 5 linhas: formato, ordem dos takes, o que é cada arquivo, pendências (`sm fato pendencias`) |

Regras de montagem (`sm montar`): formato e codec de `tecnica.formato` / `tecnica.codec_master`; título à esquerda (x 64) na faixa y 1180–1375 para nunca cobrir rosto nem moeda; rodapé em y 1408–1500 o tempo todo; zonas seguras do Instagram; `copies.txt` passa pelo `sm lint --rodape` (validador P14).

## Painel (`sm painel` → http://127.0.0.1:8765)
Lê `fluxo/estado.json` e `criativos/*/estado.json`. Mostra: matriz (células e cartões), micro-passos com status, botões de check nos passos [VOCÊ] (chamam `sm aprovar`), quadros e tomadas, "Assistir sequência", campos Manter / Mudar / Nunca, custo e saldo, aba Biblioteca. **Nunca dispara geração.** Só localhost. No terminal, "painel" faz o chefe de linha ler as decisões e seguir só o próximo passo.

## Veiculação
Antes de subir qualquer peça: `sm fato pendencias` (termos da Instituição e do Apresentador, Mecir, logos originais, rótulo de IA), rodapé completo, número do processo confirmado, lint limpo na versão com copies.
