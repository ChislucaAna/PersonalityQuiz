# Portrait Service (FastAPI backend)

Synchronous backend for the quiz-to-portrait app. Matches the architecture diagram:
the Next.js frontend POSTs answers to `/analyze`; the backend scores traits, derives
a visual style, builds a prompt, generates an image, stores it, and returns
`{image_url, traits, label}` in one response.

## Pipeline (the diagram's boxes)
1. **Trait scorer** (`analysis/trait_scorer.py`) — answers -> trait scores + interests
2. **Style config** (`analysis/style_config.py`) — traits -> visual style (palette, art style, ...)
3. **Prompt builder** (`analysis/prompt_builder.py`) — style -> strict image prompt
4. **Labeler** (`analysis/labeler.py`) — traits -> shareable archetype label
5. Generation (`generation/`) -> Storage (`storage/`) -> response

## Run locally (no API key needed)
```bash
pip install -r requirements.txt
cp .env.example .env          # defaults to the fake generator + local disk
uvicorn app.main:app --reload
python smoke_test.py          # end-to-end check
```

## API
- `POST /analyze` -> `{image_url, traits, label}`  (add `?include_prompt=true` to see the prompt)
- `GET  /files/{name}` -> the generated image (local storage only)
- `GET  /health`

Request body:
```json
{ "answers": [ { "question_id": "q_hobby", "answer_id": "stargazing" } ] }
```

## Switching to OpenAI
Set in `.env`:
```
PORTRAIT_GENERATOR=openai
PORTRAIT_OPENAI_API_KEY=sk-...
PORTRAIT_OPENAI_MODEL=gpt-image-1-mini
```
Notes baked into `generation/openai_client.py`: GPT-Image has **no seed** (reproducibility
comes from the prompt), it returns **base64** (we decode + store, then serve a URL), and the
**moderation filter** can refuse a prompt (surfaced as HTTP 422). Org verification on the
OpenAI account is required before GPT-Image models work.

## Plugging in the real quiz
Topics/questions are not hard-coded. Edit the `SCORING` dict in `analysis/trait_scorer.py`
(map each `(question_id, answer_id)` to trait deltas + interest tags) and extend the
`INTERESTS` catalog in `vocabulary.py`. No other code changes needed.
