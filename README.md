# Energy Intelligence Dashboard

A Bloomberg-style dark-theme energy market dashboard built as a single HTML file. No framework, no build step, no dependencies to install — just open in a browser.

![Dashboard](https://img.shields.io/badge/status-live-brightgreen) ![EIA](https://img.shields.io/badge/data-EIA%20API-blue) ![Finnhub](https://img.shields.io/badge/data-Finnhub-orange) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

- **Commodity Prices** — WTI Crude, Brent, Henry Hub Natural Gas, Propane, RBOB Gasoline, Heating Oil with period-over-period % change
- **Energy Production** — U.S. crude oil, natural gas, coal, and electricity production with 52-week historical charts
- **Energy Stocks** — Live quotes for 10 major energy companies (ExxonMobil, Chevron, ConocoPhillips, SLB, EOG, Phillips 66, Marathon, NextEra, Occidental, Devon) with fundamentals drill-down
- **Research Reports** — Direct links to 9 EIA publications including STEO, AEO, Weekly Petroleum Status Report, and more
- **Live ticker bar** — Real-time scrolling prices across all tabs
- **Click-through modals** — Drill into any price card or stock for detailed data
- **Mobile responsive** — Works on phones and tablets
- **Live ET clock** — Sticky header with API status indicators

---

## Data Sources

| Source | Data | Cost |
|---|---|---|
| [EIA Open Data](https://www.eia.gov/opendata/) | Commodity prices, production, storage, generation | Free |
| [Finnhub](https://finnhub.io/) | Stock quotes, company fundamentals, earnings | Free tier |

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

Open `energy-dashboard.html` in any text editor and find these two lines near the top of the `<script>` section:

```javascript
const EIA_KEY = 'your_eia_key_here';
const FH_KEY  = 'your_finnhub_key_here';
```

Replace the placeholder values with your actual keys and save.

### 3. Open in Browser

No server needed. Just open the file:

```bash
# Mac
open energy-dashboard.html

# Windows
start energy-dashboard.html

# Linux
xdg-open energy-dashboard.html
```

Or drag and drop the file into any browser window.

---

## Project Structure

```
energy-dashboard/
└── energy-dashboard.html    # Entire app — HTML, CSS, and JS in one file
└── README.md
```

Everything is self-contained in a single file for easy sharing and deployment.

---

## Dashboard Tabs

### Commodity Prices
Pulls live data from the EIA API for six major energy commodities. Each card shows the current price, unit, reporting period, and period-over-period percentage change. Click any card for a 10-period price history table. The chart below shows 52 weeks of WTI or Henry Hub data, switchable via buttons.

### Energy Production
U.S. production metrics for crude oil, natural gas, coal, and total electricity. Includes an electricity generation mix breakdown by fuel source (natural gas, coal, nuclear, wind, solar, hydro) and a 52-week bar chart of weekly crude oil production.

### Energy Stocks
Live stock quotes for 10 major energy companies sourced from Finnhub. The top summary shows sector gainers, losers, and average sector change. Click any company row for a fundamentals modal showing P/E ratio, EPS, dividend yield, 52-week high/low, and beta.

### Research Reports
Cards linking directly to EIA publications — STEO, AEO, IEO, Weekly Petroleum Status Report, Monthly Energy Review, Electric Power Monthly, Natural Gas Storage Report, Quarterly Coal Report, and Today in Energy. Also includes a full publications table with release frequency.

---

## EIA Series Used

| Metric | EIA Series ID |
|---|---|
| WTI Crude Oil | `PET.RWTC.W` |
| Brent Crude Oil | `PET.RBRTE.D` |
| Henry Hub Natural Gas | `NG.RNGWHHD.D` |
| RBOB Gasoline | `PET.EER_EPMRR_PF4_RGC_DPG.W` |
| No.2 Heating Oil | `PET.EPD2DXL0_PF4_Y35NY_DPG.W` |
| Propane (Mont Belvieu) | `PET.EER_EPLLPA_PF4_Y35NY_DPG.W` |
| U.S. Crude Production | `PET.WCRFPUS2.W` |
| Dry Nat Gas Production | `NG.N9070US2.W` |
| Total Electricity Gen | `TOTAL.ELETPUS.M` |

---

## Energy Stocks Tracked

`XOM` · `CVX` · `COP` · `SLB` · `EOG` · `PSX` · `MPC` · `NEE` · `OXY` · `DVN`

To add or remove tickers, edit the `ENERGY_TICKERS` array in the script section.

---

## Limitations

- **EIA data is not real-time** — most series update weekly or monthly depending on the publication schedule
- **Finnhub free tier** — 60 API calls/minute; no uptime SLA; US stocks only on free plan
- **No backend / no caching** — each page load fetches fresh from the APIs directly; all data lives in memory
- **CORS** — both EIA and Finnhub support browser-side requests; no proxy needed
- **Electricity mix chart** — currently uses static approximate percentages; a future version can wire this to live EIA generation data

---

## Roadmap

- [ ] Wire electricity generation mix to live EIA data by fuel type
- [ ] Add FRED macroeconomic overlay (GDP, CPI, interest rates)
- [ ] Add NewsAPI / RSS feed panel for energy news headlines
- [ ] Add company earnings calendar via Finnhub
- [ ] Add localStorage caching to reduce API calls on refresh
- [ ] Add export to CSV for price and production data
- [ ] Dark/light theme toggle

---

## License

MIT — free to use, modify, and distribute.

---

## Acknowledgements

- [U.S. Energy Information Administration](https://www.eia.gov/) — public domain energy data
- [Finnhub](https://finnhub.io/) — market data API
- [Chart.js](https://www.chartjs.org/) — charting library
- [IBM Plex fonts](https://www.ibm.com/plex/) — typography
