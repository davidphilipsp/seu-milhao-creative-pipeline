# PLAYBOOK · RESUMO (1 página; é o que cada agente lê)

**Valores nunca de cabeça:** `./sm fato <chave>` (ex.: `produto.premio`, `redacoes_fixas.rodape`, `tecnica.modelo_teste`). Texto novo passa por `./sm lint <arquivo>` antes do auditor.

**Produto:** título de capitalização, modalidade filantropia premiável; emissora, preço, prêmio, data e quem sorteia em `produto.*`. Cessão integral do resgate à Instituição (`produto.mecanismo`). Promoção comercial bloqueada. Nível 1: o anúncio vende o mundo; prêmio e data só como fato da memória.

**Redações fixas:** destinação, sorteio (fala e texto), rodapé, nome da entidade, "parceiro" — `redacoes_fixas.*`, copiadas literalmente.

**Proibidos:** `proibidos.lista` (ganhe→concorre, aposta, ganho certo, transformar sua vida, vai direto, cota/bilhete→título, sócio/patrocinador→parceiro, não perde nunca, Pix+prêmio, sorteio pela Emissora, "loteria" como nome, investimento, atributo de quem assiste em 2ª pessoa).

**Pessoas:** um adulto por plano, três quartos, sem olhar a lente, sem falar, nunca grupo; imperfeições reais (rugas, dentes desalinhados, cabelo bagunçado, roupa amassada), idades e corpos variados; emoção no pico e curta (gargalhada, susto, olho marejado). Texto de prêmio só sobre moeda ou mão. Apresentador: única exceção que olha a lente, sem barba, não fala, aprovação dele, plano B gravação real. Crianças: só foto real da Instituição animada sem IA (status em `pessoas.fotos_instituicao_status`). A Instituição nunca é gerada.

**Moeda:** 50 centavos de verso (referência catalogada); frente nunca inventada; número gravado sempre correto; uma por plano; nunca voando, pilha, chuva ou prêmio. Mecir = pendência de veiculação.

**Estilo:** do cartão → `estilos/<nome>/bloco.txt` idêntico em todo prompt + `negativos.txt` (realismo-celular v2: luz chapada/nublada, tremor, horizonte torto, primeiro plano atrapalhando, saturação baixa); exceção literal do olhar só nos takes do Apresentador. Texto/logo/rodapé só em `sm montar`.

**Técnica:** formato, codecs, modelos de teste e final, image + lastFrame (8 s), preços e lições em `tecnica.*`. Trecho de uso 1–2 s por plano (mais planos por vídeo); ritmo: cortes de ~1,2 s alternados com o plano real da criança segurado. Antes da montagem: `sm tratar-celular` (tremor, curva, grão, compressão). Teste Fast 720p; final padrão 1080p (rosto, mão com moeda) ou Fast 1080p (lugar).

**Custo:** um quadro de início por take (fim só com lastFrame); 1 teste (2º só se o 1º cair); 1 final. Geração só por `sm quadro gerar --confirmar` (diretor-de-quadros) e `sm veo gerar --confirmar` (operador). Teto por criativo, alerta a 80%. `--seco` simula.

**Fluxo:** P01 cartão → P02 [VOCÊ] → P03 partitura → P04 decupagem → P05 banco → P06 auditoria → P07 [VOCÊ] G1 → P08 quadros → P09 [VOCÊ] G2 → P10 testes → P11 inspeção → P12 [VOCÊ] G3 → P13 finais → P14 montagem → P15 [VOCÊ] G4 → P16 ponte → P17 publicação → P18 custo. Cada estação escreve uma ficha JSON em `criativos/<id>/esteira/` e responde ao chefe em ≤ 5 linhas. Ajustes do usuário: Manter / Mudar / Nunca (só o Mudar é aplicado).

**Trava:** geração paga só com `sm liberar-geracao <id>` dado pelo usuário (um criativo por vez); `sm quadro`/`sm veo` recusam com a trava fechada. **Regra de ouro do estilo:** mundo banal e crível com um único elemento impossível; textura de cinegrafista amador (`estilo.regra_de_ouro`). Referências externas (cavaleiro, referencia-externa-1) só estilo, uso local, sem licença. **Entrada do roteiro:** `planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md` → `sm importar-roteiro` → `sm validar roteiro <id>`.

**Nada se apaga; nada se inventa:** fato sem fonte não entra; o que sai vai para `_arquivo/`.
