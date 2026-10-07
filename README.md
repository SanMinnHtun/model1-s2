# IT Career Matching

A small IT career quiz project with a FastAPI backend, a generated training dataset, and a separate command-line recommender. The API exposes quiz questions and accepts frontend answers to return ranked career suggestions.

## Project contents

- `app.py` — FastAPI application entry point; includes the quiz routes and a health check.
- `routes/quiz.py` — question definitions, request validation, and the API's current career scoring logic.
- `generate_it_career_dataset.py` — generates `it_career_matching_dataset.csv`.
- `train_model.py` — trains and evaluates a multi-output Random Forest model, saving `career_model_pipeline.joblib`.
- `interactive_it_career_recommender.py` — standalone terminal quiz/recommender.
- `requirements.txt` — Python libraries used by the project.

**Model/API note:** the current FastAPI `/quiz/submit` endpoint uses the fixed `ROLE_WEIGHTS` scoring rules in `routes/quiz.py`. It does not load or call `career_model_pipeline.joblib`. `train_model.py` trains a separate model artifact; connecting that artifact to the API would be a further implementation step.

There is no frontend included yet. The frontend section below describes how a web client can use the API.

## Requirements

- Python 3.10 or newer is recommended.
- `pip`
- `uvicorn` to run the API server. It is not currently listed in `requirements.txt`, so install it separately as shown below.

## Run the API locally

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Install project dependencies and the ASGI server:

```bash
python -m pip install -r requirements.txt
python -m pip install uvicorn
```

Start the development server:

```bash
python -m uvicorn app:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

- Health check: `GET http://127.0.0.1:8000/`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## API usage

### Get quiz questions

```http
GET /quiz/questions
```

The response is an array of question objects. Each object has a `prompt`, an `options` array, and a `key`. The first four questions collect profile choices; the remaining seven provide the behavioral answers used for scoring. Use the returned option strings directly in the submission so the frontend stays in sync with the backend.

### Submit answers

```http
POST /quiz/submit
Content-Type: application/json
```

The request body has four profile strings and seven integer behavioral choices. Each integer is the selected option's zero-based index (`0` through `4`) for questions Q5–Q11.

```json
{
  "zodiac": "Other / Skip",
  "mbti": "Unknown / Skip",
  "energy": "Flexible - အခြေအနေပေါ်မူတည်ပြီး တစ်ယောက်တည်းရော အဖွဲ့လိုက်ရော ရတယ်",
  "personality_type": "Ambivert - အခြေအနေပေါ်မူတည်ပြီး တစ်ယောက်တည်းရော အဖွဲ့လိုက်ရော အဆင်ပြေတယ်",
  "role_choices": [0, 1, 2, 3, 4, 0, 1]
}
```

The four profile fields must exactly match a string in the corresponding option list returned by `GET /quiz/questions`. `role_choices` must contain exactly seven integers, each from 0 to 4. Unknown fields are rejected.

A successful response has this shape:

```json
{
  "primary_recommendation": {
    "role": "UI/UX Design",
    "percentage": 71.4
  },
  "runner_up": {
    "role": "Software Development",
    "percentage": 17.1
  },
  "all_role_percentages": [
    { "role": "UI/UX Design", "percentage": 71.4 },
    { "role": "Software Development", "percentage": 17.1 }
  ]
}
```

The example abbreviates `all_role_percentages`; the actual response includes all nine roles. The current values are weighted scores divided by the maximum per-role score, not a probability distribution, so percentages across roles are not expected to sum to 100.

Invalid request data returns HTTP `422` with validation details. For example, a wrong number of `role_choices`, an index outside 0–4, an unrecognized profile string, or an extra field will fail validation.

## Frontend integration

A browser frontend can fetch the questions, render each prompt and its options, save the selected answers, and submit them to the API. The frontend should map the four profile answers to their named fields and the seven behavioral selections to `role_choices` in Q5–Q11 order.

Example using browser JavaScript:

```js
const API_URL = "http://127.0.0.1:8000";

const questionsResponse = await fetch(`${API_URL}/quiz/questions`);
if (!questionsResponse.ok) throw new Error("Could not load quiz questions");
const questions = await questionsResponse.json();

// Fill these values from the user's selections in the rendered form.
const submission = {
  zodiac: "Other / Skip",
  mbti: "Unknown / Skip",
  energy: questions[2].options[2],
  personality_type: questions[3].options[2],
  // One zero-based option index for each behavioral question Q5 through Q11.
  role_choices: [0, 1, 2, 3, 4, 0, 1],
};

const resultResponse = await fetch(`${API_URL}/quiz/submit`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(submission),
});

if (!resultResponse.ok) {
  const details = await resultResponse.json();
  throw new Error(`Quiz submission failed (${resultResponse.status}): ${JSON.stringify(details)}`);
}

const result = await resultResponse.json();
console.log(result.primary_recommendation, result.runner_up);
```

For a real form, build the payload from the user's selections rather than keeping the example values. For each behavioral question, submit the selected option's index within that question's `options` array, preserving the Q5–Q11 order.

If the frontend runs on a different origin or port from the API, the browser may block requests until the backend allows that frontend origin through CORS. The current app does not configure CORS. For production, serve both behind a configured same origin or add a CORS policy restricted to the deployed frontend origin.

## Generate data and train the standalone model

These commands are optional for running the current API. Run them from the project root:

```bash
python generate_it_career_dataset.py
python train_model.py
```

The first command writes `it_career_matching_dataset.csv`; the second reads it, prints evaluation metrics, performs a sanity check, and writes `career_model_pipeline.joblib`. The API currently does not consume this artifact.

## Notes

- The dataset generator creates synthetic examples; model evaluation on that dataset does not establish real-world career recommendation accuracy.
- The API and the standalone terminal recommender are separate interfaces with different quiz definitions. The API contract is defined by `routes/quiz.py`.
