from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

project_folder = Path(__file__).resolve().parent.parent
df = pd.read_csv(project_folder / "data" / "gait.csv")

figures_folder = project_folder / "figures"
figures_folder.mkdir(exist_ok=True)

# Translate the dataset's numeric codes into readable labels.
conditions = {1: "Normal", 2: "Knee brace", 3: "Ankle brace"}
joints = {1: "Ankle", 2: "Knee", 3: "Hip"}

# Select participant 1's right leg, keeping every walking cycle.
participant = df[
    (df["subject"] == 1)
    & (df["leg"] == 2)
]

# Create three graphs side by side.
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True)

for ax, (joint_code, joint_name) in zip(axes, joints.items()):
    for condition_code, condition_name in conditions.items():

        selected = participant[
            (participant["joint"] == joint_code)
            & (participant["condition"] == condition_code)
        ]

        # Average the 10 cycles at each gait-cycle percentage.
        mean_curve = selected.groupby("time")["angle"].mean()

        ax.plot(
            mean_curve.index,
            mean_curve.values,
            label=condition_name
        )

    ax.set_title(joint_name)
    ax.set_xlabel("Gait cycle (%)")
    ax.set_ylabel("Joint angle (degrees)")
    ax.grid(True, alpha=0.3)

axes[0].legend()
fig.suptitle("Participant 1: right leg, mean of 10 walking cycles")
fig.tight_layout()

fig.savefig(
    figures_folder / "participant1_all_joints.png",
    dpi=300
)

# Calculate ROM separately for each individual cycle.
cycle_rom = (
    participant
    .groupby(["condition", "joint", "replication"])["angle"]
    .agg(["min", "max"])
)

cycle_rom["rom"] = cycle_rom["max"] - cycle_rom["min"]

# Summarize those cycle ROMs for each condition and joint.
rom_summary = (
    cycle_rom
    .groupby(["condition", "joint"])["rom"]
    .agg(["mean", "std"])
    .reset_index()
)

rom_summary["condition"] = rom_summary["condition"].map(conditions)
rom_summary["joint"] = rom_summary["joint"].map(joints)

print("\nParticipant 1, right leg: ROM in degrees")
print(rom_summary.round(2).to_string(index=False))

# Include all participants, keeping the right leg.
right_leg = df[df["leg"] == 2]

# Calculate ROM for each cycle separately.
all_cycle_rom = (
    right_leg
    .groupby(["subject", "condition", "joint", "replication"])["angle"]
    .agg(["min", "max"])
    .reset_index()
)

all_cycle_rom["rom"] = all_cycle_rom["max"] - all_cycle_rom["min"]

# Average the 10 cycle ROMs within each participant.
subject_rom = (
    all_cycle_rom
    .groupby(["subject", "condition", "joint"])["rom"]
    .mean()
    .reset_index()
)

# Summarize across the 10 participants.
group_summary = (
    subject_rom
    .groupby(["condition", "joint"])["rom"]
    .agg(["mean", "std", "count"])
    .reset_index()
)

# Give the tables readable labels.
for table in [all_cycle_rom, subject_rom, group_summary]:
    table["condition"] = table["condition"].map(conditions)
    table["joint"] = table["joint"].map(joints)

# Save tables for later analysis and reporting.
results_folder = project_folder / "results"
results_folder.mkdir(exist_ok=True)

all_cycle_rom.to_csv(results_folder / "cycle_rom.csv", index=False)
subject_rom.to_csv(results_folder / "subject_rom.csv", index=False)
group_summary.to_csv(results_folder / "group_rom_summary.csv", index=False)

print("\nAll participants, right leg: ROM in degrees")
print(group_summary.round(2).to_string(index=False))

# Set the display order of walking conditions.
condition_order = ["Normal", "Knee brace", "Ankle brace"]

fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))

for ax, joint_name in zip(axes2, joints.values()):

    # Keep one joint, then arrange one row per participant.
    joint_data = subject_rom[subject_rom["joint"] == joint_name]

    paired = joint_data.pivot(
        index="subject",
        columns="condition",
        values="rom"
    )

    paired = paired[condition_order]

    # Draw each participant's results.
    for subject_id, row in paired.iterrows():
        ax.plot(
            condition_order,
            row.values,
            marker="o",
            color="steelblue",
            alpha=0.4,
            linewidth=1
        )

    # Add the average across participants.
    ax.plot(
        condition_order,
        paired.mean().values,
        marker="o",
        color="black",
        linewidth=3,
        label="Group mean"
    )

    ax.set_title(joint_name)
    ax.set_ylabel("Range of motion (degrees)")
    ax.grid(True, alpha=0.3)

axes2[0].legend()
fig2.suptitle("Right-leg ROM: individual participants and group mean")
fig2.tight_layout()

fig2.savefig(
    figures_folder / "all_participants_rom.png",
    dpi=300
)
plt.show()