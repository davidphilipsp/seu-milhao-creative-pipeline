# 05 · Biblioteca e banco de takes

- **Repositório:** `<owner>/<private-library-repo>` (privado, Git LFS para mp4/mov/png/jpg/jpeg/webp/pdf/woff2/ttf/otf). Clone de trabalho: `biblioteca/` (ignorado pelo git da produção). Só o **bibliotecario** escreve e só por `sm publicar`.
- **Índice:** `README.md` (gerado, miniaturas por seção) · `CATALOGO.md` (gerado) · `catalogo.json` (fonte).

## Estrutura
`referencias/{estilo,moeda50,apresentador,instituicao,marca}` · `regulamento/` · `playbook/` (cópia versionada de 01_PLAYBOOK e 03_ESTEIRA) · `aprovados/<id>/` (**somente G4**: `takes/NN_take.mp4` sem texto e `NN_take_copies.mp4` com texto, `sequencia*.mp4`, `partitura.srt`, `guia_copies.srt`, `rodape_legal.png`, `copies.txt`, `FICHA.md`).

## Catálogo (`catalogo.json`)
Item: `id`, `tipo` (imagem | video | documento | fonte | texto | prompt | captura), `caminho`, `origem`, `licenca`, `autorizacao` (sim | nao | pendente), `status` (liberado | provisorio | bloqueado), `data`, `take_origem`, `tags` (vocabulário fechado de `memoria/glossario.json → tags`: segmento, angulo, lugar, elemento, acao, estilo, duracao, ligacao, modelo), `nota`.
Todo take aprovado vira ativo reutilizável com essas tags; `sm banco buscar` marca REUSO quando lugar, elemento e ação batem com um item `video` liberado.

## O que nunca entra
Termos e autorizações; tomadas reprovadas, testes 720p, rascunhos, quadros não escolhidos; prompts com chaves; `.env`; qualquer item sem origem e licença; vídeos de referência de terceiros sem licença (ficam em `fontes/referencia/`); vídeos dos pilotos anteriores.

## Proteção (`biblioteca/.githooks/pre-commit`, versionado)
Bloqueia: item em `aprovados/<id>/` sem G4 no estado do criativo (`criativos/<id>/estado.json`: P15 ok ou portão G4 aprovado); qualquer caminho `autorizacoes/`; mídia fora do LFS; arquivo sem entrada no catálogo. `sm validar R13` cria três arquivos proibidos, confere a recusa e limpa. Nunca `--no-verify`.

## Espaço
Masters CRF 16 ficam na produção; a biblioteca recebe CRF 18. `sm publicar` imprime o uso do LFS e avisa a 80% da cota em `biblioteca/.lfs-cota` (confirmar a cota real em github.com/settings/billing: `sm fato pendencias.cota_lfs`).

## Migração feita (21/10/2026)
Referências válidas catalogadas e publicadas (estilo, moeda, Apresentador com 3 prints provisórios, fotos da Instituição com status, marca, regulamento e consultas); T1 do TK-03 publicado com FICHA marcando "aprovado para produção, não liberado para veiculação" até os termos. Nenhum vídeo antigo.
