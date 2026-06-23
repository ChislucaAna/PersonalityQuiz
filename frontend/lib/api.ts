import type { Answer, AnalyzeResponse } from "./types";

// Thrown for the contract's known error states so the UI can react per-case.
export class AnalyzeError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "AnalyzeError";
  }
}

// Rewrites an absolute backend image URL (http://localhost:8000/files/x.png)
// to a same-origin proxied path (/api/files/x.png). Keeps <img> loads and the
// download fetch on our own origin, so no CORS and downloads behave.
export function proxyImageUrl(imageUrl: string): string {
  try {
    const u = new URL(imageUrl);
    return `/api${u.pathname}`; // /files/x.png -> /api/files/x.png
  } catch {
    // already relative, or unexpected — leave it as-is
    return imageUrl;
  }
}

export async function analyze(
  answers: Answer[],
  opts: { includePrompt?: boolean } = {}
): Promise<AnalyzeResponse> {
  const qs = opts.includePrompt ? "?include_prompt=true" : "";

  let res: Response;
  try {
    res = await fetch(`/api/analyze${qs}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers }),
    });
  } catch {
    throw new AnalyzeError(
      0,
      "Couldn't reach the server. Is the backend running on http://localhost:8000?"
    );
  }

  if (!res.ok) {
    // Map the backend's documented error codes to friendly messages.
    let detail = "";
    try {
      const body = await res.json();
      detail = body?.detail ?? "";
    } catch {
      /* non-JSON error body */
    }
    const friendly =
      res.status === 422
        ? "Your answers produced an image prompt that was filtered. Try different choices."
        : res.status === 504
        ? "The portrait took too long to generate. Please try again."
        : res.status === 502
        ? "Image generation failed upstream."
        : `Request failed (${res.status}).`;
    // Surface the backend detail (e.g. the real OpenAI error) so failures are
    // diagnosable instead of hidden behind a generic string.
    const message = detail ? `${friendly} — ${detail}` : friendly;
    throw new AnalyzeError(res.status, message);
  }

  const data = (await res.json()) as AnalyzeResponse;
  // Normalize the image URL to the same-origin proxy path.
  return { ...data, image_url: proxyImageUrl(data.image_url) };
}

// Fetches the (proxied, same-origin) image and triggers a browser download.
export async function downloadImage(imageUrl: string, filename = "portrait.png") {
  const res = await fetch(imageUrl);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
