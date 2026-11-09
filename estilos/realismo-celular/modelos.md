# Modelos · realismo-celular

Fatos em `sm fato tecnica.modelo_teste`, `tecnica.modelo_final_rosto_mao`, `tecnica.modelo_final_lugar`, `tecnica.modelo_imagem`, `tecnica.precos_usd`.

| Uso | Comando | Observação |
|---|---|---|
| Quadro de início/fim | `sm quadro gerar <id> <take> [--fim] --confirmar` | Nano Banana 2, 1K, 9:16, refs: M50_ref (+ prints do Apresentador quando o take tem `apresentador`) |
| Teste | `sm veo gerar <id> <take> --modo teste --confirmar` | Fast 720p, 8 s, image + lastFrame se existir `_fim.png`; 1 tomada (2ª só se a 1ª cair) |
| Final (rosto, mão com moeda) | `sm veo gerar <id> <take> --modo final --confirmar` | padrão 1080p (o Fast reprovou em mão com moeda no comparativo de 20/10) |
| Final (lugar, objeto parado) | idem, take com `modelo: veo-3.1-fast-1080p` | Fast 1080p |
| Foto real da Instituição | `sm animar-foto <foto> <saida>` | sem IA generativa |

`--seco` em `sm quadro` e `sm veo` simula sem custo (placeholders) para testar a esteira.
