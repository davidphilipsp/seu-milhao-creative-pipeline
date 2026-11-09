"""CLI da Sala de Roteiro (./sala). Separada do sm: não importa nem chama o sm."""
import argparse
import re
import shutil
import sys

from .base import CONTRATO_VERSAO, hoje, ler_json, norm, sala_raiz


def cmd_sincronizar(a):
    from .sincronizar import sincronizar
    print(sincronizar(a.corpus))


def _proximo_pedido(sala) -> str:
    ns = [int(m.group(1)) for p in (sala / "pedidos").glob("P-*.md") if (m := re.match(r"P-(\d+)", p.stem))]
    return f"P-{(max(ns) + 1 if ns else 1):03d}"


def interpretar(texto: str) -> dict:
    t = norm(texto)
    seg = next((v for k, v in (("alto ticket", "alto_ticket"), ("classe media", "classe_media"), ("popular", "popular")) if k in t), "popular")
    ang = next((v for k, v in (("solidari", "solidario"), ("aspirac", "aspiracional"), ("convite", "convite_direto")) if k in t), "a definir")
    dest = "grupo" if "grupo" in t or "comunidade" in t else ("compra" if "compra" in t or "link" in t else "a definir")
    dur = re.search(r"(\d+)\s*s\b", t)
    qtd = re.search(r"(\d+)\s*cascas?", t)
    pers = sorted(set(re.findall(r"\bp[1-5]\b", t)))
    return {"segmento": seg, "angulo": ang, "destino": dest, "duracao_s": int(dur.group(1)) if dur else 30,
            "quantidade": int(qtd.group(1)) if qtd else 1, "personas": [p.upper() for p in pers]}


def cmd_pedido(a):
    sala = sala_raiz()
    (sala / "pedidos").mkdir(exist_ok=True)
    pid = _proximo_pedido(sala)
    d = interpretar(a.texto)
    man = sala / "insumos" / "MANIFESTO.json"
    h = ler_json(man)["hash"] if man.exists() else "sem-sincronizar"
    corpo = [f"# Pedido {pid}", "", f"- id: {pid}", f"- data: {hoje()}", f"- texto: \"{a.texto}\"",
             f"- segmento: {d['segmento']}", f"- angulo: {d['angulo']}", f"- destino: {d['destino']}",
             f"- duracao_s: {d['duracao_s']}", f"- quantidade: {d['quantidade']}",
             f"- personas: {', '.join(d['personas']) or 'livre (o idealizador escolhe e justifica)'}",
             f"- insumos_hash: {h}", "- status: aberto", "",
             "## Regras do pedido",
             "- várias cascas → famílias de gancho diferentes;",
             "- fatos só dos snapshots; segunda pessoa só para convite;",
             "- cada casca cabe em insumos/limites_producao.md.", ""]
    (sala / "pedidos" / f"{pid}.md").write_text("\n".join(corpo), encoding="utf-8")
    print(f"pedidos/{pid}.md · {d['segmento']} · {d['angulo']} · {d['destino']} · {d['duracao_s']} s · {d['quantidade']} casca(s)")


def cmd_validar(a):
    from .validar_casca import relatorio, validar
    sala = sala_raiz()
    ids = a.ids or [p.stem for p in sorted((sala / "cascas" / "rascunho").glob("*.md"))]
    pior = 0
    for cid in ids:
        r = validar(cid, sala)
        print(relatorio(r))
        pior = max(pior, 0 if r["status"] == "OK" else 1)
    sys.exit(pior)


def cmd_aprovar(a):
    from .validar_casca import validar
    sala = sala_raiz()
    src = sala / "cascas" / "rascunho" / f"{a.id}.md"
    if not src.exists():
        sys.exit(f"{a.id} não está em cascas/rascunho/")
    r = validar(a.id, sala)
    if r["status"] != "OK":
        sys.exit(f"{a.id}: {r['status']} — não aprovo casca que não passa em ./sala validar")
    dst = sala / "cascas" / "aprovadas" / src.name
    shutil.move(src, dst)
    v = src.with_suffix(".validacao.json")
    if v.exists():
        shutil.move(v, dst.with_suffix(".validacao.json"))
    print(f"{a.id} aprovada → cascas/aprovadas/ · próximo: ./sala para-roteiro {a.id}")


def cmd_para_roteiro(a):
    from .para_roteiro import converter
    print(converter(a.id))


def cmd_estado(a):
    from .validar_casca import validar
    sala = sala_raiz()
    peds = sorted((sala / "pedidos").glob("P-*.md"))
    abertos = [p.stem for p in peds if "status: aberto" in p.read_text(encoding="utf-8")]
    cont, desat = {}, []
    for pasta in ("rascunho", "aprovadas"):
        for p in sorted((sala / "cascas" / pasta).glob("*.md")):
            r = validar(p.stem, sala, gravar=False)
            chave = f"{pasta}:{r['status']}"
            cont[chave] = cont.get(chave, 0) + 1
            if r["status"] == "DESATUALIZADA":
                desat.append(p.stem)
    saidas = sorted(p.name for p in (sala / "saida").glob("*_ROTEIRO.md"))
    man = sala / "insumos" / "MANIFESTO.json"
    h = ler_json(man) if man.exists() else {"hash": "—", "data": "nunca"}
    print(f"SALA DE ROTEIRO · contrato {CONTRATO_VERSAO} · insumos {h['hash']} ({h['data'][:16]})")
    print(f"pedidos: {len(peds)} ({len(abertos)} aberto(s): {', '.join(abertos) or '—'})")
    print("cascas: " + (" · ".join(f"{k} {v}" for k, v in sorted(cont.items())) or "nenhuma"))
    print(f"saídas prontas: {len(saidas)}" + (f" ({', '.join(saidas)})" if saidas else ""))
    print(f"desatualizadas: {', '.join(desat) or 'nenhuma'}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="./sala", description="Sala de Roteiro: idealização de cascas. Sem geração, sem custo.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sincronizar", help="copia os insumos de leitura da produção, com hash e data")
    s.add_argument("--corpus", help="pasta do corpus (padrão: <produção>/fontes/corpus)")
    s.set_defaults(f=cmd_sincronizar)
    s = sub.add_parser("pedido", help='cria pedidos/P-NNN.md a partir de "<texto>"'); s.add_argument("texto"); s.set_defaults(f=cmd_pedido)
    s = sub.add_parser("validar", help="valida uma ou mais cascas (todas do rascunho se vazio)"); s.add_argument("ids", nargs="*"); s.set_defaults(f=cmd_validar)
    s = sub.add_parser("aprovar", help="move a casca para aprovadas/ (SÓ por comando do usuário)"); s.add_argument("id"); s.set_defaults(f=cmd_aprovar)
    s = sub.add_parser("para-roteiro", help="casca aprovada → saida/<id>_ROTEIRO.md"); s.add_argument("id"); s.set_defaults(f=cmd_para_roteiro)
    s = sub.add_parser("estado", help="pedidos, cascas por status, saídas, desatualizadas (≤5 linhas)"); s.set_defaults(f=cmd_estado)
    s = sub.add_parser("verificar-isolamento", help="falha se o branch alterou algo fora das áreas permitidas"); s.add_argument("base", nargs="?", default="main")
    s.set_defaults(f=lambda a: sys.exit(__import__("sala_de_roteiro.ferramentas.verificar_isolamento", fromlist=["main"]).main([a.base])))
    a = ap.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
