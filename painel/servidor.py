#!/usr/bin/env python3
"""Painel local da máquina de criativos. Só 127.0.0.1. Lê fluxo/estado.json e criativos/*/estado.json; escreve via `sm aprovar` e ajustes. Nunca gera.
Rotas: /  /api/fluxo  /api/criativo?id=  /api/biblioteca?q=  POST /api/acao  /midia/<caminho>  /thumb/<caminho>"""
import argparse, hashlib, json, mimetypes, pathlib, subprocess, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "sistema_nervoso"))
from sm.raiz import ler_json, gravar_json  # noqa: E402
from sm import fluxo as F  # noqa: E402

CACHE = RAIZ / "painel" / "_cache"
PERMITIDOS = ("criativos", "ponte_capcut", "biblioteca", "planejamento")
SM = [str(RAIZ / ".venv" / "bin" / "python"), "-m", "sm.cli"]


def sm(*args):
    r = subprocess.run([*SM, *args], text=True, capture_output=True, cwd=str(RAIZ / "sistema_nervoso"), env={**__import__("os").environ, "SM_RAIZ": str(RAIZ)})
    return (r.stdout + r.stderr).strip(), r.returncode


def seguro(rel):
    p = (RAIZ / rel).resolve()
    if not any(str(p).startswith(str((RAIZ / r).resolve()) + "/") for r in PERMITIDOS): return None
    if "autorizacoes" in p.parts or p.name == ".env": return None
    return p if p.is_file() else None


def listar(pasta, exts):
    if not pasta.is_dir(): return []
    return sorted(str(p.relative_to(RAIZ)) for p in pasta.rglob("*") if p.is_file() and p.suffix.lower() in exts and not p.name.startswith("_"))


def fluxo():
    g = F.estado_global()
    passos_r = [{"id": p["id"], "descricao": p["descricao"], "executor": p["executor"], **g.get("reestruturacao", {}).get("passos", {}).get(p["id"], {"status": "pendente"})} for p in F.carregar_passos("reestruturacao.yaml")]
    crs = []
    for e in sorted((RAIZ / "criativos").glob("*/estado.json")):
        est = ler_json(e)
        from sm.custo import gasto_de
        crs.append({"id": est["id"] if "id" in est else e.parent.name, "titulo": est.get("titulo", ""), "gasto": gasto_de(e.parent.name), "teto": est.get("teto_usd", 45),
                    "proximo": (F.proximo_passo("passos.yaml", est.get("passos", {})) or {}).get("id"), "passos": est.get("passos", {})})
    matriz = ler_json(RAIZ / "planejamento" / "matriz.json", {"celulas": []})
    return {"criativo_atual": g.get("criativo_atual"), "reestruturacao": passos_r, "criativos": crs, "matriz": matriz}


def criativo(cid):
    d = RAIZ / "criativos" / cid
    est = ler_json(d / "estado.json")
    from sm.custo import gasto_de
    est["gasto_usd"] = gasto_de(cid)
    passos = []
    for p in F.carregar_passos("passos.yaml"):
        st = est.get("passos", {}).get(p["id"], {"status": "pendente"})
        passos.append({"id": p["id"], "descricao": p["descricao"], "executor": p["executor"], "linha": p["linha"], **st})
    dec = ler_json(d / "decupagem.json", {"takes": []}); part = ler_json(d / "partitura.json", {"falas": []})
    cartao = ler_json(RAIZ / "planejamento" / "cartoes" / f"{cid}.json", {})
    takes = []
    for t in dec["takes"]:
        tid = t["id"]
        takes.append({**t, "_quadros": [q for q in listar(d / "quadros", {".png", ".jpg", ".webp"}) if f"/{tid}_" in q and "_folha" not in q],
                      "_teste": [v for v in listar(d / "tomadas" / "teste", {".mp4"}) if f"/{tid}_" in v], "_final": [v for v in listar(d / "tomadas" / "final", {".mp4"}) if f"/{tid}_" in v],
                      "_aprovado": [a for a in listar(d / "aprovados", {".mp4", ".png"}) if f"/{tid}_" in a], "_estado": est.get("takes", {}).get(tid, {})})
    fichas = []
    for f in sorted((d / "esteira").glob("*.json")):
        try: c = ler_json(f); fichas.append({"arquivo": f.name, "veredito": c.get("veredito"), "motivo": c.get("motivo"), "status": c.get("status"), "automatico_ok": c.get("automatico_ok"), "erros": c.get("erros")})
        except Exception as ex: fichas.append({"arquivo": f.name, "erro": str(ex)})
    folhas = listar(d / "inspecao", {".jpg", ".png"})
    seq = d / "aprovados" / "sequencia_copies.mp4"
    seq2 = d / "aprovados" / "sequencia.mp4"
    return {"estado": est, "passos": passos, "takes": takes, "falas": part.get("falas", []), "cartao": cartao, "fichas": fichas, "folhas": folhas,
            "_sequencia": str((seq if seq.exists() else seq2).relative_to(RAIZ)) if (seq.exists() or seq2.exists()) else None}


def buscar_biblioteca(q):
    cat = RAIZ / "biblioteca" / "catalogo.json"
    if not cat.exists(): return []
    q = (q or "").lower().strip(); out = []
    for i in ler_json(cat).get("itens", []):
        blob = json.dumps(i, ensure_ascii=False).lower()
        if not q or all(w in blob for w in q.split()):
            ext = pathlib.Path(i["caminho"]).suffix.lower(); i = dict(i)
            i["_url"] = "/midia/biblioteca/" + i["caminho"]; i["_kind"] = "imagem" if ext in (".png", ".jpg", ".jpeg", ".webp") else "video" if ext in (".mp4", ".mov") else "arquivo"
            out.append(i)
    return out[:200]


def thumb(rel):
    p = seguro(rel)
    if not p: return None
    CACHE.mkdir(exist_ok=True)
    out = CACHE / (hashlib.md5(f"{p}:{p.stat().st_mtime}".encode()).hexdigest() + ".jpg")
    if not out.exists():
        args = ["-sseof", "-0.1", "-i", str(p)] if p.suffix.lower() in (".mp4", ".mov") else ["-i", str(p)]
        subprocess.run(["ffmpeg", "-y", "-v", "error", *args, "-frames:v", "1", "-vf", "scale=240:-2", str(out)])
    return out if out.exists() else None


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _file(self, p, ctype=None):
        ctype = ctype or mimetypes.guess_type(str(p))[0] or "application/octet-stream"; tam = p.stat().st_size
        rng = self.headers.get("Range"); ini, fim = 0, tam - 1
        if rng and rng.startswith("bytes="):
            a, _, b = rng[6:].partition("-"); ini = int(a) if a else max(0, tam - int(b)); fim = min(int(b) if b and a else tam - 1, tam - 1)
            self.send_response(206); self.send_header("Content-Range", f"bytes {ini}-{fim}/{tam}")
        else: self.send_response(200)
        self.send_header("Content-Type", ctype); self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Length", str(fim - ini + 1)); self.send_header("Cache-Control", "no-cache"); self.end_headers()
        with p.open("rb") as f:
            f.seek(ini); resto = fim - ini + 1
            while resto > 0:
                ch = f.read(min(1 << 20, resto))
                if not ch: break
                self.wfile.write(ch); resto -= len(ch)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path); qs = urllib.parse.parse_qs(u.query)
        try:
            if u.path == "/": return self._file(RAIZ / "painel" / "index.html", "text/html; charset=utf-8")
            if u.path == "/api/fluxo": return self._json(fluxo())
            if u.path == "/api/criativo": return self._json(criativo(qs.get("id", [""])[0]))
            if u.path == "/api/biblioteca": return self._json(buscar_biblioteca(qs.get("q", [""])[0]))
            if u.path.startswith("/midia/"):
                p = seguro(urllib.parse.unquote(u.path[7:])); return self._file(p) if p else self._json({"erro": "não permitido"}, 404)
            if u.path.startswith("/thumb/"):
                p = thumb(urllib.parse.unquote(u.path[7:])); return self._file(p, "image/jpeg") if p else self._json({"erro": "sem miniatura"}, 404)
            self._json({"erro": "rota"}, 404)
        except SystemExit as e: self._json({"erro": str(e)}, 400)
        except Exception as e: self._json({"erro": repr(e)}, 500)

    def do_POST(self):
        if self.path != "/api/acao": return self._json({"erro": "rota"}, 404)
        d = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        try:
            acao = d["acao"]; cid = d.get("id")
            if acao == "aprovar":
                args = ["aprovar", d["passo"], d.get("nota") or ""]
                if d.get("reprovar"): args.append("--reprovar")
                if cid and not d["passo"].upper().startswith("R"): args += ["--id", cid]
                out, rc = sm(*args); return self._json({"ok": rc == 0, "saida": out}, 200 if rc == 0 else 400)
            if acao == "ajustes":
                est = F.estado_criativo(cid)
                for k in ("manter", "mudar", "nunca"):
                    if k in d: est.setdefault("ajustes", {})[k] = d[k]
                F.evento(est, "ajustes", est["ajustes"], "painel"); F.gravar_criativo(cid, est); return self._json({"ok": True})
            if acao == "take":
                est = F.estado_criativo(cid); t = est.setdefault("takes", {}).setdefault(d["take"], {})
                for k in ("tomada_aprovada", "trecho_uso", "quadro_ok"):
                    if k in d: t[k] = d[k]
                F.evento(est, f"take_{d['take']}", {k: d[k] for k in ("tomada_aprovada", "trecho_uso", "quadro_ok") if k in d}, "painel"); F.gravar_criativo(cid, est); return self._json({"ok": True})
            if acao == "nota":
                est = F.estado_criativo(cid); F.evento(est, "nota", d.get("texto"), "painel"); F.gravar_criativo(cid, est); return self._json({"ok": True})
            self._json({"erro": "ação desconhecida"}, 400)
        except SystemExit as e: self._json({"erro": str(e)}, 400)
        except Exception as e: self._json({"erro": repr(e)}, 500)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--porta", type=int, default=8765); a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.porta), H)
    print(f"painel em http://127.0.0.1:{a.porta} (só localhost; nunca gera nada)")
    try: srv.serve_forever()
    except KeyboardInterrupt: pass


if __name__ == "__main__":
    main()
