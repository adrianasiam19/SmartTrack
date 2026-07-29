'use client';

import { useMemo, useState } from 'react';

export type PhaseQuestion = {
  id: number;
  subject: string;
  question_text: string;
  question_type?: string;
  options?: Record<string, unknown> | null;
  image?: {
    url?: string;
    alt?: string;
    attribution?: string;
  } | null;
  difficulty?: number;
};

type Props = {
  question: PhaseQuestion;
  busy: boolean;
  value: string;
  onChange: (value: string) => void;
};

function getChoices(options: Record<string, unknown> | null | undefined) {
  if (!options) return [] as { key: string; text: string }[];
  const nested = options.choices;
  const source =
    nested && typeof nested === 'object' && !Array.isArray(nested)
      ? (nested as Record<string, unknown>)
      : options;
  return Object.entries(source)
    .filter(([key, val]) => {
      if (
        [
          'choices',
          'image',
          'template',
          'answers',
          'hints',
          'accepted',
          'left',
          'right',
          'correct_matches',
          'items',
          'correct_order',
          'instruction',
          'legend',
        ].includes(key)
      ) {
        return false;
      }
      return typeof val === 'string' || typeof val === 'number';
    })
    .map(([key, text]) => ({ key, text: String(text) }));
}

function EducationalImage({
  image,
  options,
}: {
  image?: PhaseQuestion['image'];
  options?: Record<string, unknown> | null;
}) {
  const fromOptions =
    options && typeof options.image === 'object' && options.image
      ? (options.image as { url?: string; alt?: string; attribution?: string })
      : null;
  const img = image?.url ? image : fromOptions;
  const legend =
    options && typeof options.legend === 'object' && options.legend
      ? (options.legend as { title?: string; hint?: string })
      : null;
  const [failed, setFailed] = useState(false);
  if (!img?.url || failed) return null;
  return (
    <figure className="mt-4 mb-2 overflow-hidden rounded-xl border border-[#E2E8F0] bg-white">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={img.url}
        alt={img.alt || 'Educational diagram'}
        referrerPolicy="no-referrer"
        loading="eager"
        onError={() => setFailed(true)}
        className="w-full max-h-80 object-contain bg-[#F8FAFC]"
      />
      {legend?.hint ? (
        <div className="border-t border-[#E2E8F0] bg-[#F8FAFC] px-3 py-2 text-left">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-[#64748B]">
            {legend.title || 'What to look for'}
          </p>
          <p className="mt-1 text-xs text-[#475569] leading-relaxed">{legend.hint}</p>
        </div>
      ) : null}
    </figure>
  );
}

function typeLabel(qtype: string) {
  const map: Record<string, string> = {
    mcq: 'Multiple choice',
    true_false: 'True or false',
    fill_blank: 'Fill in the blank',
    short_answer: 'Short answer',
    matching: 'Matching',
    ordering: 'Ordering',
    scenario: 'Scenario',
    image_mcq: 'Image question',
    diagram_label: 'Diagram',
  };
  return map[qtype] || 'Challenge';
}

export default function PhaseQuestionRenderer({
  question,
  busy,
  value,
  onChange,
}: Props) {
  const qtype = (question.question_type || 'mcq').toLowerCase();
  const options = (question.options || {}) as Record<string, unknown>;

  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-wide text-[#7C3AED]">
        {typeLabel(qtype)}
      </p>
      <EducationalImage image={question.image} options={options} />
      <h1 className="mt-3 text-xl font-semibold text-[#0F172A]">
        {qtype === 'fill_blank' && options.template
          ? 'Fill in the blanks'
          : question.question_text}
      </h1>
      {qtype === 'fill_blank' &&
      options.template &&
      question.question_text &&
      !String(options.template).includes(question.question_text) ? (
        <p className="mt-2 text-sm text-[#475569] leading-relaxed">
          {question.question_text}
        </p>
      ) : null}

      {qtype === 'true_false' ? (
        <TrueFalseUI busy={busy} value={value} onChange={onChange} />
      ) : qtype === 'fill_blank' ? (
        <FillBlankUI
          busy={busy}
          options={options}
          value={value}
          onChange={onChange}
        />
      ) : qtype === 'short_answer' ? (
        <ShortAnswerUI busy={busy} value={value} onChange={onChange} />
      ) : qtype === 'matching' ? (
        <MatchingUI
          busy={busy}
          options={options}
          value={value}
          onChange={onChange}
        />
      ) : qtype === 'ordering' ? (
        <OrderingUI
          questionId={question.id}
          busy={busy}
          options={options}
          value={value}
          onChange={onChange}
        />
      ) : (
        <McqUI
          busy={busy}
          choices={getChoices(options)}
          value={value}
          onChange={onChange}
        />
      )}
    </div>
  );
}

function McqUI({
  busy,
  choices,
  value,
  onChange,
}: {
  busy: boolean;
  choices: { key: string; text: string }[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="mt-6 space-y-3">
      {choices.map((opt) => (
        <button
          key={opt.key}
          type="button"
          disabled={busy}
          onClick={() => onChange(opt.key)}
          className={`w-full text-left rounded-xl border px-4 py-3 transition ${
            value === opt.key
              ? 'border-[#2563EB] bg-[#EFF6FF]'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <span className="font-medium mr-2">{opt.key}.</span>
          {opt.text}
        </button>
      ))}
    </div>
  );
}

function TrueFalseUI({
  busy,
  value,
  onChange,
}: {
  busy: boolean;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="mt-6 grid grid-cols-2 gap-3">
      {(['true', 'false'] as const).map((opt) => (
        <button
          key={opt}
          type="button"
          disabled={busy}
          onClick={() => onChange(opt)}
          className={`rounded-xl border px-4 py-4 font-semibold capitalize transition ${
            value === opt
              ? 'border-[#2563EB] bg-[#EFF6FF] text-[#1E3A8A]'
              : 'border-slate-200 bg-white text-[#0F172A] hover:border-slate-300'
          }`}
        >
          {opt}
        </button>
      ))}
    </div>
  );
}

function ShortAnswerUI({
  busy,
  value,
  onChange,
}: {
  busy: boolean;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="mt-6">
      <textarea
        value={value}
        disabled={busy}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        placeholder="Type your answer…"
        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-[#0F172A] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/20"
      />
    </div>
  );
}

function FillBlankUI({
  busy,
  options,
  value,
  onChange,
}: {
  busy: boolean;
  options: Record<string, unknown>;
  value: string;
  onChange: (v: string) => void;
}) {
  const template = String(options.template || '');
  const answerCount = Array.isArray(options.answers)
    ? options.answers.length
    : Math.max(1, (template.match(/___/g) || []).length || 1);
  const parts = template ? template.split('___') : [''];
  const values = value ? value.split('|') : Array(answerCount).fill('');
  while (values.length < answerCount) values.push('');

  const update = (idx: number, text: string) => {
    const next = [...values];
    next[idx] = text;
    onChange(next.join('|'));
  };

  if (!template) {
    return (
      <ShortAnswerUI busy={busy} value={value} onChange={onChange} />
    );
  }

  return (
    <div className="mt-6 rounded-xl border border-slate-200 bg-white px-4 py-4 text-[#0F172A] leading-relaxed">
      {parts.map((part, idx) => (
        <span key={idx}>
          {part}
          {idx < answerCount ? (
            <input
              type="text"
              disabled={busy}
              value={values[idx] || ''}
              onChange={(e) => update(idx, e.target.value)}
              className="mx-1 inline-block w-28 border-b-2 border-[#2563EB]/40 bg-transparent px-1 text-center font-medium outline-none focus:border-[#2563EB]"
              placeholder="…"
            />
          ) : null}
        </span>
      ))}
    </div>
  );
}

function MatchingUI({
  busy,
  options,
  value,
  onChange,
}: {
  busy: boolean;
  options: Record<string, unknown>;
  value: string;
  onChange: (v: string) => void;
}) {
  const left = Array.isArray(options.left) ? (options.left as string[]) : [];
  const right = Array.isArray(options.right) ? (options.right as string[]) : [];
  const instruction = String(options.instruction || 'Match each item on the left.');
  const [activeLeft, setActiveLeft] = useState<number | null>(null);

  const map = useMemo(() => {
    const out: Record<number, number> = {};
    if (!value) return out;
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) {
        parsed.forEach((v, i) => {
          out[i] = Number(v);
        });
        return out;
      }
      if (parsed && typeof parsed === 'object') {
        Object.entries(parsed).forEach(([k, v]) => {
          out[Number(k)] = Number(v);
        });
        return out;
      }
    } catch {
      value.split(',').forEach((part) => {
        const [a, b] = part.split(':');
        if (a != null && b != null) out[Number(a)] = Number(b);
      });
    }
    return out;
  }, [value]);

  const setPair = (leftIdx: number, rightIdx: number) => {
    const next = { ...map };
    Object.keys(next).forEach((k) => {
      if (next[Number(k)] === rightIdx) delete next[Number(k)];
    });
    next[leftIdx] = rightIdx;
    onChange(JSON.stringify(next));
    setActiveLeft(null);
  };

  return (
    <div className="mt-6 space-y-3">
      <p className="text-sm text-[#64748B]">{instruction}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          {left.map((item, idx) => (
            <button
              key={`l-${idx}`}
              type="button"
              disabled={busy}
              onClick={() => setActiveLeft(idx)}
              className={`w-full text-left rounded-xl border px-3 py-2.5 text-sm ${
                activeLeft === idx
                  ? 'border-[#2563EB] bg-[#EFF6FF]'
                  : map[idx] != null
                    ? 'border-emerald-200 bg-emerald-50'
                    : 'border-slate-200 bg-white'
              }`}
            >
              {item}
              {map[idx] != null ? (
                <span className="mt-1 block text-[11px] text-[#64748B]">
                  → {right[map[idx]]}
                </span>
              ) : null}
            </button>
          ))}
        </div>
        <div className="space-y-2">
          {right.map((item, idx) => (
            <button
              key={`r-${idx}`}
              type="button"
              disabled={busy || activeLeft == null}
              onClick={() => activeLeft != null && setPair(activeLeft, idx)}
              className="w-full text-left rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm hover:border-[#2563EB] disabled:opacity-50"
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function OrderingUI({
  questionId,
  busy,
  options,
  value,
  onChange,
}: {
  questionId: number;
  busy: boolean;
  options: Record<string, unknown>;
  value: string;
  onChange: (v: string) => void;
}) {
  const sourceItems = useMemo(() => {
    const items = Array.isArray(options.items)
      ? (options.items as string[])
      : Array.isArray(options.correct_order)
        ? (options.correct_order as string[])
        : [];
    // Stable shuffle per question id for display
    const arr = [...items];
    let seed = questionId * 2654435761;
    for (let i = arr.length - 1; i > 0; i -= 1) {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      const j = seed % (i + 1);
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }, [options, questionId]);

  const ordered = useMemo(() => {
    if (!value) return [] as string[];
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) return parsed.map(String);
    } catch {
      return value.split('|').filter(Boolean);
    }
    return [];
  }, [value]);

  const remaining = sourceItems.filter((item) => !ordered.includes(item));

  const add = (item: string) => {
    if (busy) return;
    onChange(JSON.stringify([...ordered, item]));
  };
  const removeLast = () => {
    if (busy || !ordered.length) return;
    onChange(JSON.stringify(ordered.slice(0, -1)));
  };
  const reset = () => onChange('');

  return (
    <div className="mt-6 space-y-4">
      <p className="text-sm text-[#64748B]">
        Tap items in the correct order.
      </p>
      <div className="min-h-[3rem] rounded-xl border border-dashed border-[#BFDBFE] bg-[#EFF6FF]/50 px-3 py-3 space-y-2">
        {ordered.length === 0 ? (
          <p className="text-xs text-[#94A3B8]">Your sequence appears here…</p>
        ) : (
          ordered.map((item, idx) => (
            <div
              key={`${item}-${idx}`}
              className="rounded-lg border border-[#BFDBFE] bg-white px-3 py-2 text-sm text-[#0F172A]"
            >
              <span className="mr-2 font-semibold text-[#2563EB]">{idx + 1}.</span>
              {item}
            </div>
          ))
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {remaining.map((item) => (
          <button
            key={item}
            type="button"
            disabled={busy}
            onClick={() => add(item)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm hover:border-[#2563EB]"
          >
            {item}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={busy || !ordered.length}
          onClick={removeLast}
          className="text-xs font-medium text-[#64748B] hover:text-[#0F172A]"
        >
          Undo
        </button>
        <button
          type="button"
          disabled={busy || !ordered.length}
          onClick={reset}
          className="text-xs font-medium text-[#64748B] hover:text-[#0F172A]"
        >
          Reset
        </button>
      </div>
    </div>
  );
}

export function answerReady(question: PhaseQuestion, value: string): boolean {
  const qtype = (question.question_type || 'mcq').toLowerCase();
  const v = value.trim();
  if (!v) return false;
  if (qtype === 'matching') {
    try {
      const parsed = JSON.parse(v);
      const left = Array.isArray(question.options?.left)
        ? (question.options!.left as string[])
        : [];
      if (Array.isArray(parsed)) return parsed.length === left.length;
      if (parsed && typeof parsed === 'object') {
        return Object.keys(parsed).length === left.length;
      }
    } catch {
      return v.includes(':');
    }
  }
  if (qtype === 'ordering') {
    try {
      const parsed = JSON.parse(v);
      const items = Array.isArray(question.options?.items)
        ? (question.options!.items as string[])
        : [];
      return Array.isArray(parsed) && parsed.length === items.length;
    } catch {
      return false;
    }
  }
  if (qtype === 'fill_blank') {
    const answers = Array.isArray(question.options?.answers)
      ? (question.options!.answers as string[])
      : [];
    const parts = v.split('|');
    return answers.length
      ? parts.length === answers.length && parts.every((p) => p.trim())
      : Boolean(v);
  }
  return Boolean(v);
}
