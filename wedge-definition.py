import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------
# 1. Trajectory Data & Parameters
# -------------------------------------------------------------------------
# Historical trajectory (2020 - 2023)
hist_years = np.array([2020, 2021, 2022, 2023])
hist_emissions = np.array([53.9, 58.3, 58.6, 55.5])

# Forward baseline projection starting from 2023 to 2050
start_year = 2023
end_year = 2050
base_2023 = 55.5
bau_2050 = 95.6

# Calculate wedge_h to achieve a Net Zero target of 0 MtCO2e/year
target_2050_emissions = 0.0
total_reduction_needed = bau_2050 - target_2050_emissions
wedge_h = 3
total_wedges = int(round(total_reduction_needed / wedge_h))

# -------------------------------------------------------------------------
# 2. Plotting
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
ax.set_facecolor("white")
ax.grid(axis="y", color="#eaeaea", linestyle="-", linewidth=1, zorder=0)

# 1. Individual wedge fan lines (anchored at 2023)
for i in range(total_wedges + 1):
    y_end = bau_2050 - (i * wedge_h)
    ax.plot([start_year, end_year], [base_2023, y_end],
            color="#b5b5b5", linewidth=0.6, alpha=0.7, zorder=1)

# 3. Main Pathways
# Historical line (2020 - 2023)
ax.plot(hist_years, hist_emissions, color="black", linewidth=2.5, zorder=5)

# BAU line & Net Zero target line from 2023 to 2050
target_2050 = bau_2050 - (total_wedges * wedge_h)
ax.plot([start_year, end_year], [base_2023, bau_2050], color="#333333", linewidth=1.8, zorder=4)
ax.plot([start_year, end_year], [base_2023, target_2050], color="#333333", linewidth=1.8, zorder=4)

# Dotted vertical reference at 2023
ax.vlines(x=start_year, ymin=0, ymax=base_2023, colors="black", linestyles="dotted", linewidth=1.2, zorder=3)

# -------------------------------------------------------------------------
# 3. Annotations & Labels
# -------------------------------------------------------------------------
# Scenario labels on the right
ax.text(end_year + 0.6, bau_2050, "…… BAU", va="center", ha="left", fontsize=12, weight="bold")
ax.text(end_year + 0.6, target_2050, "…… NZS", va="center", ha="left", fontsize=12, weight="bold")

# Non-overlapping point annotation at 2023 branch point
ax.annotate(f"{base_2023:.1f} Mt",
            xy=(start_year, base_2023),
            xytext=(start_year - 0.8, base_2023 + 4),
            fontsize=10, weight="bold", color="#222222")

# Single wedge indicator
w_idx = 7
mid_x = 2043
frac = (mid_x - start_year) / (end_year - start_year)
y_top_mid = base_2023 + frac * ((bau_2050 - (w_idx * wedge_h)) - base_2023)
y_bot_mid = base_2023 + frac * ((bau_2050 - ((w_idx + 1) * wedge_h)) - base_2023)

ax.annotate(r"↓ $\it{One}$" "\n  " r"$\it{wedge}$" "\n↑",
            xy=(mid_x, (y_top_mid + y_bot_mid) / 2),
            ha="center", va="center", fontsize=9, color="#222222")

# -----------------------------------------------------------------
# 4. Axes & Spines Configuration
# -----------------------------------------------------------------
ax.set_title(f"Singapore Climate Wedges: {total_wedges} Wedges (3 " + r"$\mathrm{MtCO_2e\ y^{-1}}$ each)",
             fontsize=12, pad=20)
ax.set_ylabel(r"Annual GHG Emissions ($\mathrm{MtCO_2e\ year^{-1}}$)", fontsize=12)

ax.set_xlim(2019, 2056)
ax.set_ylim(-2, 110)
ax.set_xticks([2020, 2023, 2030, 2040, 2050])

for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
plt.savefig("singapore_stabilization_wedges.png", dpi=300, bbox_inches="tight")
plt.show()
