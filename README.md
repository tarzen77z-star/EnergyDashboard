# Energy Intelligence Dashboard — Trader View

A dark-theme energy market dashboard built as a single HTML file. No framework, no build step — just open in a browser. v1 is rebuilt trader-first: a glanceable strip, spreads, storage, fund positioning, and the majors, with every section either showing verified live data or saying so.

![Dashboard](https://img.shields.io/badge/status-live-brightgreen) ![EIA](https://img.shields.io/badge/data-EIA%20API-blue) ![Finnhub](https://img.shields.io/badge/data-Finnhub-orange) ![CFTC](https://img.shields.io/badge/data-CFTC-purple) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What it shows (v1)

- **Trader strip (Tier 1)** — WTI, Brent, reformulated gasoline (LA), heating oil (NY Harbor), Henry Hub, Brent-WTI spread, 3-2-1 crack (spot proxy), crude stocks, nat-gas storage, plus countdowns to the EIA petroleum print (Wed 10:30am ET), EIA nat-gas storage print (Thu 10:30am ET), and Baker Hughes rigs (Fri ~1:00pm ET)
- **Price history** — Weekly and daily spot history charts (WTI, Brent, Henry Hub, retail gasoline). EIA discontinued its futures contract series in April 2024, so no futures curve is shown; full calendar strips need CME monthly settlements (phase 2)
- **Spreads** — Brent-WTI, gasoline crack, heating-oil crack, 3-2-1 crack. Crack spreads here are a **spot-based proxy** (EIA spot prices, not NYMEX futures settlements)
- **Storage & positioning** — Crude, gasoline, and distillate stocks, nat-gas storage, crude and nat-gas production, LNG and pipeline exports, and CFTC Commitments of Traders large-speculator net positions (WTI, nat-gas, RBOB, ULSD)
- **Equities** — Live quotes plus fundamentals for 11 majors (XOM, CVX, COP, SLB, OXY, EOG, DVN, HAL, BKR, MPC, PSX) with analyst recommendations
- **News** — Latest company headlines for XOM, CVX, COP (Finnhub)
- **Research & reports** — Links to free EIA outlooks and reports plus CFTC COT

No section fails silently: any feed that does not return data shows a short "Data unavailable" note in its panel.

---

## Data Sources

| Source | Data | Cost |
|---|---|---|
| [EIA Open Data](https://www.eia.gov/opendata/) | Commodity prices, production, storage, trade | Free |
| [Finnhub](https://finnhub.io/) | Stock quotes, fundamentals, recommendations, company news | Free tier |
| [CFTC COT (Socrata)](https://publicreporting.cftc.gov/resource/6dca-aqww.json) | Large-speculator positions, weekly | Free, no key |

---

## Setup

### 1. Get API Keys

**EIA (required)**
- Go to [eia.gov/opendata](https://www.eia.gov/opendata/register.php)
- Enter your name and email — key arrives instantly, no credit card needed

**Finnhub (required for stock data)**
- Go to [finnhub.io](https://finnhub.io/)
- Sign up for a free account — key is shown immediately in your dashboard

### 2. Add Your Keys

Open `index.html` in any text editor and find these two lines near the top of the `<script>` section:

```javascript
const EIA_KEY = 'YOUR_EIA_KEY';     // Register free at eia.gov/opendata
const FH_KEY  = 'YOUR_FINNHUB_KEY'; // Register free at finnhub.io
```

Replace the placeholder values with your actual keys and save. (The published copy already has working keys configured.)

### 3. Verify Your Keys Are Working

Open `index.html` in your browser. You should see:

- **EIA key working** — the trader strip loads WTI, Brent, and natural gas prices within a few seconds. The `EIA ●` pill in the top-right header turns green.
- **Finnhub key working** — the majors section loads quotes and fundamentals. The `FINNHUB ●` pill turns green.
- **CFTC** — needs no key. The `CFTC ●` pill turns green when the positioning cards load.

If prices show `--` or "Data unavailable", double-check that your key was pasted correctly with no extra spaces and is inside the single quotes.

### 4. Open in Browser

No server needed and no local API needed. The v1 page fetches nat-gas data directly from EIA — the old `localhost:5000` local API (`energy_api.py`, `natural_gas_energy.db`) is no longer required by the page and is retained in the repo for local use only.

---

## EIA Series Used (v1)

| Metric | EIA Series / Route |
|---|---|
| WTI Crude Oil | `PET.RWTC.W` (weekly spot) |
| Brent Crude Oil | `PET.RBRTE.D` (daily spot), `PET.RBRTE.W` (weekly, chart) |
| Henry Hub Natural Gas | `NG.RNGWHHD.D` (daily spot) |
| RBOB Gasoline (LA reformulated) | `petroleum/pri/spt` v2, product EPMRR, area Y05LA, daily |
| No.2 Heating Oil (NY Harbor) | `petroleum/pri/spt` v2, product EPD2F, area Y35NY, daily |
| Propane (Mont Belvieu) | `petroleum/pri/spt` v2, product EPLLPA, area Y44MB, daily |
| Retail Gasoline (U.S. avg) | `PET.EMM_EPMR_PTE_NUS_DPG.W` |
| U.S. Crude Production | `PET.WCRFPUS2.W` |
| U.S. Commercial Crude Stocks | `PET.WCESTUS1.W` |
| U.S. Gasoline Stocks | `PET.WGTSTUS1.W` |
| U.S. Distillate Stocks | `PET.WDISTUS1.W` |
| Nat-Gas Storage (Lower 48) | `NG.NW2_EPG0_SWO_R48_BCF.W` |
| Dry Nat-Gas Production | `NG.N9070US2.M` |
| LNG Exports (monthly / annual) | `NG.N9133US2.M` / `NG.N9133US2.A` |
| Pipeline Exports | `NG.N9102US2.M` |

Note: EIA discontinued its futures contract series in April 2024 (`RCLC`/`RNGC` return stale 2024 data and `RCLC6`/`RCLC12`/`RNGC6` 404), so no futures curve ships in v1 — see Phase 2. No verified total nat-gas imports series was found (candidate `N9103US2` returned an implausible scale), so imports are omitted in v1.

## CFTC Series Used (v1)

Legacy futures-only Commitments of Traders, dataset `6dca-aqww` (Socrata, no key). Markets: WTI-PHYSICAL (`067651`), NAT GAS NYME (`023651`), GASOLINE RBOB (`111659`), NY HARBOR ULSD (`022651`). Shown: large speculators (non-commercial) net, week change in net, share of open interest.

## Energy Stocks Tracked (v1)

`XOM` · `CVX` · `COP` · `SLB` · `OXY` · `EOG` · `DVN` · `HAL` · `BKR` · `MPC` · `PSX`

---

## Limitations

- **EIA data is not real-time** — most series update weekly or monthly depending on the publication schedule
- **Crack spreads are spot-based proxies** — not NYMEX futures cracks
- **Finnhub free tier** — 60 API calls/minute; no uptime SLA; US stocks only on free plan
- **No backend / no caching** — each page load fetches fresh from the APIs directly; all data lives in memory
- **CORS** — EIA, Finnhub, and CFTC Socrata all support browser-side requests; no proxy needed

---

## Roadmap (phase 2)

- [ ] Scheduled pre-built JSON for strips (CME monthly settlements), COT history, and news history — faster loads, fewer live calls
- [ ] Full calendar strips (Cal-27 etc.) from CME monthly settlements
- [ ] Earnings calendar and insider transactions via Finnhub (Earnings / Insider sections)
- [ ] Coal and electricity sections, wired to verified EIA routes (currently cut — they rendered blank)
- [ ] Market-intelligence summaries (needs a server-side AI proxy; browsers cannot call the Anthropic API directly)

---

## License

MIT — free to use, modify, and distribute.

---

## Acknowledgements

- [U.S. Energy Information Administration](https://www.eia.gov/) — public domain energy data
- [Finnhub](https://finnhub.io/) — market data API
- [CFTC](https://www.cftc.gov/) — public Commitments of Traders data
- [Chart.js](https://www.chartjs.org/) — charting library
- [IBM Plex fonts](https://www.ibm.com/plex/) — typography
