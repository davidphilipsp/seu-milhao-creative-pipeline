"""Localiza a raiz da produção (a pasta que tem memoria/fatos.json) e utilitários de arquivo."""
import datetime, json, os, pathlib

_RAIZ = None


def raiz() -> pathlib.Path:
    global _RAIZ
    if _RAIZ:
        return _RAIZ
    cands = [pathlib.Path(os.environ["SM_RAIZ"])] if os.environ.get("SM_RAIZ") else []
    cands += [pathlib.Path.cwd(), *pathlib.Path.cwd().parents, pathlib.Path(__file__).resolve().parents[2]]
    for c in cands:
        if (c / "memoria" / "fatos.json").exists():
            _RAIZ = c
            return c
    raise SystemExit("raiz não encontrada: rode dentro de seu-milhao-video/ (precisa de memoria/fatos.json) ou defina SM_RAIZ")


def agora() -> str:
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def hoje() -> str:
    return datetime.date.today().isoformat()


def ler_json(p: pathlib.Path, padrao=None):
    if not p.exists():
        if padrao is not None:
            return padrao
        raise SystemExit(f"não existe: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def gravar_json(p: pathlib.Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def criativo_dir(cid: str) -> pathlib.Path:
    return raiz() / "criativos" / cid


def rel(p: pathlib.Path) -> str:
    try:
        return str(pathlib.Path(p).resolve().relative_to(raiz()))
    except ValueError:
        return str(p)
