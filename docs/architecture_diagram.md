```mermaid
flowchart TD
  User(["User / Browser"])

  subgraph Vercel ["Vercel — Next.js frontend"]
    direction TB
    QuizUI["Quiz UI\n/app/quiz/page.tsx"]
    ResultUI["Result UI\n/app/result/page.tsx"]
    APIRoute["API proxy route\n/app/api/generate/route.ts"]
    QuizUI -->|"answers[]"| APIRoute
    APIRoute -->|"image_url + traits"| ResultUI
  end

  subgraph Render ["Render / Railway — FastAPI backend"]
    direction TB
    Endpoint["POST /analyze\nFastAPI endpoint"]
    Pydantic["Pydantic validator\nAnswersPayload"]
    Scorer["Trait scorer\nanswers → OCEAN scores"]
    StyleMap["Style mapper\ntraits → art_style config"]
    PromptBuilder["Prompt builder\ntraits + style → string"]
    OpenAIClient["OpenAI Python client\nopenai.images.generate()"]
    Endpoint --> Pydantic --> Scorer --> StyleMap --> PromptBuilder --> OpenAIClient
  end

  subgraph OpenAI ["OpenAI — External API"]
    ImageGen["gpt-image-1\nimages/generations"]
  end
```
  User -->|"HTTP"| QuizUI
  APIRoute -->|"POST /analyze"| Endpoint
  OpenAIClient -->|"images API"| ImageGen
  ImageGen -->|"base64 PNG"| OpenAIClient
  Endpoint -->|"200 OK · image_url + traits"| APIRoute
  ResultUI -->|"renders image"| User
