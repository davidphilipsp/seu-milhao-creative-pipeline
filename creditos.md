# Créditos e licenças

## Ferramentas e métodos

| Item | Autor / origem | Licença | Uso neste projeto |
|---|---|---|---|
| visual-skills (`video`, `image`) | **Serge Shima — github.com/smixs/visual-skills** (t.me/aimastersme · sergeshima.com · aimasters.me) | CC BY 4.0 — atribuição obrigatória | Direção de cinema e sintaxe de prompts para Veo e Nano Banana. Usadas localmente em `.claude/skills/`; **não incluídas** neste repositório público (instale a partir do repositório original). |
| ai-video-skill | Advait Jayant — github.com/0xadvait/ai-video-skill | MIT | Só o método (prompt em 5 partes, validação, folha de contato, QC, lições). Não incluída neste repositório público. |
| HyperFrames | HeyGen — github.com/heygen-com/hyperframes | Open source | Montagem e render (HTML + GSAP). Versão fixada: 0.8.181. |
| whisper.cpp | ggerganov — github.com/ggml-org/whisper.cpp | MIT | Transcrição local com tempo por palavra (via `npx hyperframes transcribe`). |
| FFmpeg | ffmpeg.org | LGPL/GPL | Tratamento de áudio e vídeo. |

## Fontes tipográficas
(a registrar na Fase 5, com licença)

## Trilhas e efeitos
(nenhum na v1, salvo decisão em contrário; se usar, só com licença comercial explícita para anúncio)

## Fontes tipográficas (registro, 20/10/2026)
| Fonte | Uso | Licença | Situação |
|---|---|---|---|
| Montserrat (Google Fonts) | títulos 900/800, textos 400/700, legendas | SIL Open Font License 1.1 (uso comercial livre) | só o nome registrado; arquivos serão baixados do Google Fonts para `composition/assets/fonts/` na Fase 5, com a licença copiada junto |
| Inter (Google Fonts) | botões 700 | SIL Open Font License 1.1 | idem |
| Anton (Google Fonts) | opcional, título ouro 3D estilo pôster, só se o usuário escolher | SIL Open Font License 1.1 | idem |

A prancha `biblioteca/estilo/prancha-1080x1920.png` carregou as fontes direto do Google Fonts para visualização; nenhum arquivo de fonte foi salvo no projeto.

Papéis fechados pelo usuário (20/10/2026): **Anton** nos títulos de tela; **Montserrat 800** na legenda, nos textos de apoio e no rodapé. Ambas SIL OFL 1.1. Inter não entra no vídeo.

## Arquivos de fonte no projeto (20/10/2026)
Baixados do repositório oficial do Google Fonts (github.com/google/fonts, pasta `ofl/`) para `criativos/N1-01/composition/assets/fonts/`, com a licença ao lado:
- `Anton-Regular.ttf` + `Anton-OFL.txt` — Copyright 2020 The Anton Project Authors, SIL Open Font License 1.1.
- `Montserrat-wght.ttf` (variável) + `Montserrat-OFL.txt` — The Montserrat Project Authors, SIL Open Font License 1.1.
Uso: grafismos, gabarito e faixa de legenda. Licença livre para uso comercial; os arquivos de fonte ficam fora do git (`fontes/marca/fontes/` também).
Logos no kit: provisórios, copiados do site; substituir pelos originais do designer. GSAP 3.14.2 (CDN jsdelivr) é usado pelo HyperFrames na composição.

## Missão v2 (realismo)
- Referência de estilo: vídeo de IA realista baixado pelo usuário (`fontes/referencia/realismo/`, fora do git); usado só para medir luz, cor e enquadramento; nenhum quadro reutilizado.
- Quadros iniciais e moeda de referência: Nano Banana 2 (Vertex AI). Clipes: Veo 3.1 (Vertex AI). Rótulo de "conteúdo gerado por IA" obrigatório no Meta.

## Esteira (21/10/2026)
| Item | Origem | Licença | Uso |
|---|---|---|---|
| Git LFS 3.8.0 | git-lfs.com (Homebrew) | MIT | mídia da biblioteca |
| GitHub CLI (`gh`) | cli.github.com | MIT | criação do repositório e publicação |
| Painel local (`painel/`) | produção própria, só biblioteca padrão do Python | — | aprovação dos portões em localhost |
Fontes Anton e Montserrat (SIL OFL 1.1) agora catalogadas em `biblioteca/referencias/marca/fontes/` com a licença ao lado.
