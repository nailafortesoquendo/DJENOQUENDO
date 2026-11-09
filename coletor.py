#!/usr/bin/env python3
"""Coletor diário do DJEN para os advogados do escritório.

Consulta a API pública do Diário de Justiça Eletrônico Nacional
(comunicaapi.pje.jus.br) para cada OAB configurada, em todos os tribunais,
e grava o resultado acumulado em site/data/comunicacoes.json, que a
página em site lê.

Uso:
    python coletor.py                 # últimos 3 dias
    python coletor.py 2026-11-01 2026-11-07
    python coletor.py --dias 30       # últimos 30 dias

Sem dependências além da biblioteca padrão.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

API = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
ITENS_POR_PAGINA = 100
PAUSA_ENTRE_CHAMADAS = 1.0      # segundos; a API é pública e limita por IP
RETENCAO_DIAS = 120             # histórico mantido no JSON

ADVOGADOS = [
    {"key": "mauro",   "nome": "Mauro Oquendo do Rêgo Monteiro", "oab": "5935",  "uf": "PI"},
    {"key": "gabriel", "nome": "Gabriel Ataíde da Silva",         "oab": "22891", "uf": "PI"},
    {"key": "naila",   "nome": "Naila Fortes e Silva",            "oab": "5815",  "uf": "PI"},
]

RAIZ = Path(__file__).resolve().parent
ARQ_DADOS = RAIZ / "site" / "data" / "comunicacoes.json"
ARQ_META = RAIZ / "site" / "data" / "meta.json"


def _pick(obj: dict, *chaves):
    """Primeiro valor não vazio entre grafias alternativas de um campo."""
    for k in chaves:
        v = obj.get(k) if isinstance(obj, dict) else None
        if v not in (None, ""):
            return v
    return ""


def normalizar(bruto: dict) -> dict:
    advs = []
    for d in _pick(bruto, "destinatarioadvogados", "destinatarioAdvogados", "advogados") or []:
        a = d.get("advogado", d) if isinstance(d, dict) else {}
        advs.append({
            "nome": _pick(a, "nome", "nomeAdvogado"),
            "oab": str(_pick(a, "numero_oab", "numeroOab", "oab")),
            "uf": _pick(a, "uf_oab", "ufOab", "uf"),
        })
    data = str(_pick(bruto, "data_disponibilizacao", "datadisponibilizacao", "dataDisponibilizacao"))[:10]
    texto = str(_pick(bruto, "texto", "conteudo"))
    ident = _pick(bruto, "id", "hash") or f"{data}|{_pick(bruto, 'numero_processo')}|{texto[:60]}"
    return {
        "id": str(ident),
        "data": data,
        "tribunal": _pick(bruto, "siglaTribunal", "sigla_tribunal", "tribunal"),
        "tipo": _pick(bruto, "tipoComunicacao", "tipo_comunicacao", "tipoDocumento"),
        "orgao": _pick(bruto, "nomeOrgao", "nome_orgao", "orgao"),
        "processo": _pick(bruto, "numeroprocessocommascara", "numero_processo_mascara", "numero_processo", "numeroProcesso"),
        "classe": _pick(bruto, "nomeClasse", "nome_classe"),
        "meio": _pick(bruto, "meiocompleto", "meio"),
        "texto": texto,
        "link": _pick(bruto, "link"),
        "advs": advs,
        "partes": [f"{_pick(d, 'nome')}{' (' + d['polo'] + ')' if d.get('polo') else ''}"
                   for d in (_pick(bruto, "destinatarios") or []) if isinstance(d, dict)],
        "match": [],
    }


def _get(url: str, tentativas: int = 4) -> dict:
    req = urllib.request.Request(url, headers={
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "User-Agent": "RadarDJEN/1.0 (monitor de publicacoes do escritorio; GitHub Actions)",
    })
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tentativas - 1:
                time.sleep(2 ** (i + 1))
                continue
            detalhe = ""
            try:
                corpo = e.read(2000).decode("utf-8", "replace")
                m = re.search(r"<title>(.*?)</title>", corpo, re.I | re.S)
                detalhe = " ".join((m.group(1) if m else corpo[:120]).split())
            except Exception:  # noqa: BLE001
                pass
            raise RuntimeError(f"HTTP {e.code} {e.reason}: {detalhe}".rstrip(": ")) from None
        except urllib.error.URLError:
            if i < tentativas - 1:
                time.sleep(2 ** (i + 1))
                continue
            raise
    raise RuntimeError("sem resposta")


def buscar(adv: dict, inicio: str, fim: str) -> list[dict]:
    itens, pagina = [], 1
    while True:
        q = urllib.parse.urlencode({
            "numeroOab": adv["oab"], "ufOab": adv["uf"],
            "dataDisponibilizacaoInicio": inicio, "dataDisponibilizacaoFim": fim,
            "pagina": pagina, "itensPorPagina": ITENS_POR_PAGINA,
        })
        resp = _get(f"{API}?{q}")
        lote = resp.get("items") or resp.get("content") or resp.get("data") or ([] if isinstance(resp, dict) else resp)
        itens.extend(lote)
        total = int(resp.get("count") or resp.get("total") or resp.get("totalElements") or len(itens)) if isinstance(resp, dict) else len(itens)
        if len(lote) < ITENS_POR_PAGINA or len(itens) >= total:
            return itens
        pagina += 1
        time.sleep(PAUSA_ENTRE_CHAMADAS)


def carregar_existentes() -> dict[str, dict]:
    if not ARQ_DADOS.exists():
        return {}
    try:
        return {c["id"]: c for c in json.loads(ARQ_DADOS.read_text(encoding="utf-8")).get("comunicacoes", [])}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def main(argv: list[str]) -> int:
    hoje = date.today()
    if "--dias" in argv:
        n = int(argv[argv.index("--dias") + 1])
        inicio, fim = (hoje - timedelta(days=n)).isoformat(), hoje.isoformat()
    elif len(argv) >= 3 and argv[1][:1] != "-":
        inicio, fim = argv[1], argv[2]
    else:
        # Padrão: últimos 3 dias. Cobre fim de semana e um dia em que o computador ficou desligado.
        inicio, fim = (hoje - timedelta(days=3)).isoformat(), hoje.isoformat()

    acumulado = carregar_existentes()
    novos, erros = 0, []
    for adv in ADVOGADOS:
        try:
            brutos = buscar(adv, inicio, fim)
        except Exception as e:  # noqa: BLE001 - registra e segue para o próximo advogado
            erros.append(f"{adv['nome']}: {e}")
            continue
        for b in brutos:
            c = normalizar(b)
            alvo = acumulado.setdefault(c["id"], c)
            if adv["key"] not in alvo["match"]:
                alvo["match"].append(adv["key"])
            if alvo is c:
                novos += 1
        print(f"{adv['nome']}: {len(brutos)} comunicação(ões) entre {inicio} e {fim}")
        time.sleep(PAUSA_ENTRE_CHAMADAS)

    limite = (hoje - timedelta(days=RETENCAO_DIAS)).isoformat()
    lista = sorted((c for c in acumulado.values() if c["data"] >= limite), key=lambda c: c["data"], reverse=True)

    ARQ_DADOS.parent.mkdir(parents=True, exist_ok=True)
    ARQ_DADOS.write_text(json.dumps({"advogados": ADVOGADOS, "comunicacoes": lista}, ensure_ascii=False, indent=1), encoding="utf-8")
    ARQ_META.write_text(json.dumps({
        "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "periodo_consultado": [inicio, fim],
        "total": len(lista), "novos": novos, "erros": erros,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Total acumulado: {len(lista)} | novos nesta execução: {novos}")
    for e in erros:
        print("ERRO:", e, file=sys.stderr)
    return 1 if erros and not novos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
