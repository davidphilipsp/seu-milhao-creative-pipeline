# (v1, 20/10/2026) Realismo de celular — análise da referência realista-30s

Fonte: `fontes/referencia/realismo/referencia-realista-30s.mp4` (720×720, 24 fps, 30 s; vídeo de IA realista baixado pelo usuário). Quadros em `quadros/`, folha em `folha-contato.jpg`. **Uso só como estilo.** Nunca entra como primeiro quadro. Não se reproduz: a lanchonete, logos e o arco dourado; uniformes de marca; o enquadramento sexualizado (quadros 19–21, excluídos da medição); o cavaleiro.

## O que o olho vê
- **Câmera:** celular na mão, altura dos olhos, grande-angular leve (24–28 mm equivalente), foco profundo com o fundo todo legível (balcões, cadeiras, pessoas ao fundo), leve respiração de câmera, motion blur natural nos movimentos rápidos. Nada de dolly, nada de rack focus.
- **Luz:** luz prática do lugar (fluorescente do teto, painéis luminosos, vitrine), sombras suaves e abertas, realces que estouram no branco sem drama. Sem key light, sem contraluz desenhado.
- **Cor:** saturação moderada, cores do cotidiano (azul do uniforme, vermelho dos assentos, bege das mesas), sem teal-orange, sem gradação de cinema; o preto nunca é puro.
- **Pele:** textura visível, poros, brilho de oleosidade no nariz e testa, tons diversos; mãos com veias; unhas curtas.
- **Expressão:** contida, de quem está trabalhando; nenhum "ator"; ninguém olha para a lente com pose de depoimento.
- **Ambiente:** lugar comum, cheio de detalhes legíveis, gente ao fundo fazendo a própria vida, de costas ou de lado.

## Valores medidos (quadros 1–18 e 22–25, por amostragem de pixels)
| Item | Medido | Valor de partida do usuário | Uso nos prompts |
|---|---|---|---|
| Sombras (10% mais escuros) | #272230 | #332F40 | sombras azuladas-arroxeadas, nunca #000 (0% de preto puro no vídeo) |
| Meios-tons | #7C5C5B (cena inteira) | #9E7E7B · #BDA69B | tons quentes acinzentados; os valores do usuário valem para superfícies claras |
| Altas luzes | #EBD2C7 | — | branco quente, estourado sem azular |
| Pele | clara #C7A68D · média #997159 · escura #583125 | #ECC9B2 a #573831 | faixa toda cabe na regra "do retinto ao claro" |
| Saturação média (HSV) | 0,35 | moderada | pedir "moderate saturation" |
| Contraste (desvio da luminância) | 55 de 255 | médio | sem crush de preto, sem "cinematic" |
| Dominantes | #24243C, #846C6C, #6C3C24, #B49C84 | — | azul-escuro das sombras, bege-rosado das superfícies, castanhos de pele e madeira |

## Como isso vira prompt
Bloco de estilo fixo em `realismo_bloco.txt` (em inglês, idêntico em todos os prompts do Veo e dos quadros iniciais). Em resumo: footage de celular, handheld na altura dos olhos, 24–28 mm, foco profundo, luz prática, sombras suaves, saturação moderada, pessoas brasileiras comuns com pele texturizada, expressões contidas, e os negativos (animação, 3D, cartoon, Pixar, plástico, pele lisa, cinematic, bokeh, logo, marca, texto, fast food, golden arches, criança, olhar para a lente).

## O que muda em relação ao 3D de novelinha (v1)
- Fundo legível em vez de desfoque; objetos reais e gastos em vez de formas arredondadas.
- A moeda é uma só, definida em imagem de referência, com riscos e sem inscrição.
- Pessoas aparecem (uma ou duas por plano), mas só de perfil, de costas, parciais ou fora do centro; nunca olhando para a lente; nunca em S04 e S08.
