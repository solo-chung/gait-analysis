from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

project_folder = Path(__file__).resolve().parent.parent
results_folder = project_folder / "results"

# Load the participant averages saved by our analysis script.
df = pd.read_csv(results_folder / "subject_rom.csv")

comparisons = []
fig, axes = plt.subplots(3, 2, figsize=(10, 12))

for joint_index, joint in enumerate(["Ankle", "Knee", "Hip"]):
    paired = df[df["joint"] == joint].pivot(
        index="subject",
        columns="condition",
        values="rom"
    )

    # Check that all 10 participants have all three measurements.
    assert len(paired) == 10
    assert not paired.isna().any().any()

    for brace_index, brace in enumerate(["Knee brace", "Ankle brace"]):
        normal = paired["Normal"]
        braced = paired[brace]
        difference = braced - normal

        test = stats.ttest_rel(braced, normal)
        ci = test.confidence_interval(confidence_level=0.95)

        comparisons.append({
            "joint": joint,
            "comparison": f"{brace} vs Normal",
            "n": len(difference),
            "mean_change_deg": difference.mean(),
            "ci95_low": ci.low,
            "ci95_high": ci.high,
            "p_raw": test.pvalue
        })

        # Inspect the distribution of participant differences.
        ax = axes[joint_index, brace_index]
        stats.probplot(difference, dist="norm", plot=ax)
        ax.set_title(f"{joint}: {brace} minus Normal")

results = pd.DataFrame(comparisons)

# Adjust for the six comparisons using Bonferroni correction.
results["p_adjusted"] = (
    results["p_raw"] * len(results)
).clip(upper=1)

results.to_csv(results_folder / "paired_rom_tests.csv", index=False)

print("\nPaired comparisons: braced minus normal")
print(results.to_string(index=False, float_format=lambda x: f"{x:.4g}"))

fig.suptitle("Normal Q-Q plots of participant ROM differences")
fig.tight_layout()
fig.savefig(
    project_folder / "figures" / "rom_difference_checks.png",
    dpi=300
)

plt.show()