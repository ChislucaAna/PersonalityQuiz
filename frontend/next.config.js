/** @type {import('next').NextConfig} */

// The backend base URL. Browser calls go to same-origin /api/* and Next.js
// proxies them here server-side, so we never hit CORS and never need to touch
// the FastAPI app. Override with BACKEND_URL when the backend isn't local.
// Use 127.0.0.1 (not "localhost"): on Windows, Node resolves "localhost" to IPv6
// ::1 first, but uvicorn binds IPv4 127.0.0.1 by default — the mismatch makes the
// proxy fail with ECONNREFUSED (surfaced as a 500). Forcing IPv4 avoids that.
const BACKEND_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

const nextConfig = {
  async rewrites() {
    return [
      {
        // /api/analyze        -> http://localhost:8000/analyze
        // /api/files/abc.png  -> http://localhost:8000/files/abc.png
        source: "/api/:path*",
        destination: `${BACKEND_URL}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
