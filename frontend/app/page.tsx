"use client";

import { useState } from "react";
import { QUIZ } from "@/data/quiz";
import { analyze, AnalyzeError } from "@/lib/api";
import type { Answer, AnalyzeResponse } from "@/lib/types";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { QuestionScreen } from "@/components/QuestionScreen";
import { LoadingScreen } from "@/components/LoadingScreen";
import { ResultScreen } from "@/components/ResultScreen";

// A follow-up paired with the main it belongs to (so we can label/key it).
type FollowStep = { mainId: string; followIndex: number };

type Phase =
  | { name: "welcome" }
  | { name: "baseline"; index: number } // asking main question `index`
  | { name: "followups"; queue: FollowStep[]; pos: number }
  | { name: "loading" }
  | { name: "result"; result: AnalyzeResponse }
  | { name: "error"; message: string };

export default function Home() {
  const [phase, setPhase] = useState<Phase>({ name: "welcome" });
  // answers keyed by question_id (e.g. "1" -> "yes", "1a" -> "c")
  const [answers, setAnswers] = useState<Record<string, string>>({});

  function start() {
    setAnswers({});
    setPhase({ name: "baseline", index: 0 });
  }

  // Build the request payload in deterministic quiz order (each main, then its
  // shown follow-ups), so motif ordering in the prompt is stable.
  function buildPayload(all: Record<string, string>): Answer[] {
    const out: Answer[] = [];
    for (const q of QUIZ) {
      if (all[q.id] === undefined) continue;
      out.push({ question_id: q.id, answer_id: all[q.id] });
      if (all[q.id] === "yes") {
        for (const f of q.followUps) {
          if (all[f.id] !== undefined) {
            out.push({ question_id: f.id, answer_id: all[f.id] });
          }
        }
      }
    }
    return out;
  }

  // After all baselines: queue the follow-ups of every main answered "yes".
  function buildFollowQueue(all: Record<string, string>): FollowStep[] {
    const queue: FollowStep[] = [];
    for (const q of QUIZ) {
      if (all[q.id] === "yes") {
        q.followUps.forEach((_f, i) => queue.push({ mainId: q.id, followIndex: i }));
      }
    }
    return queue;
  }

  async function submit(all: Record<string, string>) {
    setPhase({ name: "loading" });
    try {
      const result = await analyze(buildPayload(all));
      setPhase({ name: "result", result });
    } catch (err) {
      const message =
        err instanceof AnalyzeError
          ? err.message
          : "Something went wrong. Please try again.";
      setPhase({ name: "error", message });
    }
  }

  function handleNext(answerId: string) {
    if (phase.name === "baseline") {
      const main = QUIZ[phase.index];
      const next = { ...answers, [main.id]: answerId };
      setAnswers(next);

      if (phase.index < QUIZ.length - 1) {
        setPhase({ name: "baseline", index: phase.index + 1 });
      } else {
        // baselines done — move to follow-ups, or straight to generation
        const queue = buildFollowQueue(next);
        if (queue.length > 0) {
          setPhase({ name: "followups", queue, pos: 0 });
        } else {
          void submit(next);
        }
      }
      return;
    }

    if (phase.name === "followups") {
      const step = phase.queue[phase.pos];
      const main = QUIZ.find((q) => q.id === step.mainId)!;
      const followId = main.followUps[step.followIndex].id;
      const next = { ...answers, [followId]: answerId };
      setAnswers(next);

      if (phase.pos < phase.queue.length - 1) {
        setPhase({ name: "followups", queue: phase.queue, pos: phase.pos + 1 });
      } else {
        void submit(next);
      }
    }
  }

  switch (phase.name) {
    case "welcome":
      return <WelcomeScreen onStart={start} />;

    case "baseline": {
      const main = QUIZ[phase.index];
      return (
        <QuestionScreen
          questionKey={main.id}
          prompt={main.text}
          options={main.options}
          progressLabel={`Question ${phase.index + 1} of ${QUIZ.length}`}
          initialAnswerId={answers[main.id]}
          isFinalStep={false} // never final: follow-ups may follow
          onNext={handleNext}
        />
      );
    }

    case "followups": {
      const step = phase.queue[phase.pos];
      const main = QUIZ.find((q) => q.id === step.mainId)!;
      const follow = main.followUps[step.followIndex];
      return (
        <QuestionScreen
          questionKey={follow.id}
          prompt={follow.text}
          options={follow.options}
          progressLabel={`Follow-up ${phase.pos + 1} of ${phase.queue.length}`}
          initialAnswerId={answers[follow.id]}
          isFinalStep={phase.pos === phase.queue.length - 1}
          onNext={handleNext}
        />
      );
    }

    case "loading":
      return <LoadingScreen />;

    case "result":
      return <ResultScreen result={phase.result} onRestart={start} />;

    case "error":
      return (
        <div className="card center">
          <p className="eyebrow">Something went wrong</p>
          <div className="error-box">{phase.message}</div>
          <button className="btn btn-block" onClick={start}>
            Try again
          </button>
        </div>
      );
  }
}
