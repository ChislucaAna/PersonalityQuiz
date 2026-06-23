"use client";

import { useState } from "react";
import type { QuizOption } from "@/data/quiz";

export function QuestionScreen({
  questionKey,
  prompt,
  options,
  progressLabel,
  initialAnswerId,
  isFinalStep,
  onNext,
}: {
  questionKey: string; // remounts state when the step changes
  prompt: string;
  options: QuizOption[];
  progressLabel: string;
  initialAnswerId?: string;
  isFinalStep: boolean;
  onNext: (answerId: string) => void;
}) {
  const [selected, setSelected] = useState<string | undefined>(initialAnswerId);

  return (
    <div className="card" key={questionKey}>
      <p className="progress">{progressLabel}</p>
      <p className="question">{prompt}</p>

      <div className="options">
        {options.map((opt) => {
          const isSelected = selected === opt.answer_id;
          return (
            <button
              key={opt.answer_id}
              className={`option${isSelected ? " selected" : ""}`}
              onClick={() => setSelected(opt.answer_id)}
              aria-pressed={isSelected}
            >
              <span className="dot" />
              <span>{opt.text}</span>
            </button>
          );
        })}
      </div>

      <button
        className="btn btn-block"
        disabled={!selected}
        onClick={() => selected && onNext(selected)}
      >
        {isFinalStep ? "See my portrait" : "Next"}
      </button>
    </div>
  );
}
