# Portrait Quiz — Frontend

Next.js (App Router, TypeScript) frontend for the portrait service. Implements the
four-screen flow: **Welcome → Questions → Result** (image + label + download).

## Run it

1. Start the backend first (from the `portrait-service` folder):

   ```
   uvicorn app.main:app --reload
   ```

   It should be reachable at http://localhost:8000 (check http://localhost:8000/health).

2. In this `frontend` folder:

   ```
   npm install
   npm run dev
   ```

3. Open http://localhost:3000 and take the quiz.

That's it — the fake image generator is on by default, so no API key is needed to
see the full flow working.

## How it talks to the backend

The browser calls **same-origin** `/api/*`, and Next.js proxies it to the backend
(`next.config.js` → `rewrites`). This avoids CORS entirely, so the FastAPI app
needs no changes. To point at a non-local backend:

```
BACKEND_URL=https://your-backend npm run dev
```

## Where things live

- `data/quiz.ts` — the sample questions. **Every `answer_id` matches a key in the
  backend `SCORING` dict**, so the full pipeline works today. Update this file and
  the backend `SCORING`/`INTERESTS` together when the real quiz is defined.
- `lib/api.ts` — typed client for `POST /analyze`, maps the 422/502/504 error
  codes to friendly messages, and proxies/​downloads the image.
- `lib/types.ts` — mirrors the backend response shapes.
- `app/page.tsx` — the flow state machine (welcome → quiz → loading → result/error).
- `components/` — one component per screen.

## Error handling

The result of `POST /analyze` is mapped per the backend contract:

- **422** — the image model's moderation filter rejected the prompt.
- **504** — generation timed out.
- **502** — generation failed upstream.
- **network** — backend unreachable (is it running on :8000?).
