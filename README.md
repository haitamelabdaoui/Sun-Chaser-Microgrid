# Techno-Economic and Multi-Physical Optimization of a PV + BESS Household Microgrid

> **Engineering Research and Development Project** | IMT Mines Albi and Lycée Albert Schweitzer | Mulhouse, France  
> *A high-resolution 30-minute simulation framework integrating thermodynamic cell modeling, dynamic Enedis load profiling, BESS dispatch, and 20-year financial viability analytics.*

---

## The Story: Why We Built This?
In two years of preparatory class, I spent a lot of time and energy into my TIPE project: optimizing the orientation of solar panels to maximize energy capture.

When I entered engineering school, I faced a choice. I could put all that hard work into a drawer and start something new, or I could take what I already built and make it better. 

I believed that my previous work mattered. Using the new software and green tech skills learned during my first year of engineering studies, I decided to upgrade my physical prototype into a real, working IoT system.

---

## Research Question

**How does a 2-axis tracking solar PV system combined with a Battery Energy Storage System (BESS) compare against a static PV setup in terms of multi-physical efficiency ($PR$, cell temperature dynamics), geometric rooftop footprint, grid self-sufficiency, and long-term financial performance (NPV, IRR, LCOE, PBP)?**

---

## Key Performance Summary

| Metric / Parameter | Fixed PV System (α = 180°, β = 45°) | Sun-Chaser Dual-Axis Tracker | Gain / Variation |
| :--- | :---: | :---: | :---: |
| **Installed Capacity (P<sub>p</sub>)** | 7.60 kWp (20 × 380 W) | 7.60 kWp (20 × 380 W) | — |
| **Active Panel Area (A<sub>pv</sub>)** | 36.0 m² | 36.0 m² | — |
| **Incident Solar Energy (E<sub>inc</sub>)** | 43.01 MWh/year | 51.55 MWh/year | **+19.85%** |
| **Net Electric Production (E<sub>elec</sub>)** | 8.05 MWh/year | 9.63 MWh/year | **+19.52%** (+1,572 kWh/yr) |
| **Annual Conversion Efficiency (η<sub>annual</sub>)** | 18.73% | 18.67% | -0.06% |
| **Performance Ratio (PR)** | 88.70% | 88.46% | -0.24% |
| **CAPEX (PV + 10 kWh BESS)** | **€11,900** | **€15,100** | +26.89% |
| **20-Year Net Present Value (NPV)** | **€16,023.50** | **€16,207.92** | **+€184.42** |
| **Internal Rate of Return (IRR / TRI)** | **14.8%** | **11.2%** | -3.60% |
| **Payback Period (PBP Actualisé)** | **8.0 Years** | **~9.1 Years** | +1.1 Years |

---

## Multi-Physical and Technical Methodology

### 1. PV Module and Cell Efficiency Fundamentals
At Standard Test Conditions (STC: $G_{STC} = 1000 \text{ W/m}^2, T_{STC} = 25^\circ\text{C}$), each $380 \text{ W}$ panel exhibits:
- **Fill Factor ($FF$)**:
  $$FF = \frac{P_{mp}}{V_{oc} \cdot I_{sc}} = 0.7793 \quad (77.93\%)$$
- **Nominal STC Efficiency ($\eta_{STC}$)**:
  $$\eta_{STC} = \frac{P_{mp,STC}}{A_{pv} \cdot G_{STC}} = 0.2111 \quad (21.11\%)$$

### 2. System Loss Decomposition and Performance Ratio ($PR$)
The instantaneous electrical efficiency is governed by the Performance Ratio $PR(t)$:
$$\eta(t) = \eta_{STC} \cdot PR(t)$$

$PR(t)$ breaks down into temperature-dependent and fixed system loss factors:
$$PR(t) = f_{temp}(t) \cdot f_{inv} \cdot f_{c\hat{a}bles} \cdot f_{opt} \cdot f_{salissure}$$

- **Inverter Conversion Factor ($f_{inv}$)**: $0.970$ ($3.0\%$ loss)
- **Ohmic Cable Factor ($f_{c\hat{a}bles}$)**: $0.985$ ($1.5\%$ Joule loss)
- **Optical / IAM Factor ($f_{opt}$)**: $0.975$ ($2.5\%$ incidence reflection loss)
- **Soiling Factor ($f_{salissure}$)**: $0.980$ ($2.0\%$ dust accumulation loss)
- **Overall Constant Loss Factor ($f_{fixe}$)**:
  $$f_{fixe} = 0.980 \cdot 0.975 \cdot 0.985 \cdot 0.970 \approx 0.9129 \quad (8.71\% \text{ fixed losses})$$

---

### 3. Thermodynamic Cell Temperature Engine (Faiman Model Derivation)

The thermal loss factor is driven by cell temperature $T_{cell}(t)$:
$$f_{temp}(t) = 1 + \gamma \cdot \left( T_{cell}(t) - T_{STC} \right) \quad \text{with } \gamma = -0.35\%/^\circ\text{C}$$

#### Physical Heat Balance Derivation
In steady state, the absorbed solar flux balances electrical generation and thermal losses:
$$\alpha_{opt} \cdot G_{inc}(t) = \eta \cdot G_{inc}(t) + q_{pertes}(t)$$
$$q_{pertes}(t) = (\alpha_{opt} - \eta_{STC}) \cdot G_{inc}(t) = U_L(t) \cdot \left( T_{cell}(t) - T_{amb}(t) \right)$$

Where total loss coefficient $U_L(t)$ combines convection, linearized radiation, and conduction:
- **Convective Losses ($h_c$)**: Modeled via **Watmuff et al. (1977)** correlation:
  $$h_c(t) = a_c + b_c \cdot WS(t) \quad (a_c \approx 2.8 \text{ W/m}^2\text{K}, b_c \approx 3.0 \text{ W/m}^2\text{K}/(\text{m/s}))$$
- **Radiative Losses ($h_r$)**: Linearized Stefan-Boltzmann law:
  $$T_{cell}^4 - T_{amb}^4 \approx 4 T_m^3 (T_{cell} - T_{amb}) \implies h_r = 4\epsilon\sigma T_m^3 \approx 5.5 \text{ W/m}^2\text{K}$$
- **Conductive Losses ($h_{cond}$)**: $1.0 \text{ to } 2.0 \text{ W/m}^2\text{K}$ through frame and backing.

#### Faiman Apparent Thermal Coefficients
Dividing the physical loss term $U_L = U_0 + U_1 \cdot WS(t)$ by $(\alpha_{opt} - \eta_{STC}) \approx 0.6889$ yields Faiman's empirical model:
$$T_{cell}(t) = T_{amb}(t) + \frac{G_{inc}(t)}{U_0' + U_1' \cdot WS(t)}$$
$$U_0' = \frac{a_c + h_r + h_{cond}}{\alpha_{opt} - \eta_{STC}} \approx 25.0 \text{ W/m}^2\text{K}, \quad U_1' = \frac{b_c}{\alpha_{opt} - \eta_{STC}} \approx 6.84 \text{ W/m}^2\text{K}/(\text{m/s})$$

---

### 4. Inter-Row Anti-Shading Spacing (GB 50797 Standard)

To prevent mutual shading between 09:00 and 15:00 at the winter solstice, the minimum inter-row distance $D$ for a flat roof in Mulhouse ($\phi = 47.75^\circ$) with panel length $L = 1.80 \text{ m}$ and max tilt $\beta_{max} = 45^\circ$ is:

$$D = L \cos\beta + L \sin\beta \frac{0.707 \tan\phi + 0.4338}{0.707 - 0.4338 \tan\phi}$$

$$D = 1.80 \cos(45^\circ) + 1.80 \sin(45^\circ) \times 5.283 \approx 8.00 \text{ m}$$

- **Rooftop Integration**: On a $125 \text{ m}^2$ roof ($12.5 \text{ m} \text{ N-S} \times 10 \text{ m} \text{ E-W}$), $D = 8.00 \text{ m}$ allows **2 rows of 10 panels** = **20 modules** ($A_{pv} = 36.0 \text{ m}^2$, $P_p = 7.60 \text{ kWp}$).

---

### 5. Dynamic Enedis Load Profiling and EMS Interface

- **Enedis Data Structure**: 30-minute resolution dataset (`coefficients-des-profils.csv`, 17,568 points across 2024).
- **Thermosensitive Adjustment**: Uses `COEFFICIENT_AJUSTE` to capture real temperature-driven heating/cooling demand.
- **Target Household**: 4-person family, all-electric home ($E_{annual} \approx 4,500 - 6,000 \text{ kWh}$).
- **Instantaneous Load**: $P_{load}(t) = C_{ajusté}(t) \times \mathcal{F}_{échelle}$.
- **Net Power Balance Differential**:
  $$\Delta P(t) = P_{gen}(t) - P_{load}(t)$$
  This fundamental value drives real-time IoT energy dispatch decisions (BESS charging/discharging or grid interactions).

---

### 6. BESS State-of-Charge Dynamics and Rule-Based EMS Dispatch Strategy

The Battery Energy Storage System (Huawei LUNA2000, $E_{\text{cap}} = 10 \text{ kWh}$) operates on a 30-minute timestep ($\Delta t = 0.5 \text{ h}$) with charge/discharge efficiencies $\eta_{\text{charge}} = \eta_{\text{discharge}} = 0.95$ (round-trip efficiency $\approx 90\%$).

#### State-of-Charge (SoC) Governing Equation

$$\text{SoC}(t) = \text{SoC}(t - \Delta t) + \frac{P_{\text{batt}}(t) \cdot \Delta t}{E_{\text{cap}}}$$

#### Rule-Based EMS Dispatch Arbitration Algorithm

##### Case 1: Surplus Generation ($\Delta P(t) > 0$)

1. **Priority 1 — Self-Consumption**: Direct load fulfillment.
2. **Priority 2 — BESS Charging**:

$$P_{\text{charge}}(t) = \min\left(\Delta P(t) \cdot \eta_{\text{charge}}, \, P_{\text{max,charge}}, \, \frac{(1 - \text{SoC}(t - \Delta t)) \cdot E_{\text{cap}}}{\Delta t}\right)$$
*Where $\text{SoC}_{\text{max}} = 1.0$ ($100\%$).*

3. **Priority 3 — Grid Injection**: Any remaining surplus power is exported to the grid at EDF OA Feed-in Tariff ($C_{\text{inj}} = 0.1301 \text{ €/kWh}$):

$$P_{\text{inject}}(t) = \Delta P(t) - \frac{P_{\text{charge}}(t)}{\eta_{\text{charge}}}$$

##### Case 2: Power Deficit ($\Delta P(t) < 0$) during Peak Hours (Heures Pleines)

1. **Priority 1 — BESS Discharging**:

$$P_{\text{discharge}}(t) = \min\left(\frac{\vert{}\Delta P(t)\vert{}}{\eta_{\text{discharge}}}, \, P_{\text{max,discharge}}, \, \frac{(\text{SoC}(t - \Delta t) - \text{SoC}_{\text{min}}) \cdot E_{\text{cap}}}{\Delta t}\right)$$
*Where $\text{SoC}_{\text{min}} = 0.10$ ($10\%$ limit / $90\%$ Depth-of-Discharge).*

2. **Priority 2 — Grid Purchase**: Any unfulfilled deficit is drawn from the Enedis grid under Time-of-Use (TOU) peak tariffs:

$$P_{\text{grid}}(t) = \vert{}\Delta P(t)\vert{} - P_{\text{discharge}}(t) \cdot \eta_{\text{discharge}}$$

##### Case 3: Off-Peak Grid Charging Strategy (Heures Creuses - HC)

1. **Off-Peak Tariff Arbitrage**: During scheduled low-cost night intervals ($t \in \text{HC}$, e.g., 02:00–06:00), if $\text{SoC}(t - \Delta t) < \text{SoC}_{\text{target,HC}}$, the EMS charges the BESS directly from the grid at off-peak rates:

$$P_{\text{grid,HC}}(t) = \min\left(P_{\text{max,charge}} \, \frac{(\text{SoC}_{\text{target,HC}} - \text{SoC}(t - \Delta t)) \cdot E_{\text{cap}}}{\Delta t \cdot \eta_{\text{charge}}}\right)$$

2. **Peak Load Shaving**: Stores low-cost electricity overnight to cover high-cost morning consumption peaks.

---

### 7. 20-Year Financial Discounted Cash Flow Engine

- **Discount Rate (WACC)**: $d = 4.0\%$
- **Electricity Price Inflation**: $r_e = 3.0\% / \text{year}$
- **PV Degradation**: $\delta = 0.5\% / \text{year}$
- **Inverter Replacement**: €1,000 overhaul at Year 10.

$$NPV = -CAPEX + \sum_{t=1}^{20} \frac{S_t \cdot (1 + r_e)^{t-1} - (OPEX_t + M_t)}{(1 + d)^t}$$

---

## Repository Structure

```text
Sun-Chaser-Microgrid/
├── Analyse_economique_financiere/
│   ├── analyse_financiere.py                   # 20-year DCF model, NPV, IRR, PBP and LCOE engine
│   ├── graphiques_finance.py                   # High-resolution plotting script
│   ├── simulation_BESS_annuelle_avec_prix.csv  # 30-min annual dataset with dynamic TOU tariffs
│   └── Figures/
│       ├── bilan_mensuel_injection_soutirage.png # Monthly grid flux bar chart (+/-)
│       ├── cash_flow_20years.png                 # 20-year NPV trajectory and payback comparison
│       └── net_portfolio_365d.png                # 365-day cumulative cost chart
├── Simulation_BESS/
│   ├── bess_ems.py                             # Energy Management System and BESS control rules
│   ├── data_loader.py                          # Enedis profile ingestion and 30-min interpolation
│   ├── main.py                                 # Annual microgrid simulation runner
│   ├── tracees_simulation_BESS.py              # Operational profile visualizer
│   └── Figures/                                # Dispatch profile charts
└── Suite_TIPE/
    ├── BDD_consomation/                        # Enedis profiling and load curve scripts
    ├── Interpolations_30M/                     # Solar geometry and irradiance interpolation
    └── TIPE_RESULT_36m2/                       # Physical 36m² PV array yields and Faiman thermal outputs
