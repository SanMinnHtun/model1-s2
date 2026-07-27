import numpy as np
import streamlit as st


TEMPERATURE = 0.8

ZODIAC_OPTIONS = [
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

MBTI_OPTIONS = [
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

ENERGY_OPTIONS = [
    "Introvert - တစ်ယောက်တည်း အာရုံစိုက်လုပ်ရတာ ပိုအားရှိတယ်",
    "Extrovert - လူတွေနဲ့ ဆွေးနွေးလုပ်ရတာ ပိုအားရှိတယ်",
    "Ambivert - တစ်ယောက်တည်းရော အဖွဲ့လိုက်ရော လုပ်နိုင်တယ်",
]

ROLE_OPTIONS = [
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

QUESTIONS = [
    {
        "prompt": "Q1. သင့် Zodiac sign ကိုရွေးပါ။",
        "options": ZODIAC_OPTIONS,
        "key": "zodiac",
    },
    {
        "prompt": "Q2. သင့် MBTI type ကိုရွေးပါ။ မသိပါက Unknown ကိုရွေးပါ။",
        "options": MBTI_OPTIONS,
        "key": "mbti",
    },
    {
        "prompt": "Q3. သင့် energy source ကိုရွေးပါ။",
        "options": ENERGY_OPTIONS,
        "key": "energy",
    },
    {
        "prompt": "Q4. Project တစ်ခုစလုပ်ရင် သင်ဘယ်အပိုင်းကို အရင်ဆုံးစဉ်းစားမလဲ?",
        "options": [
            "Feature တွေဘယ်လိုအလုပ်လုပ်မလဲဆိုပြီး logic/code flow စဉ်းစားမယ်",
            "User တွေမြင်ရမယ့် screen နဲ့ design အရင်စဉ်းစားမယ်",
            "လိုအပ်တဲ့ data နဲ့ metric တွေကို အရင်သတ်မှတ်မယ်",
            "Risk, access, security issue ရှိမရှိ အရင်စစ်မယ်",
            "Goal, timeline, လူအင်အားနဲ့ task ခွဲဝေမှု စီစဉ်မယ်",
            "Automation သို့မဟုတ် AI နဲ့ ပိုထိရောက်အောင်လုပ်လို့ရမရ စဉ်းစားမယ်",
            "Server, deployment, scaling ဘယ်လိုလုပ်မလဲ စဉ်းစားမယ်",
            "Interaction နဲ့ game-like experience ကို အရင်စဉ်းစားမယ်",
            "Device, sensor, hardware input/output ကို အရင်စဉ်းစားမယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q5. ပစ္စည်း သို့မဟုတ် app တစ်ခုတည်ဆောက်ရမယ်ဆိုရင် သင့်လုပ်ပုံက ဘာလဲ?",
        "options": [
            "Step-by-step code ရေးပြီး prototype တစ်ခု အမြန်တည်ဆောက်မယ်",
            "Sketch/wireframe ဆွဲပြီး user အသုံးပြုပုံကို အရင်စမ်းမယ်",
            "Sample data စုပြီး trend/pattern တွေကို အရင်ကြည့်မယ်",
            "Configuration, password, connection safety ကို အရင်စစ်မယ်",
            "Requirement စုပြီး task list နဲ့ deadline ချမယ်",
            "Model/API တစ်ခုနဲ့ smart feature စမ်းသပ်မယ်",
            "Cloud service သို့မဟုတ် container နဲ့ run ကြည့်မယ်",
            "Playable mechanic တစ်ခုလုပ်ပြီး fun ဖြစ်မဖြစ် စမ်းမယ်",
            "Circuit/sensor/device ချိတ်ပြီး input/output စမ်းမယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q6. အဖွဲ့လိုက်ခရီးစဉ် သို့မဟုတ် event တစ်ခုစီစဉ်ရင် သင်ဘာလုပ်တတ်လဲ?",
        "options": [
            "Route planner/app သေးသေးလေးရေးပြီး schedule တွက်မယ်",
            "လူတိုင်းနားလည်လွယ်တဲ့ map/poster/interface လုပ်မယ်",
            "Budget, distance, time data တွေကို နှိုင်းယှဉ်တွက်မယ်",
            "လုံခြုံရေး၊ emergency contact, network access ကိုစစ်မယ်",
            "လူတွေကိုတာဝန်ခွဲပြီး plan ကိုထိန်းမယ်",
            "Recommendation tool နဲ့ အကောင်းဆုံး route/place ရွေးမယ်",
            "Shared document, cloud folder, automation reminder ထားမယ်",
            "Trip ကို mission/game ပုံစံ activity တွေနဲ့ ပျော်စရာလုပ်မယ်",
            "GPS, device, power bank, gadget setup တွေပြင်မယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q7. ခက်ခဲတဲ့ problem တစ်ခုတွေ့ရင် သင်ဘယ်လိုဖြေရှင်းချင်လဲ?",
        "options": [
            "Problem ကို function/module တွေအဖြစ်ခွဲပြီး logic နဲ့ဖြေရှင်းမယ်",
            "User ဘာကြောင့်ရှုပ်နေလဲကိုကြည့်ပြီး design ကိုပြင်မယ်",
            "Data နဲ့ evidence ကြည့်ပြီး root cause ရှာမယ်",
            "Attack path သို့မဟုတ် weak point ရှိမရှိ စစ်မယ်",
            "Stakeholder တွေနဲ့ညှိပြီး priority သတ်မှတ်မယ်",
            "Pattern learning/modeling နဲ့ prediction လုပ်မယ်",
            "Log, server status, deployment pipeline ကိုစစ်မယ်",
            "Challenge level နဲ့ feedback loop ကိုချိန်ညှိမယ်",
            "Hardware signal, wiring, device behavior ကိုတိုင်းတာမယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q8. ဖိုင်တွေ၊ အခန်းတွေ၊ system တွေရှင်းလင်းတဲ့အခါ သင်ဘာကိုပိုဂရုစိုက်လဲ?",
        "options": [
            "Folder/code structure ကို clean ဖြစ်အောင်စီမယ်",
            "မြင်ရတာရှင်းပြီး သုံးရလွယ်အောင် arrangement လုပ်မယ်",
            "Category, label, spreadsheet နဲ့ data ကိုစုစည်းမယ်",
            "Private file, permission, backup safety ကိုစစ်မယ်",
            "Task owner, process, checklist တွေနဲ့ စနစ်တကျလုပ်မယ်",
            "Repeated cleanup ကို automate လုပ်ဖို့စဉ်းစားမယ်",
            "Sync, storage, versioning, deployment folder ကိုစီမယ်",
            "ပျော်စရာ theme/achievement ပုံစံနဲ့ organize လုပ်မယ်",
            "Cable, device, tool, component တွေကို physical setup နဲ့စီမယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q9. Game သို့မဟုတ် digital activity တစ်ခုမှာ သင်ဘယ်အပိုင်းကို ပိုစိတ်ဝင်စားလဲ?",
        "options": [
            "Game system ရဲ့ code နဲ့ mechanics ဘယ်လိုအလုပ်လုပ်လဲ",
            "Menu, color, animation, user experience ဘယ်လိုကောင်းလဲ",
            "Player behavior data နဲ့ score pattern တွေ",
            "Account safety, cheating prevention, secure connection",
            "Team coordination, release plan, monetization idea",
            "AI opponent, NPC behavior, recommendation system",
            "Online server, matchmaking, uptime, deployment",
            "Level design, gameplay loop, reward system",
            "Controller, VR device, sensor, physical interaction",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q10. အသစ်တစ်ခုသင်ယူတဲ့အခါ သင်ဘယ်နည်းလမ်းကိုပိုနှစ်သက်လဲ?",
        "options": [
            "Code example တွေလိုက်ရေးပြီး build လုပ်ရင်းသင်မယ်",
            "Visual example, layout, design sample ကြည့်ပြီးသင်မယ်",
            "Dataset နဲ့ exercise တွေတွက်ပြီးသင်မယ်",
            "Security lab, network simulation နဲ့စမ်းပြီးသင်မယ်",
            "Case study, business scenario, team exercise နဲ့သင်မယ်",
            "Model demo, AI tool, experiment နဲ့သင်မယ်",
            "Cloud lab, deployment practice, command line နဲ့သင်မယ်",
            "Game project သေးသေးလေးလုပ်ပြီးသင်မယ်",
            "Device kit, circuit, sensor project နဲ့သင်မယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q11. အလုပ်လုပ်ရင်း စိတ်ညစ်စေဆုံးပြဿနာတစ်ခုကို ဘယ်လိုကိုင်တွယ်ချင်လဲ?",
        "options": [
            "Bug ကို trace လိုက်ပြီး code fix လုပ်မယ်",
            "User pain point ကိုရှာပြီး interface ကိုပြင်မယ်",
            "Numbers တွေကြည့်ပြီး ပြဿနာဖြစ်တဲ့ pattern ကိုရှာမယ်",
            "Security hole သို့မဟုတ် network failure ကို isolate လုပ်မယ်",
            "Communication ပြန်ညှိပြီး scope/timeline ကိုပြင်မယ်",
            "Automation နဲ့ repetitive problem ကိုလျှော့မယ်",
            "Infrastructure log ကြည့်ပြီး service ကို stable ဖြစ်အောင်လုပ်မယ်",
            "Difficulty/feedback ကိုပြင်ပြီး experience ကောင်းအောင်လုပ်မယ်",
            "Hardware component တွေစစ်ပြီး signal/device issue ဖြေရှင်းမယ်",
        ],
        "key": "role_choice",
    },
    {
        "prompt": "Q12. လူတွေက သင့်ကို ဘာနဲ့ချီးကျူးရင် အဂုဏ်ယူဆုံးလဲ?",
        "options": [
            "သင်ရေးတဲ့ system က အလုပ်လုပ်တာမြန်ပြီးယုံကြည်ရတယ်",
            "သင်လုပ်တဲ့ design က လှပြီးသုံးရလွယ်တယ်",
            "သင်ရှာတဲ့ insight က decision ချရာမှာအသုံးဝင်တယ်",
            "သင်ကာကွယ်ပေးလို့ system ကပိုလုံခြုံသွားတယ်",
            "သင်စီမံလို့ team အလုပ်ပြီးမြောက်သွားတယ်",
            "သင်လုပ်တဲ့ AI feature က လူအလုပ်ကိုလျှော့ပေးတယ်",
            "သင်တည်ဆောက်တဲ့ cloud system က stable ဖြစ်တယ်",
            "သင်ဖန်တီးတဲ့ game/activity က ပျော်စရာကောင်းတယ်",
            "သင်ချိတ်ဆက်တဲ့ device/hardware က တကယ်အလုပ်လုပ်တယ်",
        ],
        "key": "role_choice",
    },
]


def softmax(logits, temperature=TEMPERATURE):
    scaled_logits = np.asarray(logits, dtype=float) / temperature
    scaled_logits -= np.max(scaled_logits)
    exp_values = np.exp(scaled_logits)
    return exp_values / exp_values.sum()


def compute_role_percentages(role_choices):
    counts = np.zeros(len(ROLE_OPTIONS), dtype=float)

    for choice in role_choices:
        counts[choice - 1] += 1.0

    probabilities = softmax(counts)
    percentages = np.round(probabilities * 100.0, 2)

    rounding_difference = round(100.0 - percentages.sum(), 2)
    percentages[np.argmax(percentages)] += rounding_difference

    return percentages


def format_option(index, text):
    return f"{index}. {text}"


def main():
    st.set_page_config(
        page_title="IT Career Diagnostic",
        page_icon="💻",
        layout="centered",
    )

    st.title("IT Career Diagnostic Test")
    st.markdown(
        "မေးခွန်း ၁၂ ခုကို ဖြေဆိုပြီး သင့်အတွက် သင့်တော်နိုင်သော IT career path "
        "၉ မျိုးကို percentage score ဖြင့် ကြည့်နိုင်ပါတယ်။"
    )

    with st.form("career_diagnostic_form"):
        traits = {}
        role_choices = []

        for idx, question in enumerate(QUESTIONS, start=1):
            st.subheader(question["prompt"])

            labels = [
                format_option(option_idx, option)
                for option_idx, option in enumerate(question["options"], start=1)
            ]

            selected_label = st.radio(
                "ရွေးချယ်ပါ",
                labels,
                key=f"question_{idx}",
                label_visibility="collapsed",
            )
            selected_number = labels.index(selected_label) + 1

            if question["key"] == "role_choice":
                role_choices.append(selected_number)
            else:
                traits[question["key"]] = question["options"][selected_number - 1]

        submitted = st.form_submit_button("Submit")

    if submitted:
        percentages = compute_role_percentages(role_choices)
        ranked_indices = np.argsort(percentages)[::-1]
        top_index = ranked_indices[0]

        st.success(
            f"Top Recommendation: {ROLE_OPTIONS[top_index]} "
            f"({percentages[top_index]:.2f}%)"
        )

        st.markdown("### Compatibility Scores")
        st.caption(
            f"Zodiac: {traits['zodiac']} | MBTI: {traits['mbti']} | "
            f"Energy: {traits['energy']}"
        )

        for index in ranked_indices:
            role = ROLE_OPTIONS[index]
            percentage = float(percentages[index])
            st.write(f"**{role}** - {percentage:.2f}%")
            st.progress(percentage / 100.0)

        st.caption(f"Total: {percentages.sum():.2f}%")


if __name__ == "__main__":
    main()
