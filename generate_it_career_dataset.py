import numpy as np
import pandas as pd


RANDOM_SEED = 42
TOTAL_SAMPLES = 500
OUTPUT_FILE = "it_career_matching_dataset.csv"

ZODIAC_OPTIONS = [
    "Aries / Taurus / Gemini",
    "Cancer / Leo / Virgo",
    "Libra / Scorpio / Sagittarius",
    "Capricorn / Aquarius / Pisces",
    "Other / Skip",
]

MBTI_OPTIONS = [
    "Analyst (INTJ, INTP, ENTJ, ENTP)",
    "Diplomat (INFJ, INFP, ENFJ, ENFP)",
    "Sentinel (ISTJ, ISFJ, ESTJ, ESFJ)",
    "Explorer (ISTP, ISFP, ESTP, ESFP)",
    "Unknown / Skip",
]

ENERGY_OPTIONS = [
    "Deep Focus - တစ်ယောက်တည်း အေးဆေး အာရုံစိုက်ပြီး လုပ်ရတာ ပိုကြိုက်တယ်",
    "Team Energy - သူငယ်ချင်းတွေနဲ့ စကားပြော၊ တိုင်ပင်ပြီး လုပ်ရတာ ပိုကြိုက်တယ်",
    "Flexible - အခြေအနေပေါ်မူတည်ပြီး တစ်ယောက်တည်းရော အဖွဲ့လိုက်ရော ရတယ်",
    "Leader Vibe - အစီအစဉ်ဆွဲပေးပြီး အဖွဲ့ကို ဦးဆောင်ရတာ ပိုကြိုက်တယ်",
    "Hands-on - စာတွေဖတ်နေတာထက် ကိုယ်တိုင် လက်နဲ့ ထိတွေ့စမ်းသပ်ရတာ ကြိုက်တယ်",
]

PERSONALITY_OPTIONS = [
    "Introvert - တစ်ယောက်တည်း အေးဆေး နေရတာ ပိုကြိုက်တယ် (Social Battery မြန်မြန်ကုန်တယ်)",
    "Extrovert - လူအများကြီးနဲ့ ပျော်ပျော်ပါးပါး စကားပြောရတာ အားပြည့်တယ်",
    "Ambivert - အခြေအနေပေါ်မူတည်ပြီး တစ်ယောက်တည်းရော အဖွဲ့လိုက်ရော အဆင်ပြေတယ်",
    "Selective Introvert - ကိုယ်ခင်တဲ့ သူငယ်ချင်း အနည်းစုနဲ့ပဲ ပျော်ပျော်ပါးပါး နေတတ်တယ်",
    "Social Butterfly - ဘယ်သူနဲ့မဆို ခွေခွေခေါက်ခေါက် ခင်းမင်လွယ်တယ်",
]

# Each behavioral response is the integer index (0–4) of the selected option.
OPTIONS = [0, 1, 2, 3, 4]
QUESTION_COLUMNS = [
    "Q5_Event_Role",
    "Q6_Assembly_Style",
    "Q7_Puzzle_Approach",
    "Q8_Tech_Preference",
    "Q9_Learning_Style",
    "Q10_Cleaning_Style",
    "Q11_Proud_Compliment",
]

ROLE_MAP = {
    "Software_Development": 0,
    "UI_UX_Design": 1,
    "Data_Science_Analytics": 2,
    "Cyber_Security_Networking": 3,
    "Project_Management_Business": 4,
    "AI_ML_Intelligent_Systems": 5,
    "Cloud_Engineering_DevOps": 6,
    "Game_Development": 7,
    "IoT_Hardware_Systems": 8,
}
TARGET_COLUMNS = [f"Role_{role}" for role in ROLE_MAP]

ROLE_WEIGHT_MATRIX = {
    0: {"Software_Development": 3, "Game_Development": 2},
    1: {"UI_UX_Design": 5},
    2: {"Data_Science_Analytics": 3, "AI_ML_Intelligent_Systems": 3},
    3: {"Cyber_Security_Networking": 3, "Cloud_Engineering_DevOps": 3},
    4: {"Project_Management_Business": 3, "IoT_Hardware_Systems": 3},
}


def softmax(values, temperature=0.8):
    """Convert scores to a numerically stable probability distribution."""
    scaled = np.asarray(values, dtype=float) / temperature
    scaled -= np.max(scaled)
    exp_values = np.exp(scaled)
    return exp_values / exp_values.sum()


def weighted_choice(rng, choices, weights):
    probabilities = np.asarray(weights, dtype=float)
    probabilities /= probabilities.sum()
    return rng.choice(choices, p=probabilities)


def balanced_archetypes(total_samples):
    """Balance the five behavioral answer archetypes across generated rows."""
    base_count, remainder = divmod(total_samples, len(OPTIONS))
    return [
        option
        for index, option in enumerate(OPTIONS)
        for _ in range(base_count + int(index < remainder))
    ]


def calculate_target_probabilities(answers, rng):
    """Score answers, apply softmax, and normalize each target row to 1.0."""
    scores = np.zeros(len(ROLE_MAP), dtype=float)
    for answer in answers:
        for role, weight in ROLE_WEIGHT_MATRIX[int(answer)].items():
            scores[ROLE_MAP[role]] += weight

    # Small noise and smoothing provide useful variation while preserving the
    # scoring signal from the answers.
    scores += rng.normal(loc=0.0, scale=0.12, size=len(scores))
    scores = np.clip(scores, 0.0, None)
    probabilities = softmax(scores, temperature=0.8)
    probabilities += rng.uniform(0.0005, 0.004, size=len(probabilities))
    probabilities /= probabilities.sum()

    # Round to CSV precision and correct the final value so row probabilities
    # sum exactly to 1.0 at that precision.
    rounded = np.round(probabilities, 6)
    rounded[-1] = round(float(rounded[-1] + (1.0 - rounded.sum())), 6)
    return rounded


def generate_dataset(total_samples=TOTAL_SAMPLES, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    archetypes = balanced_archetypes(total_samples)
    rng.shuffle(archetypes)

    rows = []
    primary_roles = []
    for primary_option in archetypes:
        # Keep the archetype answer most likely while allowing all five choices.
        answer_weights = np.full(len(OPTIONS), 1.0, dtype=float)
        answer_weights[primary_option] = 7.0
        answer_weights += np.asarray([0.0, 0.25, 0.5, 0.75, 1.0])
        probabilities = answer_weights / answer_weights.sum()
        answers = rng.choice(OPTIONS, size=len(QUESTION_COLUMNS), p=probabilities)

        targets = calculate_target_probabilities(answers, rng)
        primary_role = list(ROLE_MAP)[int(np.argmax(targets))]
        primary_roles.append(primary_role)

        rows.append(
            {
                "Q1_Zodiac": rng.choice(ZODIAC_OPTIONS),
                "Q2_MBTI": rng.choice(MBTI_OPTIONS),
                "Q3_Energy": rng.choice(ENERGY_OPTIONS),
                "Q4_Personality": rng.choice(PERSONALITY_OPTIONS),
                **dict(zip(QUESTION_COLUMNS, answers.tolist())),
                **dict(zip(TARGET_COLUMNS, targets.tolist())),
            }
        )

    return pd.DataFrame(rows), pd.Series(primary_roles, name="Primary_Role")


def main():
    df, primary_roles = generate_dataset()
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
    print("\nDataset preview:")
    print(df.head())
    print("\nGenerated primary role distribution:")
    print(primary_roles.value_counts().sort_index())
    print("\nTop softmax role distribution:")
    top_roles = df[TARGET_COLUMNS].idxmax(axis=1).str.replace("Role_", "", regex=False)
    print(top_roles.value_counts().sort_index())
    print("\nQ1-Q4 categorical answer distribution:")
    print(df[["Q1_Zodiac", "Q2_MBTI", "Q3_Energy", "Q4_Personality"]].stack().value_counts())
    print("\nBehavioral answer distribution:")
    print(df[QUESTION_COLUMNS].stack().value_counts().sort_index())
    print("\nTarget row-sum check:")
    print(df[TARGET_COLUMNS].sum(axis=1).describe())


if __name__ == "__main__":
    main()
