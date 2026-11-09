# Seu Milhão · AI creative pipeline

A production line for short vertical video ads (9:16), built for **Seu Milhão**, a SUSEP-regulated
philanthropic sweepstakes brand in Brazil. A squad of Claude Code agents writes, directs, audits and
assembles each ad. Still frames and video clips are generated on Google Vertex AI. A local Python package
(`sm`) handles everything mechanical, so the model only spends tokens on judgment.

Code, comments and internal docs are in Brazilian Portuguese. This README is the English entry point.

> Built with Claude Code as a pair programmer.

## The principle: reflex before reasoning

Any repetitive or mechanical task is a `sm` command: plain Python that costs no tokens. Examples are state tracking,
validation, compliance lint, cost sums, ffmpeg/Pillow work, contact sheets, CapCut hand-off and publishing.
The model is used only for judgment: copy, direction, policy nuance and the final visual check.
A task done by hand twice becomes a command on the third time. Each one is logged in
[`sistema_nervoso/REFLEXOS.md`](sistema_nervoso/REFLEXOS.md) with what it replaced and its estimated token savings.

## The flow: 18 steps, 4 human gates

Defined in [`fluxo/passos.yaml`](fluxo/passos.yaml). Each step has an executor, inputs and outputs, dependencies
and a validator (`sm validar <step>`). A step that passes is checked automatically. A step marked **VOCÊ** stops
and waits for the human (`sm aprovar <step>`).

| Line | Steps |
|---|---|
| Planning | P01 creative card · P02 card approved (human) |
| Writing / Direction | P03 *partitura* (exact lines, timing from speech calibration, on-screen text) · P04 *decupagem* (shot list, framing, cut type, style) · P05 take bank search: REUSE or GENERATE |
| Convergence | P06 audit (`sm lint` clean + stamp) · **P07 G1**: script + shot list together |
| Production | P08 start frames · **P09 G2**: frame sheet · P10 Fast 720p tests · P11 inspector pre-filter · **P12 G3**: video per take or batch · P13 finals · P14 assembly (graphics, legal footer, versions with/without copy) · **P15 G4**: assembled sequence |
| Shipping | P16 CapCut hand-off · P17 publish to the private media library · P18 cost close-out |

A local approval panel ([`painel/servidor.py`](painel/servidor.py), localhost only, standard library only) shows the
matrix, steps, frames, takes, sequence and cost. It records gate decisions and never generates anything.

## Agent roster (`.claude/agents/`)

| Agent | Step | Role |
|---|---|---|
| `estrategista` | P01 | segment × angle × style × duration matrix; writes the creative card with observation vs. inference |
| `roteirista` | P03 | turns the card into the *partitura*: exact lines, words/second timing, 6-movement skeleton |
| `diretor` | P04 | turns lines into shots: framing, movement, cut type, REUSE or GENERATE |
| `auditor` | P06 + before every gate | read-only; runs `sm lint` first, then policy nuance. **Can veto** and send work back with a one-line reason |
| `diretor-de-quadros` | P08 | one start frame per generated take (end frame only when needed) |
| `operador-de-video` | P10, P13 | **the only agent that spends on video**, only through `sm veo gerar --confirmar` on the line chief's order |
| `inspetor` | P11, before G4 | contact sheets and crops; automatic discard rules (eye contact, speech, groups, text, deformed hands, wrong coin) |
| `finalizador` | P14, P16 | normalize, last frame, assembly, CapCut hand-off; never generates paid media |
| `bibliotecario` | P17 | the only writer to the media library, and only for creatives that passed G4 |
| `idealizador` | Script Room | ideates script "shells" from hashed inputs; no generation, zero cost |

The main session acts as **line chief**. It reads `sm status` / `sm proximo`, starts the right station,
presents the gates, and never skips one.

## Generation on Vertex AI

[`sistema_nervoso/sm/gerar.py`](sistema_nervoso/sm/gerar.py):
- Frames: `gemini-3.1-flash-image` (Nano Banana 2), 1K, 9:16.
- Video: `veo-3.1-generate-001` (standard), `veo-3.1-fast-generate-001` (fast), `veo-3.1-lite-generate-001`. All are 8 s,
  9:16, no audio, with the start frame plus an optional `lastFrame` for direct-continuity cuts.
- Prompts are built from a style package (`estilos/<style>/bloco.txt`, `negativos.txt`, `licoes.md`) and the shot list.

## Fact base contract

[`memoria/fatos.json`](memoria/fatos.json) is the single source of truth. Every leaf has `valor`, `fonte`
(source) and `data`, with an optional `status` (`confirmado | a_confirmar | bloqueado | estimativa`).
Docs and agents never copy values. They query them with `sm fato <dotted.key>`, and `sm validar` flags a product
value duplicated in docs or agent files. **In this public copy the structure and keys are real, but the values are
examples or placeholders.** Partner, issuer, registration numbers, people, budgets and vendors were replaced. Only the
publicly advertised product terms remain (prize, price, draw date).

## Compliance lint

[`sm lint`](sistema_nervoso/sm/lint.py) checks every text artifact (script, shot list, prompts, on-screen copy):
- **13 banned-phrase regexes** from `fatos.proibidos`, each with a reason and, where one exists, a replacement. They cover
  guaranteed-win language, betting vocabulary, "investment", second-person financial attributes (ad-platform policy),
  wrong product nouns and payout-method claims the regulation does not define.
- Fact checks: prize amount, draw date, registration number, and a required legal footer (`--rodape`).
- A dirty lint means an automatic veto by the auditor.

## Cost control

- **Dry run:** `--seco` simulates every paid step at zero cost, including a full P01–P18 dry run in tests.
- **Confirm:** without `--confirmar`, a paid command only prints model, prompt, estimated cost and spend so far.
- **Lock:** [`sm/trava.py`](sistema_nervoso/sm/trava.py) refuses paid generation, even with `--confirmar`,
  until the user runs `sm liberar-geracao <id>`, one creative at a time.
- **Cap and 80% alert:** [`sm/custo.py`](sistema_nervoso/sm/custo.py) keeps a per-creative ledger, blocks at the
  cap (`tecnica.teto_padrao_conjunto`) and warns at 80%. Estimates use public Vertex AI list prices from
  `tecnica.precos_usd`. Check the current pricing page before relying on them.
- **CapCut hand-off:** [`sm/ponte.py`](sistema_nervoso/sm/ponte.py) writes stable file names, an SRT of the lines,
  a copy guide, a legal footer PNG and a 5-line README for the human editor.

## Script Room (`sala_de_roteiro/`)

An isolated module for ideating script shells (hook plus structure, with place and camera fixed from second zero).
It has its own CLI (`./sala`) and never imports or calls `sm`. See [`CONTRATO.md`](sala_de_roteiro/CONTRATO.md).
- **Isolation:** it writes only inside `sala_de_roteiro/`. Changes to shared files are proposed as diffs.
  [`verificar_isolamento.py`](sala_de_roteiro/ferramentas/verificar_isolamento.py) compares the branch with `main`
  and fails on any file changed outside the allowed areas.
- **Hashed inputs:** [`sincronizar.py`](sala_de_roteiro/ferramentas/sincronizar.py) copies read-only snapshots of
  production inputs and writes `MANIFESTO.json` with per-file SHA-256 and a set hash. It keeps history in `historico/`.
- **Stale detection:** every shell records the `insumos_hash` it used. When production changes, validation marks the
  shell **DESATUALIZADA** (stale) and lists what changed.
- **Validator:** [`validar_casca.py`](sala_de_roteiro/ferramentas/validar_casca.py) is the definition of done. It checks
  required fields, sections and beat table, the lint, timing at the calibrated words/second, allowed origins, take-bank
  reuse and estimated cost.
- **Hook library:** [`hooks/biblioteca_hooks.json`](sala_de_roteiro/hooks/biblioteca_hooks.json) holds **68 hooks**
  from the brand's own scripts and pilots. Each has a family, trigger, physical setting and a **policy classification**
  (`passa` / `passa com ajuste` / `bloqueado`) with the reason and a compliant rewrite. A lexicon
  ([`hooks/lexico.json`](sala_de_roteiro/hooks/lexico.json)) adds extra banned patterns.

## Tests

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e sistema_nervoso pytest
(cd sistema_nervoso && python -m pytest -q)   # sm: 37 tests (1 skipped without the OFL fonts)
python -m pytest sala_de_roteiro/tests -q     # Script Room: 32 tests
```
The P14–P18 dry-run test needs the Anton and Montserrat fonts (SIL OFL, from Google Fonts) in
`biblioteca/referencias/marca/fontes/`. It is skipped when they are missing. Assembly also needs `ffmpeg`.

## Running it with placeholders

```bash
cp .env.exemplo .env            # set GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION
gcloud auth application-default login
./sm status && ./sm proximo     # where the line is and what comes next
./sm vertex                     # access test, no cost
./sm painel                     # local approval panel on 127.0.0.1
./sala estado                   # Script Room status
```
Paid generation stays locked until `./sm liberar-geracao <id>`, and every paid call needs `--confirmar`.

## Security

- No secrets in the repo. `.env` is git-ignored and only `.env.exemplo` with placeholders is published. Use ADC or a
  service-account key kept outside the repository.
- Generated media, the private media library (a separate Git LFS repo), reference footage, likeness and authorization
  files (`fontes/autorizacoes/`), community material and cost ledgers with real amounts are **not** included and are git-ignored.
- The presenter, partner institution, title issuer, registration numbers and budgets are replaced with generic
  placeholders. The decision log is replaced by a summary in [`docs/DECISIONS.md`](docs/DECISIONS.md).
- The panel binds to `127.0.0.1` only. Paid calls require a human order, `--confirmar` and an unlocked creative.
- Third-party skills used locally (see [`creditos.md`](creditos.md)) are credited but not redistributed.
