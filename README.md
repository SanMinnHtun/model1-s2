# IT Career Matching

A small IT career quiz project with a FastAPI backend, a generated training dataset, and a separate command-line recommender. The API exposes quiz questions and accepts frontend answers to return ranked career suggestions.

## Project contents

- `app.py` — FastAPI application entry point; includes the quiz routes and a health check.
- `routes/quiz.py` — question definitions, request validation, and the API's current career scoring logic.
- `generate_it_career_dataset.py` — generates `it_career_matching_dataset.csv`.
- `train_model.py` — trains and evaluates a multi-output Random Forest model, saving `career_model_pipeline.joblib`.
- `interactive_it_career_recommender.py` — standalone terminal quiz/recommender.
- `requirements.txt` — Python libraries and the Uvicorn ASGI server used by the project.
- `render.yaml` — Render Blueprint configuration for deploying the API.

**Model/API note:** the current FastAPI `/quiz/submit` endpoint uses the fixed `ROLE_WEIGHTS` scoring rules in `routes/quiz.py`. It does not load or call `career_model_pipeline.joblib`. `train_model.py` trains a separate model artifact; connecting that artifact to the API would be a further implementation step.

There is no frontend included yet. The frontend section below describes how a web client can use the API.

## Requirements

- Python 3.10 or newer is recommended.
- `pip`
- Uvicorn is included in `requirements.txt` and runs the API server.

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

The API enables CORS for `http://localhost:3000` by default. Set `FRONTEND_URL` to your deployed frontend origin on Render. Multiple origins can be comma-separated. Keep this set to the exact origin(s), including `https://`, without a path.

## Deploy the API to Render

Follow these steps to deploy the FastAPI backend from this repository:

1. **Push the project to GitHub.** Make sure `app.py`, `routes/`, `requirements.txt`, and `render.yaml` are committed and pushed to the repository. The model and CSV files are not required to run the current API.
2. **Sign in to Render.** Open [render.com](https://render.com/) and sign in, or create an account. If the repository is private, authorize Render to access it through your Git provider.
3. **Create a Blueprint.** From the Render dashboard, click **New +** and choose **Blueprint**. Select the GitHub repository that contains this project and the branch you want Render to deploy.
4. **Review the service.** Render reads `render.yaml` and shows a web service named `it-career-matching-api`. Review the settings and click **Apply** (or **Create Blueprint**) to start deployment.
5. **Wait for the first deploy to finish.** Open the service's **Events** or **Logs** page. Wait until the deploy reports success. Render installs dependencies with `pip install -r requirements.txt` and starts the app with `uvicorn app:app --host 0.0.0.0 --port $PORT`.
6. **Copy the service URL.** On the service page, copy its public URL, for example `https://it-career-matching-api.onrender.com`. Open that URL in a browser. The response should be `{"status":"ok"}`. Add `/docs` to the URL to open the interactive API documentation, or `/quiz/questions` to view the quiz questions.
7. **Allow your Vercel site to call the API.** In Render, open the service's **Environment** page and add `FRONTEND_URL` with your Vercel origin, such as `https://your-frontend.vercel.app`. Enter the origin only: no trailing slash and no route path. To allow more than one exact domain, separate the origins with commas. Save the change and wait for Render to redeploy.
8. **Set the API URL in Vercel.** In your Vercel project, add the environment variable for your framework as described in [Connect a Vercel frontend](#connect-a-vercel-frontend). Use the Render public URL from step 6, without a trailing slash, then redeploy the Vercel project.

Render supplies the `PORT` environment variable at runtime, and the Blueprint configures `/` as the health check. You do not need to create a separate start command or manually enter a port when using the Blueprint.

## Connect a Vercel frontend

In the Vercel project, add an environment variable containing the deployed API's base URL (no trailing slash):

| Frontend framework | Environment variable | Example |
| --- | --- | --- |
| Next.js (browser code) | `NEXT_PUBLIC_API_URL` | `https://it-career-matching-api.onrender.com` |
| Vite | `VITE_API_URL` | `https://it-career-matching-api.onrender.com` |
| Create React App | `REACT_APP_API_URL` | `https://it-career-matching-api.onrender.com` |

Redeploy the Vercel project after adding or changing an environment variable. Use the matching variable in the frontend, then make requests to `${API_URL}/quiz/questions` and `${API_URL}/quiz/submit`. For example, in a Vite app:

```js
const API_URL = import.meta.env.VITE_API_URL;
const response = await fetch(`${API_URL}/quiz/questions`);
```

For Next.js browser-side code, use `process.env.NEXT_PUBLIC_API_URL`. The Vercel variable must contain only the API base URL; the Render `FRONTEND_URL` setting must contain the frontend origin. These are separate settings on separate services. If using a custom Vercel domain, add that domain as `FRONTEND_URL` on Render as well.

For local frontend development, set the frontend's API variable to `http://127.0.0.1:8000` and leave the backend's default CORS origin (`http://localhost:3000`) or set `FRONTEND_URL` to the actual local development origin.

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
