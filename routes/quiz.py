"""Career matching quiz API routes."""

from typing import Annotated, Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field, field_validator

router = APIRouter(prefix="/quiz", tags=["quiz"])

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

QUESTIONS = [
    {"prompt": "Q1. သင့် Zodiac sign ကို ရွေးပါ။", "options": ZODIAC_OPTIONS, "key": "zodiac"},
    {"prompt": "Q2. သင့် MBTI group ကို ရွေးပါ။ မသိပါက Skip ကို ရွေးပါ။", "options": MBTI_OPTIONS, "key": "mbti"},
    {"prompt": "Q3. သင့် စွမ်းအင် ရရှိရာ Energy Source ကို ရွေးပါ။", "options": ENERGY_OPTIONS, "key": "energy"},
    {"prompt": "Q4. သင်ဟာ ဘယ်လို လူမျိုး ဖြစ်မလဲ?", "options": PERSONALITY_OPTIONS, "key": "personality_type"},
    {
        "prompt": "Q5. သူငယ်ချင်းတွေနဲ့ Event သို့မဟုတ် ပွဲတစ်ခု စီစဉ်ရင် သင် ဘာလုပ်ချင်လဲ?",
        "options": [
            "ပွဲမှာ ဆော့မယ့် ပျော်စရာ ဂိမ်းတွေနဲ့ စည်းမျဉ်းတွေကို စဉ်းစားမယ်",
            "ပိတ်ကား၊ ဖိတ်စာနဲ့ ပွဲတစ်ခုလုံး ကြည့်ရတာ လှပသွားအောင် ပြင်ဆင်မယ်",
            "လူဘယ်နှယောက်လာမလဲ၊ ဘာတွေကြိုက်တတ်လဲ စာရင်းဇယားကြည့်ပြီး ခန်းမှန်းမယ်",
            "ဘယ်သူမှ အန္တရာယ်မရှိအောင်နဲ့ ပစ္စည်းတွေ မပျောက်အောင် စောင့်ရှောက်မယ်",
            "လူတွေကို တာဝန်ခွဲပေးမယ် သို့မဟုတ် စပီကာ၊ မီးဆိုင်းနဲ့ ပစ္စည်းတွေ တပ်ဆင်မယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q6. Lego သို့မဟုတ် စက္ကူအရုပ် တစ်ခုခု စဆောက်တော့မယ်ဆိုရင် သင့် စတိုင်က ဘာလဲ?",
        "options": [
            "အရုပ် ရုပ်လုံးပေါ်သွားအောင် အစိတ်အပိုင်းတွေကို အမြန် ဆက်ကြည့်မယ်",
            "အရောင်စုံလှပပြီး ကြည့်ရတာ သပ်ရပ်သွားအောင် ပုံစံထုတ်မယ်",
            "လမ်းညွှန်စာအုပ်ထဲက အချက်အလက်တွေ၊ အရေအတွက်တွေကို အရင် ရေတွက်မယ်",
            "အရုပ် ပြုတ်ထွက်မသွားအောင်နဲ့ ခိုင်ခိုင်မာမာ ရှိမရှိ အရင် စစ်ဆေးမယ်",
            "အဆင့်လိုက် တည်ဆောက်ဖို့ အစီအစဉ်ဆွဲမယ် သို့မဟုတ် မီးသီး/စက်ယန္တရားတပ်မယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q7. ကစားနည်း သို့မဟုတ် ပဟေဠိတစ်ခုမှာ အဖြေရှာရရင် သင် ဘာလုပ်တတ်လဲ?",
        "options": [
            "အဆင့်ဆင့် စဉ်းစားပြီး မှန်ကန်တဲ့ နည်းလမ်းတွေ့တဲ့အထိ စမ်းကြည့်မယ်",
            "လူတွေ ကစားရတာ လွယ်ကူ အဆင်ပြေအောင် ကစားနည်း ပုံစံကို ပြင်ပေးမယ်",
            "အရင်က ဖြစ်လေ့ရှိတဲ့ ပုံစံတွေနဲ့ အထောက်အထားတွေကို ကြည့်ပြီး အဖြေရှာမယ်",
            "ဂိမ်းထဲမှာ မသမာတာ၊ လှည့်ကွက်ရှိမရှိနဲ့ မကင်းမသန့်တာတွေကို လိုက်ရှာမယ်",
            "သူငယ်ချင်းတွေကို ကူညီဖို့ လမ်းညွှန်ပေးမယ် သို့မဟုတ် ကစားပွဲ ပစ္စည်းတွေ ပြင်မယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q8. ဖုန်း (သို့) ကွန်ပျူတာ သုံးတဲ့အခါ သင် ဘာကို ပိုသဘောကျလဲ?",
        "options": [
            "ခလုတ်တစ်ခု နှိပ်လိုက်တာနဲ့ နောက်ကွယ်မှာ မြန်မြန်ဆန်ဆန် အလုပ်လုပ်သွားတာ",
            "Screen ပေါ်မှာ မြင်ရတဲ့ အရောင် သန့်သန့်ပြန့်ပြန့်လေးတွေနဲ့ လှပတဲ့ ဒီဇိုင်း",
            "ငါ ဘာကြည့်ချင်လဲဆိုတာ ဖုန်းက ကြိုသိပြီး ဖော်ပြပေးတာ",
            "ကိုယ့် Password တွေနဲ့ ဓာတ်ပုံတွေကို သူများ ခိုးမကြည့်နိုင်အောင် ကာကွယ်ထားတာ",
            "ဖုန်းနဲ့ ချိတ်ဆက်ပြီး အဝေးကနေ ခလုတ်နှိပ် စေခိုင်းလို့ရတဲ့ စက်ပစ္စည်းတွေ",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q9. ဝါသနာအသစ် တစ်ခုခုကို စတင် လေ့လာတဲ့အခါ သင် ဘယ်လို လေ့လာချင်လဲ?",
        "options": [
            "နမူနာတွေကို ကြည့်ပြီး ကိုယ်တိုင် လက်တည့်စမ်း ဖန်တီးကြည့်မယ်",
            "လှပတဲ့ ပုံစံတွေကို ကြည့်ပြီး ကိုယ်တိုင် ပုံဆွဲ/ဒီဇိုင်းဆွဲ လေ့ကျင့်မယ်",
            "ဉာဏ်စမ်း ပဟေဠိ မေးခွန်းတွေနဲ့ ဂိမ်းကစားရင်း လေ့လာမယ်",
            "စိန်ခေါ်မှုတွေ၊ လျှို့ဝှက်ချက်တွေကို ဖောက်ထွက်တဲ့ နည်းလမ်းတွေနဲ့ လေ့လာမယ်",
            "သူငယ်ချင်းတွေနဲ့ ပူးပေါင်းလုပ်ဆောင်မယ် သို့မဟုတ် ပစ္စည်းကိရိယာတွေကို တပ်ဆင်ရင်း လေ့လာမယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q10. အခန်း သို့မဟုတ် စာအုပ်စင် ရှင်းလင်းရေး လုပ်တဲ့အခါ သင် ဘာကို ပိုဂရုစိုက်လဲ?",
        "options": [
            "ပစ္စည်းတစ်ခုချင်းစီကို အစဉ်လိုက် စနစ်တကျ နေရာချမယ်",
            "ကြည့်လိုက်တာနဲ့ ရှင်းလင်းပြီး သန့်ရှင်းလှပနေအောင် ပြင်ဆင်မယ်",
            "အမျိုးအစားတူတာတွေကို အုပ်စုခွဲပြီး စာရင်းဇယားနဲ့ မှတ်ထားမယ်",
            "အရေးကြီး ပစ္စည်းတွေ ပျောက်မသွားအောင် သော့ခတ် လုံခြုံအောင်ထားမယ်",
            "ဘယ်သူ ဘာရှင်းရမလဲ တာဝန်ခွဲပေးမယ် သို့မဟုတ် မီးကြိုး/စက်ပစ္စည်းတွေကို စနစ်တကျ သိမ်းမယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q11. သူငယ်ချင်းတွေက သင့်ကို ဘာနဲ့ ချီးကျူးရင် အပျော်ဆုံးလဲ?",
        "options": [
            "\"မင်း လုပ်ပေးတာ လုံးဝ အလုပ်ဖြစ်တယ်၊ ပျော်ဖို့လည်း အရမ်းကောင်းတယ်!\"",
            "\"မင်း ဖန်တီးလိုက်တာ လုံးဝ သန့်ရှင်းလှပပြီး သုံးရတာ အရမ်း အဆင်ပြေတယ်!\"",
            "\"မင်း အဖြေရှာပေးတာ အရမ်း တိကျတာပဲ၊ အရမ်း တော်တယ်!\"",
            "\"မင်း ရှိနေလို့ ငါတို့ အားလုံး စိတ်အေးရတယ်၊ စိတ်ဓာတ် ခိုင်မာတယ်!\"",
            "\"မင်း စီစဉ်ပေးတာ အရမ်း စနစ်ကျတယ် / မင်း ချိတ်ဆက်လိုက်တဲ့ ပစ္စည်း အလုပ်လုပ်သွားပြီ!\"",
        ],
        "key": "role_choice",
    },
]

ROLE_WEIGHTS: dict[int, dict[str, int]] = {
    0: {"Software Development": 3, "Game Development": 2},
    1: {"UI/UX Design": 5},
    2: {"Data Science & Analytics": 3, "AI/ML & Intelligent Systems": 3},
    3: {"Cyber Security & Networking": 3, "Cloud Engineering & DevOps": 3},
    4: {"Project Management & Business": 3, "IoT & Hardware Systems": 3},
}

TARGET_ROLES = [
    "Software Development",
    "UI/UX Design",
    "Data Science & Analytics",
    "Cyber Security & Networking",
    "Project Management & Business",
    "AI/ML & Intelligent Systems",
    "Cloud Engineering & DevOps",
    "Game Development",
    "IoT & Hardware Systems",
]


class QuizSubmission(BaseModel):
    """Validated answers to the career matching quiz."""

    model_config = ConfigDict(extra="forbid")

    zodiac: str = Field(..., min_length=1)
    mbti: str = Field(..., min_length=1)
    energy: str = Field(..., min_length=1)
    personality_type: str = Field(..., min_length=1)
    role_choices: Annotated[list[Annotated[int, Field(strict=True, ge=0, le=4)]], Field(min_length=7, max_length=7)]

    @field_validator("zodiac")
    @classmethod
    def validate_zodiac(cls, value: str) -> str:
        if value not in ZODIAC_OPTIONS:
            raise ValueError("Select a valid zodiac option")
        return value

    @field_validator("mbti")
    @classmethod
    def validate_mbti(cls, value: str) -> str:
        if value not in MBTI_OPTIONS:
            raise ValueError("Select a valid MBTI option")
        return value

    @field_validator("energy")
    @classmethod
    def validate_energy(cls, value: str) -> str:
        if value not in ENERGY_OPTIONS:
            raise ValueError("Select a valid energy option")
        return value

    @field_validator("personality_type")
    @classmethod
    def validate_personality_type(cls, value: str) -> str:
        if value not in PERSONALITY_OPTIONS:
            raise ValueError("Select a valid personality option")
        return value


class RoleMatch(BaseModel):
    role: str
    percentage: float


class QuizResult(BaseModel):
    primary_recommendation: RoleMatch
    runner_up: RoleMatch
    all_role_percentages: list[RoleMatch]


@router.get("/questions")
def get_questions() -> list[dict[str, Any]]:
    """Return quiz questions in display order."""
    return QUESTIONS


@router.post("/submit", response_model=QuizResult)
def submit_quiz(submission: QuizSubmission) -> QuizResult:
    """Score the seven behavioral answers and return ranked career matches."""
    scores = {role: 0 for role in TARGET_ROLES}
    for choice in submission.role_choices:
        for role, weight in ROLE_WEIGHTS[choice].items():
            scores[role] += weight

    ranked = [
        RoleMatch(role=role, percentage=round((scores[role] / 35.0) * 100, 1))
        for role in TARGET_ROLES
    ]
    ranked.sort(key=lambda match: match.percentage, reverse=True)
    return QuizResult(
        primary_recommendation=ranked[0],
        runner_up=ranked[1],
        all_role_percentages=ranked,
    )
