# 03 · Esteira

```
 CARTÃO ──► ROTEIRISTA (partitura) ─┐
   P01/P02                          ├──► AUDITOR ──► [G1 VOCÊ] ──► DIRETOR-DE-QUADROS ──► [G2] ──► OPERADOR (teste) ──► INSPETOR ──► [G3]
            DIRETOR (decupagem) ────┘   sm lint      P07           sm quadro             P09       sm veo            sm inspecionar  P12
            + sm banco buscar (P05)     P06                        P08                             P10              P11
 ──► OPERADOR (final) ──► FINALIZADOR (sm montar) ──► [G4 VOCÊ] ──► FINALIZADOR (sm ponte) ──► BIBLIOTECÁRIO (sm publicar) ──► sm custo fechar
     P13                  P14                         P15           P16                        P17                             P18
 Chefe de linha: sm status / sm proximo, aciona estações, apresenta portões, nunca gera, nunca pula portão.
```

## Estações (`.claude/agents/`)
| Estação | Linha | Entrada → saída | Reflexos que usa | Dinheiro |
|---|---|---|---|---|
| chefe-de-linha (sessão) | — | `sm status`, `sm proximo` → aciona estação, apresenta portão | `sm validar`, `sm aprovar`, `sm pendente` | nunca |
| estrategista | Planejamento | matriz + segmentos → cartão (P01) | `sm fato`, `sm validar P01` | não |
| roteirista | Redação | cartão → `partitura.json` (P03) | `sm fato`, `sm lint`, `sm partitura validar` | não |
| diretor | Direção | partitura → `decupagem.json` (P04) | `sm decupagem validar`, `sm banco buscar` | não |
| auditor | Convergência | partitura + decupagem (+ prompts, quadros) → carimbo ou veto (P06) | `sm lint`, `sm fato` | não |
| diretor-de-quadros | Produção | decupagem → um quadro de início por take GERAR (+ fim se exigir) (P08) | `sm quadro gerar --confirmar`, `sm folha quadros` | centavos |
| operador-de-video | Produção | quadros → testes (P10) e finais (P13) | `sm veo gerar --modo teste\|final --confirmar` | **único em vídeo** |
| inspetor | Produção | tomadas → passou/descartada com motivo (P11, e nas finais) | `sm inspecionar`, `sm tira-moeda`, `sm folha` | não |
| finalizador | Produção/Expedição | finais → sequência com e sem copies (P14), ponte (P16) | `sm padronizar`, `sm ultimo-quadro`, `sm montar`, `sm ponte` | não |
| bibliotecario | Expedição | criativo com G4 → biblioteca (P17) | `sm publicar` | não |

## Portões [VOCÊ]
P02 cartão · P07 **G1** partitura + decupagem juntas · P09 **G2** folha única de quadros (um por take, sim/não) · P12 **G3** vídeo de teste (take a take só nos de continuidade direta; corte casado em lote) · P15 **G4** sequência montada. Reprovação volta para a estação indicada na nota, com Manter / Mudar / Nunca; só o Mudar é aplicado.

## Convergência por fichas
Cada estação escreve `criativos/<id>/esteira/<estacao>_<passo>.json`: `entrada`, `saida`, `arquivos`, `decisoes`, `pendencias`, `status`, `para`. O auditor acrescenta `veredito` (carimbado | vetado) e `motivo` (1 linha). O inspetor acrescenta `passou` e `descartes`. A estação seguinte lê só a ficha anterior, o RESUMO e o cartão.

## Devoluções
Auditor e inspetor devolvem com motivo em uma linha. Validador falhou 2 vezes: PARE e mostre o erro em 3 linhas. Segunda tomada de teste só se a primeira cair; não há terceira: o take volta ao chefe.

## Trava
Nenhuma geração paga roda sem `sm liberar-geracao <id>` do usuário (um criativo por vez); `sm quadro`/`sm veo` respondem 'geração travada: aguardando roteiro aprovado'.

## Ligações
`corte_seco` (outra cena sem casamento; o ritmo liga) · `continuidade_direta` (início = último quadro aprovado do take anterior, `sm ultimo-quadro`) · `corte_casado` (outra cena; posição e escala da mão, moeda ou sorriso casam; declarado em `casa_com`) · `abertura` · `fecho`.

## Comandos do chefe
`./sm importar-roteiro <md>` · `./sm validar roteiro <id>` · `./sm validar coerencia` · `./sm liberar-geracao <id>` / `./sm travar-geracao` · `./sm status` · `./sm proximo` · `./sm validar P05 --id TK-03` · `./sm pendente P07` · `./sm aprovar P07 "nota"` · `./sm aprovar P07 --reprovar "Mudar: …"` · `./sm custo` · `./sm painel`.
