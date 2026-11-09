# 01 · PLAYBOOK — regras completas

Os valores (preço, prêmio, data, número de processo, redações fixas, preços dos modelos) **não ficam aqui**: estão em `memoria/fatos.json` com fonte e data. Consulte com `./sm fato <chave>`; o lint (`./sm lint`) usa a mesma memória. Decisão nova = registrar em `decisoes.md` e atualizar o fato. Versão de 1 página para os agentes: `01_PLAYBOOK_RESUMO.md`.

## 1. Produto
Chaves: `produto.tipo`, `produto.emissora`, `produto.preco`, `produto.premio`, `produto.sorteio_data`, `produto.sorteio_quem`, `produto.entidade`, `produto.mecanismo`, `produto.escalonamento` (a confirmar), `produto.susep_processo` (status), `produto.promocao_comercial` (bloqueada), `produto.nivel_consciencia`.
Regra: nenhum fato de produto fora dessas chaves; a fonte primária é `biblioteca/regulamento/clausulas-citadas.md`.

## 2. Redações fixas e política
- Redações: `redacoes_fixas.destinacao`, `.sorteio_fala`, `.sorteio_texto`, `.rodape` (e `.rodape_sem_numero`), `.entidade_nome`, `.relacao_com_a_casa` (parceiro).
- Proibidos e substituições: `proibidos.lista` (regex); o lint devolve a substituição quando existe.
- Nenhum atributo de quem assiste em segunda pessoa; situação difícil é de personagem, em terceira pessoa.
- Rodapé legal visível o tempo todo em toda sequência; o número do processo só entra com `produto.susep_processo.status = confirmado`.
- Rótulo "conteúdo gerado por IA" na publicação (`marca.rotulo_ia`).

## 3. Pessoas
`pessoas.adultos_ia` (um por plano, três quartos, sem olhar a lente, sem falar, nunca grupo; imperfeições reais; emoção no pico e curta — v2 de 22/10/2026) · `pessoas.texto_premio_posicao` (moeda ou mão, nunca rosto) · `pessoas.apresentador` (réplica autorizada, única exceção que olha a lente, sem barba, aprovação dele, plano B gravação real) · `pessoas.criancas` (só material real da Instituição, animado sem IA, rosto intacto; status das fotos em `pessoas.fotos_instituicao_status`) · `pessoas.casa_nunca_ia` · `pessoas.voz` (sem TTS; takes sem áudio; narração do Apresentador entra no CapCut).

## 4. Moeda
`moeda.referencia` (verso_scan + M50_ref) · `moeda.frente` (nunca inventar) · `moeda.legibilidade` (o número gravado sempre correto; texto errado legível é descarte) · `moeda.acoes_proibidas` (nunca voando, pilha, chuva, prêmio; uma por plano) · `moeda.banco_central` (lei e cartilha com fonte; Mecir como pendência de veiculação).

## 5. Estilo
- Realismo-celular v2 (22/10/2026): luz chapada ou nublada (céu pode estourar), celular na mão de espectador com tremor constante e horizonte torto, enquadramento imperfeito, primeiro plano atrapalhando, imperfeições reais nas pessoas, saturação baixa e contraste médio-alto; proibidos golden hour, cinematic lighting, beauty, gimbal. Motivo: a referência `referencia-externa-1.mp4` mostra que o realismo vem da montagem, da textura e da gramática de cinegrafista amador.
- O estilo vem do **cartão** (`planejamento/cartoes/<id>.json → estilo`) e do pacote `estilos/<nome>/`: `bloco.txt` idêntico em todo prompt, `negativos.txt`, `paleta.md`, `modelos.md`, `licoes.md`. Nunca fixo no código.
- Nos takes do Apresentador o bloco continua idêntico e o prompt acrescenta a linha literal `Exception for this shot only: the man looks straight into the lens.`
- Texto, número, data, logo e rodapé nunca vêm do gerador (só o número gravado na moeda): entram em `sm montar`. Tipografia em `marca.titulos` / `marca.apoio` / `marca.paleta`; logos só oficiais (`marca.logos`, provisórios).

## 6. Técnica
`tecnica.formato` · `tecnica.codec_master` · `tecnica.codec_biblioteca` · `tecnica.rota` · `tecnica.modelo_teste` · `tecnica.modelo_final_rosto_mao` · `tecnica.modelo_final_lugar` · `tecnica.modelo_imagem` · `tecnica.primeiro_e_ultimo_quadro` (image + lastFrame, 8 s) · `tecnica.precos_usd` (estimativa: reconfirmar na tabela da Vertex e registrar a data) · `tecnica.duracao_trecho` (1–2 s por plano, v2) · `tecnica.ritmo_montagem` · `tecnica.pos_processamento` (`sm tratar-celular` antes da montagem) · `tecnica.licoes_veo` (lista viva; detalhe por estilo em `estilos/<nome>/licoes.md`).

## 6b. Trava de geração
`estilo.trava_geracao` em fatos.json: a geração paga nasce travada; `sm liberar-geracao <id>` (só o usuário) libera um criativo por vez; `sm travar-geracao` fecha. `--seco` não passa pela trava (custo zero).

## 7. Modo de trabalho
- Um criativo por cartão; micro-passos P01–P18 (`docs/03_ESTEIRA.md`). Portões [VOCÊ]: P02 cartão, P07 G1 (partitura + decupagem), P09 G2 (folha única de quadros), P12 G3 (teste), P15 G4 (sequência montada).
- Regra de custo (`tecnica.regra_custo`): **um quadro de início por take** (fim só se o briefing exigir lastFrame), aprovação sim/não; **1 teste** Fast (2º só se o 1º cair); **1 final**. Teto por criativo (`tecnica.teto_padrao_conjunto`), alerta a 80%.
- Ajustes do usuário em **Manter / Mudar / Nunca**: só o Mudar é aplicado; o Nunca vira regra do criativo (e fato, se for geral).
- Linhas paralelas: takes de corte casado rodam em paralelo; continuidade direta em sequência.
- Entrada do roteiro: o usuário preenche `planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md`; `sm importar-roteiro` gera partitura + decupagem; `sm validar roteiro <id>` confere duração, ritmo (1–2 s), função no esqueleto, lint, pessoas, dependências e reuso, com custo só estimado (`planejamento.entrada_roteiro`).
- Regra de ouro do estilo (`estilo.regra_de_ouro`): mundo banal e crível com um único elemento impossível; textura de cinegrafista amador. Referências externas (`estilo.referencias_externas`): só estilo, uso local, sem licença.
- TK-03 é estudo (`planejamento.tk03_status`), não produção.
- Tudo mecânico é `sm` (`docs/04_SISTEMA_NERVOSO.md`); o modelo só julga.

## 8. Descartado (em `_arquivo/`, com motivo)
Estilo 3D de novelinha; ElevenLabs/TTS/clonagem; montagem final com narração sintética; geração em lote sem portão; autoaprovação por folha; elenco infantil fictício; regras antigas de rosto e moeda genérica; 30 fps; scripts v1 substituídos por `sm`.

## 9. Pendências
`sm fato pendencias` lista cada uma com dono e status (termos da Instituição e do Apresentador, origem das fotos, logos, item 2.3 da promoção, correções do site, Banco Central, fotos originais do Apresentador, personas, calibração, cota do LFS).
