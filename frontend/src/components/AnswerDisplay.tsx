"use client";

import type { Citation } from "@/lib/types";

interface AnswerDisplayProps {
  answer: string;
  citations: Citation[];
  confidence: string;
  foundRelevant: boolean;
  onCitationClick: (index: number) => void;
}

function renderAnswerWithCitations(
  answer: string,
  onCitationClick: (index: number) => void
) {
  const parts = answer.split(/(\[\d+\])/g);
  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/);
    if (match) {
      const num = parseInt(match[1], 10);
      return (
        <button
          key={i}
          className="citation-marker mx-0.5"
          onClick={() => onCitationClick(num)}
        >
          {num}
        </button>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

const confidenceStyles: Record<string, { label: string; className: string }> = {
  high: { label: "High confidence", className: "bg-green-100 text-green-700" },
  medium: { label: "Medium confidence", className: "bg-yellow-100 text-yellow-700" },
  low: { label: "Low confidence", className: "bg-orange-100 text-orange-700" },
  none: { label: "No matching information", className: "bg-slate-100 text-slate-600" },
};

export default function AnswerDisplay({
  answer,
  citations,
  confidence,
  foundRelevant,
  onCitationClick,
}: AnswerDisplayProps) {
  const conf = confidenceStyles[confidence] || confidenceStyles.none;

  return (
    <div className="atlas-card animate-fade-in p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-atlas-navy">Answer</h3>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${conf.className}`}>
          {conf.label}
        </span>
      </div>
      <div
        className={`prose-atlas text-[15px] leading-relaxed ${
          foundRelevant ? "text-slate-800" : "text-slate-600 italic"
        }`}
      >
        {foundRelevant
          ? renderAnswerWithCitations(answer, onCitationClick)
          : answer}
      </div>
      {foundRelevant && citations.length > 0 && (
        <p className="mt-4 text-xs text-slate-400">
          Based on {citations.length} source document
          {citations.length !== 1 ? "s" : ""}. Click citation numbers to view sources.
        </p>
      )}
    </div>
  );
}
