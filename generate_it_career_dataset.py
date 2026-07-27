import numpy as np
import pandas as pd


RANDOM_SEED = 42
TOTAL_SAMPLES = 500
OUTPUT_FILE = "it_career_matching_dataset.csv"

ZODIACS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

MBTI_TYPES = [
    "INTJ",
    "INTP",
    "ENTJ",
    "ENTP",
    "INFJ",
    "INFP",
    "ENFJ",
    "ENFP",
    "ISTJ",
    "ISFJ",
    "ESTJ",
    "ESFJ",
    "ISTP",
    "ISFP",
    "ESTP",
    "ESFP",
    "Unknown",
]

ENERGY_TYPES = ["Introvert", "Extrovert", "Ambivert"]
OPTIONS = list("ABCDEFGHI")

ROLE_MAP = {
    "A": "Software_Development",
    "B": "UI_UX_Design",
    "C": "Data_Science_Analytics",
    "D": "Cyber_Security_Networking",
    "E": "Project_Management_Business",
    "F": "AI_ML_Intelligent_Systems",
    "G": "Cloud_Engineering_DevOps",
    "H": "Game_Development",
    "I": "IoT_Hardware_Embedded",
}

QUESTION_COLUMNS = [
    "Q4_Project_Instinct",
    "Q5_Assembly_Style",
    "Q6_Trip_Role",
    "Q7_Puzzle_Feeling",
    "Q8_Cleaning_Style",
    "Q9_Games_Activities",
    "Q10_Learning_Style",
    "Q11_Frustration",
    "Q12_Proud_Compliment",
]

TARGET_COLUMNS = [f"Role_{role}" for role in ROLE_MAP.values()]

ROLE_MBTI_WEIGHTS = {
    "A": {"INTJ": 3.0, "INTP": 2.8, "ISTJ": 2.0, "ENTP": 1.8, "ISTP": 1.7},
    "B": {"ISFP": 3.0, "INFP": 2.8, "ENFP": 2.2, "INFJ": 1.8, "ESFP": 1.7},
    "C": {"INTP": 3.0, "INTJ": 2.6, "ISTJ": 2.0, "ENTJ": 1.8, "INFJ": 1.5},
    "D": {"ISTJ": 3.0, "INTJ": 2.4, "ISTP": 2.2, "ESTP": 2.0, "ESTJ": 1.8},
    "E": {"ENTJ": 3.0, "ENFJ": 2.8, "ESTJ": 2.5, "ESFJ": 2.0, "ENFP": 1.6},
    "F": {"INTJ": 3.0, "INTP": 2.8, "ENTP": 2.0, "INFJ": 1.8, "ENTJ": 1.6},
    "G": {"ISTJ": 2.6, "INTJ": 2.3, "ESTJ": 2.1, "ISTP": 2.0, "ENTJ": 1.7},
    "H": {"ENTP": 2.7, "ENFP": 2.5, "ISTP": 2.0, "ISFP": 1.9, "INTP": 1.8},
    "I": {"ISTP": 3.0, "INTP": 2.2, "ISTJ": 2.0, "ESTP": 1.8, "INTJ": 1.6},
}

ROLE_ENERGY_WEIGHTS = {
    "A": {"Introvert": 2.5, "Ambivert": 1.6, "Extrovert": 0.9},
    "B": {"Ambivert": 2.2, "Introvert": 1.6, "Extrovert": 1.3},
    "C": {"Introvert": 2.4, "Ambivert": 1.7, "Extrovert": 0.8},
    "D": {"Introvert": 2.2, "Ambivert": 1.6, "Extrovert": 1.0},
    "E": {"Extrovert": 2.6, "Ambivert": 2.0, "Introvert": 0.8},
    "F": {"Introvert": 2.4, "Ambivert": 1.7, "Extrovert": 0.8},
    "G": {"Ambivert": 2.2, "Introvert": 1.8, "Extrovert": 1.1},
    "H": {"Ambivert": 2.0, "Introvert": 1.5, "Extrovert": 1.5},
    "I": {"Introvert": 2.0, "Ambivert": 1.8, "Extrovert": 1.0},
}

SECONDARY_OPTIONS = {
    "A": ["F", "C", "G"],
    "B": ["H", "E", "A"],
    "C": ["F", "A", "D"],
    "D": ["G", "A", "C"],
    "E": ["B", "G", "C"],
    "F": ["A", "C", "I"],
    "G": ["D", "A", "E"],
    "H": ["B", "A", "F"],
    "I": ["G", "F", "D"],
}


def softmax(values, temperature=0.8):
    scaled = np.asarray(values, dtype=float) / temperature
    scaled -= np.max(scaled)
    exp_values = np.exp(scaled)
    return exp_values / exp_values.sum()


def weighted_choice(rng, choices, weights):
    probabilities = np.asarray(weights, dtype=float)
    probabilities /= probabilities.sum()
    return rng.choice(choices, p=probabilities)


def make_weight_vector(primary_option):
    weights = np.ones(len(OPTIONS), dtype=float)
    weights[OPTIONS.index(primary_option)] = 7.0

    for rank, option in enumerate(SECONDARY_OPTIONS[primary_option]):
        weights[OPTIONS.index(option)] += 2.2 - (rank * 0.45)

    return weights


def sample_mbti(rng, primary_option):
    weights = np.ones(len(MBTI_TYPES), dtype=float) * 0.65
    weights[MBTI_TYPES.index("Unknown")] = 0.45

    for mbti, boost in ROLE_MBTI_WEIGHTS[primary_option].items():
        weights[MBTI_TYPES.index(mbti)] += boost

    return weighted_choice(rng, MBTI_TYPES, weights)


def sample_energy(rng, primary_option):
    weights = [ROLE_ENERGY_WEIGHTS[primary_option][energy] for energy in ENERGY_TYPES]
    return weighted_choice(rng, ENERGY_TYPES, weights)


def balanced_archetypes(total_samples):
    base_count = total_samples // len(OPTIONS)
    remainder = total_samples % len(OPTIONS)

    archetypes = []
    for index, option in enumerate(OPTIONS):
        count = base_count + int(index < remainder)
        archetypes.extend([option] * count)

    return archetypes


def generate_dataset(total_samples=TOTAL_SAMPLES, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    archetypes = balanced_archetypes(total_samples)
    rng.shuffle(archetypes)

    rows = []
    primary_roles = []
    for primary_option in archetypes:
        primary_roles.append(ROLE_MAP[primary_option])
        row = {
            "Q1_Zodiac": rng.choice(ZODIACS),
            "Q2_MBTI": sample_mbti(rng, primary_option),
            "Q3_Energy": sample_energy(rng, primary_option),
        }

        answer_weights = make_weight_vector(primary_option)
        primary_bias = rng.uniform(0.60, 0.80)
        secondary_distribution = answer_weights.copy()
        secondary_distribution[OPTIONS.index(primary_option)] = 0.0
        secondary_distribution /= secondary_distribution.sum()

        option_probabilities = secondary_distribution * (1.0 - primary_bias)
        option_probabilities[OPTIONS.index(primary_option)] = primary_bias

        answers = rng.choice(OPTIONS, size=len(QUESTION_COLUMNS), p=option_probabilities)
        row.update(dict(zip(QUESTION_COLUMNS, answers)))

        counts = np.array([np.sum(answers == option) for option in OPTIONS], dtype=float)
        counts += rng.normal(loc=0.0, scale=0.12, size=len(OPTIONS))
        counts = np.clip(counts, 0.0, None)

        role_probabilities = softmax(counts, temperature=0.8)
        role_probabilities += rng.uniform(0.0005, 0.004, size=len(OPTIONS))
        role_probabilities /= role_probabilities.sum()

        for column, probability in zip(TARGET_COLUMNS, role_probabilities):
            row[column] = round(float(probability), 6)

        # Correct the final role after rounding so every row sums exactly to 1.0.
        rounded_sum = sum(row[column] for column in TARGET_COLUMNS)
        row[TARGET_COLUMNS[-1]] = round(row[TARGET_COLUMNS[-1]] + (1.0 - rounded_sum), 6)

        rows.append(row)

    return pd.DataFrame(rows), pd.Series(primary_roles, name="Primary_Archetype")


def main():
    df, primary_roles = generate_dataset()
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
    print("\nDataset preview:")
    print(df.head())
    print("\nGenerated primary archetype distribution:")
    print(primary_roles.value_counts().sort_index())
    print("\nTop Softmax role distribution:")
    top_roles = df[TARGET_COLUMNS].idxmax(axis=1).str.replace("Role_", "", regex=False)
    print(top_roles.value_counts().sort_index())
    print("\nQ4-Q12 answer distribution:")
    print(df[QUESTION_COLUMNS].stack().value_counts(normalize=True).sort_index().round(4))
    print("\nNumeric target summary:")
    print(df[TARGET_COLUMNS].describe())
    print("\nTarget row-sum check:")
    print(df[TARGET_COLUMNS].sum(axis=1).describe())


if __name__ == "__main__":
    main()
