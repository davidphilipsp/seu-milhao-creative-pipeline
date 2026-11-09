# Cânone · Kwai venda direta (v1 · 22/10/2026)

Fonte: os 2 roteiros aprovados pelo usuário em `Kwai - Qualificatorios - 22_10.docx`
("Os meus quarenta" e "Cada um no seu"), comparados com a versão que a sala entregou.
Vale para anúncio de venda direta no Kwai (CTA site; sem comunidade de WhatsApp, sem retargeting).
Prevalece sobre o estilo da sala; **não** prevalece sobre `fatos.snapshot.json` nem sobre o lint.

## O que o usuário fez (e vira regra)
1. **Primeira pessoa, sempre.** O apresentador é comprador, não vendedor: "eu peguei", "me custou", "os meus".
   Nada de explicar o produto de fora.
2. **O sonho é do personagem, pequeno e concreto.** "já dou entrada na minha casinha, né". Nunca o sonho de quem assiste.
3. **Um número, um preço, um prêmio.** N números · preço do pacote · R$ 100 mil. Cortar grade de pacotes,
   "tem menor também", CPF, data, "ninguém escolhe, nem eu", explicação de preço por número.
4. **Preço como valor, com "apenas".** "me custou apenas <preço>" logo depois da quantidade.
5. **A causa entra na mesma respiração do preço**, como parte do valor da compra, não como bloco solto
   ("é bom pra mim e é bom pra quem precisa"). Instituição citada pelo nome e como "nossa parceira oficial".
6. **Uma linha de credibilidade, curta.** Loteria Federal + Emissora numa frase. Sem aula.
7. **Oralidade:** "né", "meu velhinho", "tão", "dá", "vai que sai". Ênfase em CAIXA ALTA na frase-tese
   ("QUARENTA CHANCES").
8. **Fecho = callback do gancho + compartilhar + assinatura.** O objeto do 0–2 s volta no fim;
   "já manda esse vídeo pra quem tu ama"; "Vem com o Seu Milhão".
9. **Corte de camadas:** nenhum aviso de "sem pressão", nenhum disclaimer falado (rodapé e 18+ vão no texto da tela).
10. **Esqueleto (≈ 25 s, ≤ 65 palavras faladas):**
    gancho-objeto em 1ª pessoa (0–2) → "vai que sai" + sonho do personagem (2–6) → 1 linha de credibilidade (6–9)
    → quantidade + "apenas" + causa numa respiração (9–18) → callback + compartilhar + assinatura (18–25).

## Onde a versão aprovada esbarra no lint (manter o ritmo, trocar a palavra)
| Escrito | Problema | Troca que mantém o ritmo |
|---|---|---|
| "com essa grana eu mudo de vida" | `mudar_de_vida` | cortar; o concreto ("entrada na minha casinha") já carrega |
| "100% legalizado e chancelado pela EMISSORA" | `chancelada`; quem sorteia é a Loteria Federal | "título da Emissora, com processo na SUSEP. Tudo certinho." |
| "cada cota vendida" | `cota_bilhete` | "cada título" |
| "ganha ganha" | `ganhe` | "bom pra mim e bom pra eles, meu velhinho" |
| "cem mil reais direto no Pix" | `pix_premio` (regulamento não define o meio) | "cem mil reais" |
| "a chance de realizar todos os seus sonhos" | `mudar_de_vida` (promessa a quem assiste) | "Vem com o Seu Milhão." ou "Sonhar não custa nada. Concorrer, quarenta e nove centavos." |
| ~125 palavras em 28 s ("Os meus quarenta") | ≈ 50 s a 2,4 p/s | um bloco ≤ 35 palavras; o total ≤ 65 |

## Variedade obrigatória entre peças
Cada nova peça muda **assunto** (quem é o personagem e qual é o mundo dele) e **ângulo** (por que ele compra 40),
mantendo o esqueleto. Já usados: o próprio celular do Apresentador (compra pessoal), a família à mesa (cada um no seu).
