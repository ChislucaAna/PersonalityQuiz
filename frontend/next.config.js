/** @type {import('next').NextConfig} */

// The backend base URL. Browser calls go to same-origin /api/* and Next.js
// proxies them here server-side, so we never hit CORS and never need to touch
// the FastAPI app. Override with BACKEND_URL when the backend isn't local.
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

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
