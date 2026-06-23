"use client";

import { useState } from "react";
import type { AnalyzeResponse } from "@/lib/types";
import { downloadImage } from "@/lib/api";

const AXIS_LABELS: Record<string, string> = {
  energy: "Energy",
  warmth: "Warmth",
  openness: "Openness",
  intensity: "Intensity",
  nature_affinity: "Nature affinity",
};

export function ResultScreen({
  result,
  onRestart,
}: {
  result: AnalyzeResponse;
  onRestart: () => void;
}) {
  const [downloading, setDownloading] = useState(false);
  const { image_url, label, traits } = result;

  async function handleDownload() {
    setDownloading(true);
    try {
      await downloadImage(image_url, `portrait-${label.name.replace(/\s+/g, "-").toLowerCase()}.png`);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div className="card center">
      <p className="eyebrow">This is you, inside</p>

      <div className="portrait-frame">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={image_url} alt={`Portrait representing ${label.name}`} />
      </div>

      <h2 className="label-name">{label.name}</h2>
      <p className="label-blurb">{label.blurb}</p>

      <button
        className="btn btn-block"
        onClick={handleDownload}
        disabled={downloading}
      >
        {downloading ? "Preparing…" : "Download image"}
      </button>

      <div className="traits">
        {Object.entries(traits.scores).map(([axis, value]) => (
          <div className="trait" key={axis}>
            <span>
              {AXIS_LABELS[axis] ?? axis} — {Math.round(value * 100)}%
            </span>
            <div className="trait-bar">
              <span style={{ width: `${Math.round(value * 100)}%` }} />
            </div>
          </div>
        ))}
      </div>

      {traits.interests.length > 0 && (
        <div className="tags">
          {traits.interests.map((t) => (
            <span className="tag" key={t}>
              {t.replace(/_/g, " ")}
            </span>
          ))}
        </div>
      )}

      <div style={{ marginTop: 22 }}>
        <button className="btn btn-secondary btn-block" onClick={onRestart}>
          Retake quiz
        </button>
      </div>
    </div>
  );
}
