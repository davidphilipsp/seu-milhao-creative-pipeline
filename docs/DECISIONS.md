# Key decisions (public summary)

The private decision log (`decisoes.md`) holds dated entries with people, partners, budgets and
production details, so it is not published. These are the engineering decisions it records, without those details.

| Decision | Why |
|---|---|
| One source of truth for facts (`memoria/fatos.json`, every leaf with value, source and date) | Docs and agents kept drifting on prize, date and legal footer wording. Docs point to keys and never copy values; `sm validar` flags a duplicated product value in docs or agent files. |
| Reflex before reasoning | Mechanical work (state, validation, lint, ffmpeg, cost sums, publishing) became `sm` commands. The model judges only copy, direction, policy nuance and the final visual check. A task done by hand twice becomes a command on the third time, logged in `sistema_nervoso/REFLEXOS.md`. |
| Only the video operator spends on video; the frame director spends on still frames | Paid calls go through `sm quadro gerar` / `sm veo gerar` with `--confirmar` and a human order at a gate. When a prompt is already stamped and no judgment is needed, the line chief runs the command directly instead of starting a subagent just to type it. |
| Generation lock | `fluxo/estado.json → geracao_liberada=false` by default. Paid generation refuses even with `--confirmar` until the user runs `sm liberar-geracao <id>`, one creative at a time. `--seco` (dry run, zero cost) bypasses the lock. |
| Cost rule per take | One start frame (end frame only if the shot needs `lastFrame`), yes/no approval, one Fast 720p test (a second only if the first is rejected), one final. Per-creative cap with an alert at 80%. |
| First and last frame on Veo | Vertex AI accepts `image` + `lastFrame` on Veo 3.1 (8 s). This is used for direct-continuity cuts. |
| The auditor can veto | `sm lint` dirty = automatic veto with the lint line. Policy nuance (ad platform policy, regulation, central-bank rules on currency images, image rights) is judged on top. |
| No generated children, no generated partner premises | Children appear only in real, authorized photos animated without generative AI. Adult AI faces: one per shot, three-quarter view, not looking at the lens, not speaking. |
| Script Room isolated from production | Ideation runs on hashed snapshots of production inputs, writes only inside `sala_de_roteiro/`, and proposes changes to shared files as diffs. A stale-input check compares the shell's input hash with `MANIFESTO.json`. |
| Media library outside this repo | Approved media lives in a separate private Git LFS repository with a pre-commit hook (gate G4, authorizations, LFS, catalog). Likeness and authorization files never go to any remote. |
