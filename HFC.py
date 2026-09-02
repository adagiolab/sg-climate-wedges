import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# 1. EXACT HISTORICAL TIME SERIES (2010-2022 from NID Table 24 in kt CO2e)
# ----------------------------------------------------------------------
hist_emissions = {
    2010: 1084.20, 2011: 1252.29, 2012: 1409.79, 2013: 1596.10, 2014: 1811.41,
    2015: 1912.65, 2016: 2066.81, 2017: 2409.44, 2018: 2837.09, 2019: 3087.92,
    2020: 3321.11, 2021: 3664.84, 2022: 4167.77
}

# ----------------------------------------------------------------------
# 2. MODEL PARAMETERS (NID Page 114-115)
# ----------------------------------------------------------------------
L = 10                  # Average lifespan (years)
x = 0.10                # Operational leak rate (10%/year)
p = 1.00                # Residual charge at disposal (100%)
eta = 0.80              # Recovery efficiency (80%)
g_bau = 0.03            # Projected BAU growth rate (3%/year)

# ----------------------------------------------------------------------
# 3. CONVERT 2010-2022 EMISSIONS TO HISTORICAL INFLOWS (M_t)
# ----------------------------------------------------------------------
hist_cagr_10yr = (hist_emissions[2020] / hist_emissions[2010]) ** (1/10) - 1.0
sum_weights_2020 = sum((1.0 + hist_cagr_10yr) ** (-k) for k in range(L))
scale_factor = hist_emissions[2020] / ((sum_weights_2020 * x) + ((1.0 + hist_cagr_10yr)**(-L) * (1.0 - eta) * p))
m_to_e_ratio = scale_factor / hist_emissions[2020]

inflows = {yr: hist_emissions[yr] * m_to_e_ratio for yr in hist_emissions}

# ----------------------------------------------------------------------
# 4. PROJECT FROM 2020 to 2050
# ----------------------------------------------------------------------
def run_simulation(scenario='kigali_singapore'):
    sim_inflows = inflows.copy()
    kigali_baseline = np.mean([sim_inflows[2020], sim_inflows[2021], sim_inflows[2022]])
    records = []
    
    for t in range(2020, 2051):
        if t <= 2022:
            m_t = sim_inflows[t]
        else:
            if scenario == 'phaseout_2030':
                if 2024 <= t <= 2028:
                    m_t = kigali_baseline
                elif t == 2029:
                    m_t = 0.90 * kigali_baseline
                elif t >= 2030:
                    m_t = 0.0
                else:
                    m_t = sim_inflows[2022]

            elif scenario == 'kigali_singapore':
                if 2024 <= t <= 2028:
                    m_t = 1.00 * kigali_baseline      # 2024-2028: Freeze
                elif 2029 <= t <= 2034:
                    m_t = 0.90 * kigali_baseline      # 2029-2034: -10%
                elif 2035 <= t <= 2039:
                    m_t = 0.70 * kigali_baseline      # 2035-2039: -30%
                elif 2040 <= t <= 2044:
                    m_t = 0.50 * kigali_baseline      # 2040-2044: -50%
                elif t >= 2045:
                    m_t = 0.20 * kigali_baseline      # 2045+: -80%
                else:
                    m_t = sim_inflows[2022]

            else:  # BAU (+3%/year)
                m_t = sim_inflows[2022] * ((1.0 + g_bau) ** (t - 2022))
            
            sim_inflows[t] = m_t
        
        bank_t = sum(sim_inflows.get(k, 0.0) for k in range(t - L + 1, t + 1))
        e_op_t = bank_t * x
        retiring_vintage = sim_inflows.get(t - L, 0.0)
        e_disp_t = retiring_vintage * (1.0 - eta) * p
        e_total_t = e_op_t + e_disp_t

        if t in hist_emission:
            e_total_t = hist_emissions[t]
            model_calculated_total_components = e_op_t + e_disp_t
            if model_calculated_total_components !=0:
                scaling_factor = e_total_t / model_calculated_total_components
                e_op_t = e_op_t * scaling_factor
                e_disp_t = e_disp_t * scaling_factor
            else:
                pass
        else:
            e_total_t = e_op_t + e_disp_t
        
        records.append({
            'Year': t,
            'Inflow_M': m_t,
            'Bank': bank_t,
            'Operational_Emissions': e_op_t,
            'Disposal_Emissions': e_disp_t,
            'Total_Emissions': e_total_t
        })
        
    return pd.DataFrame(records)

# Run simulations
df_phaseout = run_simulation('phaseout_2030')
df_kigali = run_simulation('kigali_singapore')
df_bau = run_simulation('bau')

# ----------------------------------------------------------------------
# 5. PRINT SUMMARY TABLE
# ----------------------------------------------------------------------
milestone_years = [2020, 2022, 2025, 2030, 2035, 2040, 2045, 2050]

summary_df = pd.DataFrame({
    'Year': milestone_years,
    'BAU Total (kt)': df_bau.loc[df_bau['Year'].isin(milestone_years), 'Total_Emissions'].values,
    'Kigali Total (kt)': df_kigali.loc[df_kigali['Year'].isin(milestone_years), 'Total_Emissions'].values,
    '2030 Phase-Out Total (kt)': df_phaseout.loc[df_phaseout['Year'].isin(milestone_years), 'Total_Emissions'].values,
    '2030 Phase-Out Op (kt)': df_phaseout.loc[df_phaseout['Year'].isin(milestone_years), 'Operational_Emissions'].values,
    '2030 Phase-Out EOL (kt)': df_phaseout.loc[df_phaseout['Year'].isin(milestone_years), 'Disposal_Emissions'].values
})

print("\n" + "="*80)
print("              SINGAPORE HFC EMISSIONS PROJECTIONS (kt CO2e)             ")
print("="*80)
print(summary_df.to_string(index=False, float_format="%.2f"))
print("="*80 + "\n")

# ----------------------------------------------------------------------
# 6. GENERATE COMPARISON CHART
# ----------------------------------------------------------------------
plt.figure(figsize=(12, 6), dpi=300)

hist_year_list = list(hist_emissions.keys())
hist_values_list = list(hist_emissions.values())
plt.plot(hist_years_list, hist_values_list, color='black', linewidth=2.5, label='Historical Emissions')

last_hist_year = max(hist_emissions.keys())

df_bau_proj = df_bau[df_bau['Year'] >= last_hist_year]
df_kigali_proj = df_kigali[df_kigali['Year'] >= last_hist_year]
df_phaseout_proj = df_phaseout[df_phaseout['Year'] >= last_hist_year]

plt.plot(df_bau['Year'], df_bau['Total_Emissions'], color='#d62728', linestyle='--', linewidth=2, label='BAU')
plt.plot(df_kigali['Year'], df_kigali['Total_Emissions'], color='#2ca02c', linewidth=2.5, label='Kigali Phase-Down')
plt.plot(df_phaseout['Year'], df_phaseout['Total_Emissions'], color='#1f77b4', linewidth=2.5, label='2030 Early Phase-Out')

plt.title('Singapore HFC Emissions Projections (2020–2050)', fontsize=14, fontweight='bold', pad=12)
plt.xlabel('Year', fontsize=11)
plt.ylabel('Emissions (kt $\mathrm{CO_2e}$)', fontsize=11)
plt.xlim(2020, 2050)
plt.ylim(0, 15000)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

plt.tight_layout()
plt.show()
