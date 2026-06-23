"use client";

export function WelcomeScreen({ onStart }: { onStart: () => void }) {
  return (
    <div className="card center">
      <p className="eyebrow">Portrait Quiz</p>
      <h1>Welcome!</h1>
      <p className="subtitle">
        Answer a few quick questions and we&apos;ll generate a one-of-a-kind
        portrait that captures your vibe — plus a personality label you can share.
      </p>
      <button className="btn btn-block" onClick={onStart}>
        Take Quiz
      </button>
    </div>
  );
}
