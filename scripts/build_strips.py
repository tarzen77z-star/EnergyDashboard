#!/usr/bin/env python3
"""Build data/strips.json for the EnergyDashboard from CME monthly settlements.

Input:  a JSON file {"trade_date": "YYYY-MM-DD", "commodities": {
            "WTI": {"2026-12": 102.00, ...}, "RBOB": {...},
            "ULSD": {...}, "NG": {...}}}
        Month keys are "YYYY-MM"; values are settle prices exactly as read
        from CME's public settlement pages (no sign-in). Nothing is
        interpolated, backfilled, or invented: months the page does not show
        are simply absent, incomplete calendar years are omitted, and a
        spread is omitted when either of its months is missing.
Output: data/strips.json (or --out path) with trade_date, generated_at,
        per-commodity monthly maps, calendar strips (mean of the 12 monthly
        settles, full years only), and time spreads, all computed from the
        settles alone. Brent is deliberately excluded: ICE publishes no
        public monthly settlement table (last prices only; its Report
        Center end-of-day reports are paid), so Brent stays on the
        dashboard's existing spot proxy.

Usage: python3 build_strips.py tables.json [--out data/strips.json]
Stdlib only. Exits non-zero on any malformed input; writes nothing then.
"""

import json
import re
import sys
from datetime import datetime, timezone

MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# label, unit, display decimals (CME quoting conventions)
COMMODITIES = {
    "WTI": {"label": "WTI crude", "unit": "$/bbl", "decimals": 2},
    "RBOB": {"label": "RBOB gasoline", "unit": "$/gal", "decimals": 4},
    "ULSD": {"label": "NY Harbor ULSD heating oil", "unit": "$/gal", "decimals": 4},
    "NG": {"label": "Henry Hub natural gas", "unit": "$/MMBtu", "decimals": 3},
}


def add_months(ym, n):
    y, m = int(ym[:4]), int(ym[5:7])
    idx = (y * 12 + (m - 1)) + n
    return "%04d-%02d" % (idx // 12, idx % 12 + 1)


def short(ym):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return "%s-%s" % (months[int(ym[5:7]) - 1], ym[2:4])


def build(tables):
    trade_date = tables.get("trade_date")
    if not trade_date or not DATE_RE.match(trade_date):
        raise ValueError("trade_date must be YYYY-MM-DD")
    raw = tables.get("commodities")
    if not isinstance(raw, dict) or not raw:
        raise ValueError("commodities must be a non-empty object")
    out_commodities = {}
    for code, cfg in COMMODITIES.items():
        months = raw.get(code)
        if months is None:
            continue  # absent commodity: omitted, never fabricated
        if not isinstance(months, dict) or not months:
            raise ValueError("%s: monthly map must be a non-empty object" % code)
        settles = {}
        for ym, price in months.items():
            if not MONTH_RE.match(ym):
                raise ValueError("%s: bad month key %r" % (code, ym))
            if not isinstance(price, (int, float)) or price != price:
                raise ValueError("%s: bad settle for %s" % (code, ym))
            settles[ym] = float(price)
        ordered = sorted(settles)
        # Calendar strips: mean of the 12 monthly settles, full years only.
        by_year = {}
        for ym in ordered:
            by_year.setdefault(ym[:4], []).append(ym)
        strips = []
        for year in sorted(by_year):
            ms = by_year[year]
            if len(ms) != 12 or sorted(ms) != ["%s-%02d" % (year, m)
                                                for m in range(1, 13)]:
                continue  # incomplete year: omitted, never interpolated
            mean = sum(settles[m] for m in ms) / 12.0
            strips.append({"year": int(year), "value": round(mean, 6),
                           "months": 12})
        # Time spreads, from settles only; omitted when a month is missing.
        spreads = []
        front = ordered[0]
        out12 = add_months(front, 12)
        if out12 in settles:
            spreads.append({
                "label": "12M out minus front (%s minus %s)"
                         % (short(out12), short(front)),
                "months": [front, out12],
                "value": round(settles[out12] - settles[front], 6)})
        dec_front = "%s-12" % front[:4]
        dec_next = "%d-12" % (int(front[:4]) + 1)
        if dec_front in settles and dec_next in settles:
            spreads.append({
                "label": "Dec-to-Dec (%s minus %s)"
                         % (short(dec_next), short(dec_front)),
                "months": [dec_front, dec_next],
                "value": round(settles[dec_next] - settles[dec_front], 6)})
        out_commodities[code] = {
            "label": cfg["label"], "unit": cfg["unit"],
            "decimals": cfg["decimals"], "front_month": front,
            "settlements": {ym: settles[ym] for ym in ordered},
            "strips": strips, "spreads": spreads}
    if not out_commodities:
        raise ValueError("no recognized commodities in input")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "trade_date": trade_date,
        "source": "CME Group public settlement pages (no sign-in)",
        "brent_note": ("Brent monthly settlements are not publicly "
                       "available (ICE shows last prices only; its Report "
                       "Center end-of-day reports are paid) — Brent stays "
                       "on the existing spot proxy."),
        "commodities": out_commodities}


def main(argv):
    if len(argv) < 2 or len(argv) > 4 or "--help" in argv:
        print("usage: build_strips.py tables.json [--out data/strips.json]",
              file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        tables = json.load(f)
    out = build(tables)
    out_path = "data/strips.json"
    if "--out" in argv:
        out_path = argv[argv.index("--out") + 1]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("trade_date %s" % out["trade_date"])
    for code, m in out["commodities"].items():
        ss = ", ".join("Cal-%d %.4f" % (s["year"], s["value"])
                       for s in m["strips"]) or "no full year"
        sp = ", ".join("%s %.4f" % (s["label"], s["value"])
                       for s in m["spreads"]) or "no spreads"
        print("%s: front %s, months %d, strips: %s; spreads: %s"
              % (code, m["front_month"], len(m["settlements"]), ss, sp))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
