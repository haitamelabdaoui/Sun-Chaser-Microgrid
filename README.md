# Sun-Chaser: Techno-Economic & Financial Optimization of PV + BESS Microgrids

> **Engineering Research & Development Project** | IMT Mines Albi & Lycée Albert Schweitzer | 2024–2026  
> *A comprehensive 30-minute resolution simulation, EMS control framework, and 20-year financial viability assessment for residential microgrids in Mulhouse, France.*

---

## Research Question

**How does a dual-axis sun-tracking PV system combined with Battery Energy Storage Systems (BESS) compare against a static PV installation in terms of self-consumption efficiency, grid dependency, and long-term financial performance (NPV, IRR, LCOE, PBP)?**

---

## Objective

Compare the techno-economic performance of two 7.6 kWp residential microgrid configurations:

* **Fixed PV System + BESS**: Static panel orientation ($\alpha = 180^\circ$ azimuth, $\beta = 45^\circ$ tilt) + 10 kWh Huawei LUNA2000 BESS.
* **Sun-Chaser Dual-Axis Tracker + BESS**: Real-time dual-axis sun-tracking PV system + 10 kWh Huawei LUNA2000 BESS.

Using high-resolution real solar irradiance, cell temperature dynamics, dynamic TOU electricity pricing, and household load profiles for **Mulhouse, Alsace, France (2024)**.

---

## Key Results

> **PV Yield Gain**: **+19.85%** annual energy generation achieved by the Sun-Chaser dual-axis tracking system over static tilt.  
> **Fixed PV + BESS**: CAPEX = €11,900 | **IRR (TRI) = 14.8%** | **Payback (PBP) = 8 Years** | 20-Year NPV = **€16,023.50**  
> **Sun-Chaser Tracker + BESS**: CAPEX = €15,100 | **20-Year NPV = €16,207.92** | **Payback (PBP) = ~9.1 Years**  

---

## Methodology

### 1. Data Processing & Temporal Resolution
* **30-Minute Interpolation**: High-resolution processing of solar irradiance ($W/m^2$), ambient temperature ($^\circ C$), and household load vectors ($kW$) over 17,520 timesteps ($365 \text{ days} \times 48 \text{ intervals/day}$).
* **Dynamic Tariff Model**: Hourly peak/off-peak (HP/HC) grid electricity purchase pricing alongside EDF OA Feed-in Tariff ($\text{Feed-in Tariff} = 0.1301 \text{ €/kWh}$).

### 2. Thermal & Solar Yield Modeling
Cell temperature-dependent power output calculation incorporating thermal losses:

$$T_{cell}(t) = T_{amb}(t) + \frac{NOCT - 20}{800} \cdot G(t)$$

$$P_{gen}(t) = \eta_{STC} \cdot A \cdot G(t) \cdot \left[ 1 - \gamma \cdot (T_{cell}(t) - 25) \right]$$

### 3. EMS Control & BESS Dispatch Engine
Energy Management System (EMS) strategy executing real-time power balance optimization:
* **Priority 1**: Direct load self-consumption.
* **Priority 2**: BESS charging up to 100% State-of-Charge (SoC).
* **Priority 3**: Grid injection of surplus power at feed-in tariff.
* **Deficit Management**: Discharging BESS down to 10% Depth-of-Discharge (DoD) before grid purchase.

### 4. 20-Year Financial Engine & Valuation
Discounted cash flow model incorporating real-world economic dynamics:
* **Discount Rate (WACC)**: $d = 4.0\%$
* **Electricity Price Inflation**: $r_e = 3.0\% \text{ / year}$
* **PV System Degradation**: $\delta = 0.5\% \text{ / year}$
* **Major Maintenance Event**: Inverter replacement (€1,000) at Year 10.

Net Present Value formulation:

$$NPV = -CAPEX + \sum_{t=1}^{20} \frac{S_t \cdot (1 + r_e)^{t-1} - (OPEX_t + M_t)}{(1 + d)^t}$$

---

## Repository Structure

```text
Sun-Chaser-Microgrid/
├── Analyse_economique_financiere/
│   ├── analyse_financiere.py                   # Core 20-year DCF & financial KPI engine
│   ├── graphiques_finance.py                   # High-res publication chart generator
│   ├── simulation_BESS_annuelle_avec_prix.csv  # 30-min simulation dataset with tariffs
│   └── Figures/
│       ├── bilan_mensuel_injection_soutirage.png # Monthly grid flux bar chart (+/-)
│       ├── cash_flow_20years.png                 # 20-year NPV & payback trajectory
│       └── net_portfolio_365d.png                # 365-day cumulative expenditure chart
├── Simulation_BESS/
│   ├── bess_ems.py                             # BESS SoC & EMS rule-based dispatch
│   ├── data_loader.py                          # Data ingestion & interpolation pipelines
│   ├── main.py                                 # Annual microgrid simulation runner
│   ├── tracees_simulation_BESS.py              # Power profile visualizer
│   └── Figures/                                # Dispatch profile charts
└── Suite_TIPE/
    ├── BDD_consomation/                        # Household load profile algorithms
    └── Interpolations_30M/                     # Solar geometry & irradiance modeling
