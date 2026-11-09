# corpus/ (empty in the public repo)

This folder holds plain-text extracts of the brand's internal reference material, produced by
`./sala sincronizar --corpus <folder>`:

| File | Source pattern | What it is |
|---|---|---|
| `roteiros_100mil_atemporal.txt` | `ROTEIROS*Atemporal*.pdf` | past ad scripts (angle, tone, hook, trigger) |
| `mensagens_comunidade.txt` | `Mensagem*Comunidade*.pdf` | community/group broadcast messages |
| `meta_comunidade.txt` | `Meta*Comunidade*.docx` | community goals and guidelines |

The originals are private business documents and are **not** published. The SHA-256 of each original
is recorded in `../MANIFESTO.json` so the Script Room can detect when a source changed.
To run the full sync, place your own PDFs/DOCX matching the patterns above in a folder and pass it with `--corpus`.
