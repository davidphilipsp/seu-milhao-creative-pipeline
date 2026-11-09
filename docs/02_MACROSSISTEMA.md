# 02 · Macrossistema

## A matriz (`planejamento/matriz.json`)
Eixos: **SEGMENTO** (popular · classe_media · alto_ticket) × **ÂNGULO** (solidario · aspiracional) × **ESTILO** (`estilos/`) × **DURAÇÃO** (≤ 30 s). Cada célula tem um cartão (`planejamento/cartoes/<id>.json`) com hipótese de criativo e de mídia, confiança (alta/média/baixa) e o par observação × inferência. Hoje: 6 cartões (TK-03 = estudo-v1 concluído; os outros em rascunho; o próximo entra pelo roteiro quadro a quadro).

## Segmentos (`planejamento/segmentos/`)
- **popular** (confiança alta): P1–P5 do corpus; realismo de celular; ticket unitário. Regra: concretude e pertencimento.
- **classe_media** (média): sonho tangível, praticidade, transparência; ticket intermediário; registro urbano neutro; estilo a definir.
- **alto_ticket** (baixa): impacto e legado, destinação, provas regulatórias; ticket alto; registro sóbrio. Regra: contribuição maior para a causa, nunca compra em volume para ganhar (movimento 5 suspenso).

Personas P1–P5: rótulos do corpus, sem definição escrita (`sm fato pendencias.personas`). O estrategista não inventa perfil; registra a lacuna.

## Linhas paralelas
- **Linha 1 · Redação** (roteirista): cartão → `partitura.json`.
- **Linha 2 · Direção** (diretor): partitura → `decupagem.json` (takes, ligações, REUSO/GERAR, estilo).
- **Convergência**: auditor (`sm lint` + nuance) → G1 (partitura + decupagem juntas).
- **Produção**: quadros → G2 → testes → inspeção → G3 → finais → montagem → G4.
- **Expedição**: ponte CapCut → biblioteca → custo fechado.
Ritmo (`tecnica.ritmo_montagem`): 1–2 s por plano, cortes de ~1,2 s; respiro mais longo só no plano real da criança. Regra de ouro do estilo (`estilo.regra_de_ouro`): mundo banal e crível com um único elemento impossível. Takes de **corte casado** rodam em paralelo (independentes); **continuidade direta** roda em sequência (o último quadro alimenta o próximo).

## Banco de takes
Todo take com G4 vira ativo reutilizável na biblioteca, com tags do glossário (segmento, ângulo, lugar, elemento, ação, estilo, duração, ligação) e versão sem texto. `sm banco buscar <id>` casa a decupagem com o catálogo: **REUSO** quando as tags batem, **GERAR** quando não. Reuso é custo zero.

## Como um criativo nasce
0. O usuário entrega o roteiro quadro a quadro (`planejamento/modelos/ROTEIRO_QUADRO_A_QUADRO.md` → `sm importar-roteiro` → `sm validar roteiro`), que já traz cartão, partitura e decupagem; ou
1. O estrategista escolhe a célula e escreve o cartão (P01); o usuário aprova (P02).
2. Roteirista e diretor trabalham em paralelo sobre o cartão (P03, P04); o banco marca o reuso (P05).
3. Auditor converge (P06); G1 do usuário (P07).
4. Produção take a take com os portões G2–G4; expedição e publicação.
Detalhe dos passos: `docs/03_ESTEIRA.md` e `fluxo/passos.yaml`.
