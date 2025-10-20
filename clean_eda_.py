import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

tree = pd.read_csv("IL_tree.csv", low_memory=False)
plot = pd.read_csv("IL_plot.csv", low_memory=False)
year_col = "INVYR" 
mortality_df = pd.read_csv("IL_plot_mortality_by_visit.csv")

#This part of the code checks to ensure that the count for number of visits is right
plot_unique = plot.drop_duplicates(subset=["STATECD", "COUNTYCD", "PLOT", year_col])
visit_counts = (
    plot_unique
    .groupby(["STATECD", "COUNTYCD", "PLOT"])[year_col]
    .nunique()
    .rename("num_visits")
    .reset_index()
)
summary = visit_counts["num_visits"].value_counts().sort_index()
print("Number of Illinois plots by visit count:")
print(summary)


#This creates the geom plot
lat_col = next((c for c in plot.columns if "LAT" in c.upper()), None)
lon_col = next((c for c in plot.columns if "LON" in c.upper()), None)
if not lat_col or not lon_col:
    raise KeyError("No latitude/longitude columns found in IL_plot.csv")
print("Using coords:", lat_col, lon_col)

merged = mortality_df.merge(
    plot[["STATECD", "COUNTYCD", "PLOT", lat_col, lon_col]],
    on=["STATECD", "COUNTYCD", "PLOT"],
    how="left"
).dropna(subset=[lat_col, lon_col])

print("Merged plots with coordinates:", len(merged))

merged["mortality_pct"] = merged["mortality_pct"].clip(0, 100)
BINS = 70 

plt.figure(figsize=(7.5, 6))
hb = plt.hexbin(
    merged[lon_col],
    merged[lat_col],
    C=merged["mortality_pct"],           
    gridsize=BINS,                       
    reduce_C_function=np.mean,         
    cmap="viridis",
    mincnt=1
)
plt.colorbar(hb, label="Mean % mortality per hexagon")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Regional Patterns of Plot-Level Mortality in Illinois (Hexbin)")
plt.tight_layout()
plt.savefig("IL_mortality_hexbin_map.png", dpi=300, bbox_inches="tight")
plt.close()
print("Saved: IL_mortality_hexbin_map.png")


#Plot for histogram
mortality_plot = mortality_df.copy()
plt.figure(figsize=(7,5))
sns.histplot(mortality_plot["mortality_pct"], bins=20, color="darkred", edgecolor=None)
plt.axvline(50, ls="--", color="black", label="50%")
plt.axvline(80, ls="--", color="gray", label="80%")
plt.title("Plot-Level Mortality Between Successive Visits (Illinois)")
plt.xlabel("Percent mortality per interval")
plt.ylabel("Number of plots")
plt.legend()
plt.tight_layout()
plt.savefig("IL_mortality_hist_by_plot_pairs.png", dpi=300, bbox_inches="tight")
plt.close()

print("IL_mortality_hist_by_plot_pairs.png saved")


