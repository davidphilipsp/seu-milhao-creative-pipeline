"""Expedição CapCut: ponte_capcut/<id>/ com nomes estáveis, partitura.srt, guia_copies.srt, rodape_legal.png, LEIA-ME (5 linhas)."""
import shutil
from .raiz import raiz, criativo_dir, ler_json, rel, hoje
from .memoria import fato
from .midia import probe
from .montar import rodape_png


def srt_ts(s):
    h = int(s // 3600); m = int(s % 3600 // 60); x = s % 60
    return f"{h:02d}:{m:02d}:{x:06.3f}".replace(".", ",")


def ponte(cid) -> str:
    d = criativo_dir(cid); dec = ler_json(d / "decupagem.json"); part = ler_json(d / "partitura.json")
    dest = raiz() / "ponte_capcut" / cid; dest.mkdir(parents=True, exist_ok=True)
    ap = d / "aprovados"
    n, t0, guia, linhas = 0, 0.0, [], []
    for i, t in enumerate(dec["takes"], 1):
        src = ap / f"{t['id']}_take.mp4"
        if not src.exists(): linhas.append(f"{i:02d}_take.mp4 {t['id']} — AINDA NÃO APROVADO"); continue
        n += 1; shutil.copy(src, dest / f"{i:02d}_take.mp4")
        dur = probe(src)["duracao"]
        falas = {f["id"]: f for f in part["falas"]}
        txt = " / ".join(x for x in [t.get("titulo_tela", "")] + [falas[f].get("texto_tela", "") for f in t["falas"] if f in falas] if x) or "(sem copy)"
        guia.append(f"{n}\n{srt_ts(t0)} --> {srt_ts(t0 + dur)}\n{t['id']} · {txt}\n")
        linhas.append(f"{i:02d}_take.mp4 {t['id']} {dur:.2f}s copy: {txt}"); t0 += dur
    for nome in ("sequencia.mp4", "sequencia_copies.mp4"):
        if (ap / nome).exists(): shutil.copy(ap / nome, dest / nome)
    (dest / "guia_copies.srt").write_text("\n".join(guia) + ("\n" if guia else ""), encoding="utf-8")
    # partitura.srt: falas nos tempos (para gravar e encaixar a narração)
    srt, t = [], 0.0
    for k, f in enumerate(part["falas"], 1):
        dur = float(f["duracao_s"])
        srt.append(f"{k}\n{srt_ts(t)} --> {srt_ts(t + dur)}\n{f['texto']}\n"); t += dur + float(f.get("respiro_s", 0))
    (dest / "partitura.srt").write_text("\n".join(srt) + "\n", encoding="utf-8")
    rodape_png(dest / "rodape_legal.png")
    (dest / "LEIA-ME.txt").write_text(
        f"{cid} · {part.get('titulo', '')} · gerado em {hoje()} · 1080×1920 24 fps sem áudio; rodapé legal (rodape_legal.png) em y=1408 o tempo todo.\n"
        f"Takes na ordem: {' · '.join(l.split(' ')[0] + '=' + l.split(' ')[1] for l in linhas)}.\n"
        "sequencia.mp4 = takes emendados a seco; sequencia_copies.mp4 = com títulos e rodapé; guia_copies.srt = tempo de cada copy.\n"
        "partitura.srt = falas nos tempos para gravar a narração do Apresentador e encaixar no CapCut.\n"
        "Pendências de veiculação: ver `sm fato pendencias` (termos, Mecir, logos, rótulo IA).\n", encoding="utf-8")
    return f"ponte {cid}: {n} takes · sequência {t0:.2f} s · {rel(dest)}"
