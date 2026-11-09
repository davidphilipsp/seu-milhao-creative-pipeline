# Limites de produção (GERADO por ./sala sincronizar; não edite)

Fonte: fatos.snapshot.json, estilos/*/licoes.md, playbook_resumo.snapshot.md. Toda casca precisa caber aqui.

## Vertex / Veo
- Modelos: teste veo-3.1-fast-generate-001, 720p, 8 s · final rosto/mão veo-3.1-generate-001, 1080p, 8 s · final lugar veo-3.1-fast-generate-001, 1080p, 8 s.
- Duração de uso: 1 a 2 s de uso por plano (gera 8 s, usa um trecho curto); a decupagem prevê mais planos por vídeo, dimensionados pela partitura.
- Ritmo: alternar cortes de ~1,2 s com o plano real da criança segurado por mais tempo (respiro emocional).
- Regra de custo: um quadro de início por take (fim só se exigir lastFrame), aprovação sim/não, 1 teste Fast 720p (2º só se o 1º cair), 1 final. Teto padrão US$ 20.0 (alerta 80%).
- Lição: deriva de moeda e rosto depois de ~4,5 s
- Lição: ação precisa pede tempo marcado (0–1 s, 1–3 s…)
- Lição: grupo é bloqueado pelo filtro ou vira rostos indesejados
- Lição: objeto em movimento rápido deforma
- Lição: tentativa bloqueada não é cobrada, mas é registrada
- Lição: texto nunca vem do Veo (só o '50' da moeda)
- Lição: mão erguida para a câmera vira o rosto para a lente e mostra a palma
- Lição: 'come here'/aceno com sorriso abrindo faz o modelo inventar segunda mão e boca aberta: pedir 'other hand out of frame' e 'mouth never opens'
- Lição: o padrão 1080p não reproduz o Fast quadro a quadro
- Lição: Nano Banana insere texto a menos que o prompt diga 'nothing written'; cota por minuto (429)

## Pessoas
- Adultos por IA: um por plano, de três quartos, sem olhar para a lente, sem falar, nunca em grupo (limite da Vertex); pessoas comuns brasileiras de idades e corpos variados, com imperfeições reais (rugas, manchas, dentes desalinhados, cabelo bagunçado, roupa amassada), tons de pele diversos; expressão: EMOÇÃO NO PICO E CURTA (gargalhada, susto, olho marejado), não mais contida; nunca grupo gerado na Vertex (filtro bloqueia).
- Apresentador: réplica digital autorizada do apresentador da marca; única exceção que olha para a lente; não fala; ficha de referência na biblioteca privada; aprovação dele obrigatória (folha de comparação); plano B: gravação real.
- Crianças: só material real da Instituição Parceira, com termo, animado sem IA generativa (zoom, deslize, parallax só no fundo, rosto intacto); nenhuma descrição de traço facial para geração.
- Instituição: a Instituição Parceira (fachada, interior, logo) nunca é gerada por IA.
- Voz: sem TTS, sem clonagem; takes sem áudio; narração real do apresentador entra na edição (CapCut).
- Texto de prêmio: só sobre a moeda ou a mão; nunca colado em rosto.

## Moeda
- moeda de 50 centavos do Real (verso): scan de referência na biblioteca privada.
- nunca inventar; sem frente.jpg a moeda aparece de verso ou de perfil.
- o '50' sempre correto; texto errado legível é descarte; CENTAVOS e ano podem ficar ilegíveis, nunca errados.
- nunca voando, em pilha, em chuva ou virando prêmio; uma moeda por plano.
- Banco Central: Lei 4.511/1964, art. 13 (proíbe impressos que se assemelhem a cédulas ou moedas); cartilha do BCB manda submeter publicidade com reprodução de cédulas ao Mecir; prática segura: submissão prévia ao Mecir antes da veiculação; não impede testes.

## Estilo e texto
- Regra de ouro: mundo banal e crível com um único elemento impossível; textura de cinegrafista amador.
- Texto, número, data, logo e rodapé nunca vêm do gerador (só o '50' da moeda): entram na montagem.
- Rótulo IA: rótulo 'conteúdo gerado por IA' obrigatório na publicação no Meta.

## Lições · realismo-celular
- Trecho de uso de 3 a 4 s: moeda e rosto derivam depois de ~4,5 s.
- Ação com tempo marcado (0–1 s / 1–3 s / 3–4 s / 4–8 s); uma ação por take.
- Grupo é bloqueado pelo filtro ou vira rostos indesejados: um adulto por plano; transeuntes só longe e de costas.
- Mão erguida para a câmera vira o rosto para a lente e mostra a palma: fechar a mão no lugar, sem subir.
- "Gesto de vem" + sorriso abrindo faz o modelo inventar aceno com a outra mão e boca aberta: `the other hand stays out of frame; the mouth never opens wide`.
- O padrão 1080p não reproduz o Fast quadro a quadro: o Mudar tem de ir no teste e na final com a mesma redação.
- Nano Banana insere texto a menos que o prompt diga `nothing written anywhere`; feiras pedem `no price tags, no cardboard signs`.
- Sombras de roupa escura caem abaixo de #332F40: levantar com curva por canal e máscara no rosto (T1 do TK-03).
- Texto nunca vem do Veo; só o "50" gravado na moeda.
- (G3 do TK-03, 21/10) No Fast, as restrições têm de estar na linha da ação, não só no fecho: "exactly ONE coin", "eyes stay on the coin, head never turns to the camera", "lips stay together, mouth never opens", "no other hand". Promovido ao template de `sm veo gerar`.
- Palma × dorso da mão erguida: o Veo mostra a palma mesmo pedindo o dorso (A4 na v1, T5 no TK-03). Casar por posição e ângulo; aceitar palma.
- (v2, 22/10) A referência referencia-externa-1.mp4 mostra que o realismo vem da MONTAGEM (cortes de ~1,2 s, emoção no pico, plano real segurado como respiro), da TEXTURA (compressão de celular, grão, saturação baixa, céu estourado) e da GRAMÁTICA DE CINEGRAFISTA AMADOR (tremor, horizonte torto, enquadramento imperfeito, celulares e ombros atrapalhando). O gerador entrega o plano; `sm tratar-celular` entrega a textura; a decupagem entrega o ritmo.

