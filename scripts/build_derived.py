#!/usr/bin/env python3
"""Build data/derived.json for the EnergyDashboard GitHub page.

Scheduled snapshot for data the live page cannot reliably fetch in the
browser. Public NO-KEY sources only:

  - CFTC Commitments of Traders (Socrata dataset 6dca-aqww, publicreporting
    host): latest + weekly history for WTI crude, natural gas, RBOB gasoline
    and ULSD heating oil, large speculators (non-commercial) net.
  - News history: public Google News RSS searches (energy queries). No key.

Deliberately NOT in this file: EIA series. EIA needs an API key, and this
builder must never touch page keys. EIA-backed items (including total U.S.
natural gas imports, series NG.N9100US2.M, verified against EIA's data
browser: "U.S. Natural Gas Imports (Million Cubic Feet)", ~220,000-340,000
MMCF/month) are fetched live by the page itself with its own key plumbing.

Output: <repo-root>/data/derived.json (atomic write via temp + rename).
Exit 0 when COT data is sane (news may be degraded, flagged in the file).
Exit 1 and writes NOTHING when COT data fails sanity checks, so a bad run
never overwrites the last good snapshot.

Usage:
    python3 scripts/build_derived.py [--out PATH]
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone

COTMAP = {
    "067651": ("WTI crude", "NYMEX WTI"),
    "023651": ("Natural gas", "NYMEX Henry Hub"),
    "111659": ("RBOB gasoline", "NYMEX RBOB"),
    "022651": ("ULSD heating oil", "NYMEX ULSD"),
}
COT_URL = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"
COT_SELECT = (
    "report_date_as_yyyy_mm_dd,cftc_contract_market_code,"
    "market_and_exchange_names,noncomm_positions_long_all,"
    "noncomm_positions_short_all,change_in_noncomm_long_all,"
    "change_in_noncomm_short_all,open_interest_all,"
    "pct_of_oi_noncomm_long_all,pct_of_oi_noncomm_short_all"
)
RSS_QUERIES = ["oil prices OR OPEC", "natural gas prices", "energy markets"]
RSS_URL = (
    "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
)
UA = "Mozilla/5.0 (compatible; EnergyDashboard-derived/1.0)"


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_cot():
    params = {
        "$select": COT_SELECT,
        "$where": "cftc_contract_market_code in('067651','023651','111659','022651')",
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "$limit": "200",
    }
    raw = _get(COT_URL + "?" + urllib.parse.urlencode(params))
    rows = json.loads(raw.decode("utf-8"))
    by = defaultdict(list)
    for row in rows:
        by[row["cftc_contract_market_code"]].append(row)
    markets = {}
    for code, (name, exchange) in COTMAP.items():
        arr = sorted(
            by.get(code, []),
            key=lambda r: str(r.get("report_date_as_yyyy_mm_dd", "")),
            reverse=True,
        )
        if not arr:
            raise ValueError("COT: no rows for market code %s" % code)
        cur = arr[0]
        long_n = float(cur["noncomm_positions_long_all"])
        short_n = float(cur["noncomm_positions_short_all"])
        net = int(long_n - short_n)
        oi = float(cur["open_interest_all"])
        week_change = None
        if len(arr) > 1:
            prev = arr[1]
            prev_net = int(
                float(prev["noncomm_positions_long_all"])
                - float(prev["noncomm_positions_short_all"])
            )
            week_change = net - prev_net
        history = []
        for r in arr:
            try:
                history.append(
                    {
                        "date": str(r["report_date_as_yyyy_mm_dd"])[:10],
                        "net": int(
                            float(r["noncomm_positions_long_all"])
                            - float(r["noncomm_positions_short_all"])
                        ),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue
        markets[name] = {
            "code": code,
            "exchange": exchange,
            "report_date": str(cur["report_date_as_yyyy_mm_dd"])[:10],
            "net": net,
            "long": int(long_n),
            "short": int(short_n),
            "week_change": week_change,
            "open_interest": int(oi),
            "pct_long": _fnum(cur.get("pct_of_oi_noncomm_long_all")),
            "pct_short": _fnum(cur.get("pct_of_oi_noncomm_short_all")),
            "history": history,
        }
    return markets


def _fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def fetch_news():
    items = []
    errors = []
    for q in RSS_QUERIES:
        url = RSS_URL.format(q=urllib.parse.quote(q))
        try:
            data = _get(url, timeout=30)
            root = ET.fromstring(data)
        except Exception as exc:  # noqa: BLE001 - per-feed failure is non-fatal
            errors.append("%s: %s" % (q, exc))
            continue
        for it in root.findall(".//item"):
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            pub = (it.findtext("pubDate") or "").strip()
            if not title or not link:
                continue
            source = ""
            if " - " in title:
                title, source = title.rsplit(" - ", 1)
                title, source = title.strip(), source.strip()
            published = pub
            try:
                from email.utils import parsedate_to_datetime

                published = parsedate_to_datetime(pub).isoformat()
            except (TypeError, ValueError):
                pass
            items.append(
                {
                    "title": title,
                    "url": link,
                    "source": source,
                    "published": published,
                    "query": q,
                }
            )
    seen = set()
    deduped = []
    for a in items:
        key = ("u:" + a["url"]) if a["url"] else ("t:" + _norm_title(a["title"]))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(a)
    deduped.sort(key=lambda a: a["published"], reverse=True)
    return deduped[:30], ("; ".join(errors) if errors else None)


def main(argv):
    out = None
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    if out is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = os.path.join(root, "data", "derived.json")

    try:
        markets = fetch_cot()
    except Exception as exc:  # noqa: BLE001 - COT failure must not overwrite
        print("COT fetch failed, not writing: %s" % exc, file=sys.stderr)
        return 1

    # Sanity checks: all markets, one shared latest date, fresh, nets sane.
    dates = {m["report_date"] for m in markets.values()}
    if len(dates) != 1:
        print("COT sanity failed: mismatched report dates %s" % dates, file=sys.stderr)
        return 1
    report_date = dates.pop()
    try:
        age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(report_date).replace(tzinfo=timezone.utc)).days
    except ValueError:
        print("COT sanity failed: bad report date %r" % report_date, file=sys.stderr)
        return 1
    if age_days > 21:
        print("COT sanity failed: latest report %s is %d days old" % (report_date, age_days), file=sys.stderr)
        return 1
    for name, m in markets.items():
        if not (m["open_interest"] > 0 and abs(m["net"]) <= m["open_interest"]):
            print("COT sanity failed: bad net/OI for %s" % name, file=sys.stderr)
            return 1

    news, news_error = fetch_news()
    if news_error:
        print("News warning: %s" % news_error, file=sys.stderr)

    doc = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "cot": {
            "source": "CFTC Socrata dataset 6dca-aqww (publicreporting.cftc.gov)",
            "report_date": report_date,
            "markets": markets,
        },
        "news": news,
        "news_error": news_error,
        "notes": {
            "nat_gas_imports": (
                "Total U.S. natural gas imports (EIA series NG.N9100US2.M, "
                "MMCF) are fetched live by the page with its own EIA key "
                "plumbing; they are not in this file because this builder "
                "uses only no-key sources."
            )
        },
    }
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out)
    print(
        "Wrote %s: COT report %s nets {%s}, news items %d%s"
        % (
            out,
            report_date,
            ", ".join("%s %+d" % (n, m["net"]) for n, m in markets.items()),
            len(news),
            (" (news degraded: %s)" % news_error if news_error else ""),
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
