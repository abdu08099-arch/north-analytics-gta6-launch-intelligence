import type { NextConfig } from "next";

// Static export: `npm run build` writes plain HTML/JS to out/ (Decision 0001).
// For GitHub Pages under /<repo>, set NEXT_PUBLIC_BASE_PATH=/<repo> at build time.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath,
  images: { unoptimized: true },
  poweredByHeader: false,
};

export default nextConfig;
