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
    concept?: string;
    requires_labels?: boolean;
    labels?: unknown;
  } | null;
  difficulty?: number;
};

type Props = {
  question: PhaseQuestion;
  busy: boolean;
  value: string;
  onChange: (value: string) => void;
};

function normalizeType(raw?: string | null) {
  const q = (raw || 'mcq').toLowerCase().replace(/[\s-]+/g, '_');
  const aliases: Record<string, string> = {
    truefalse: 'true_false',
    tf: 'true_false',
    fillblank: 'fill_blank',
    fill_in_the_blank: 'fill_blank',
    shortanswer: 'short_answer',
    short_response: 'short_answer',
    match: 'matching',
    order: 'ordering',
    sequence: 'ordering',
    rank: 'ordering',
    diagram: 'diagram_label',
    image: 'image_mcq',
  };
  return aliases[q] || q;
}

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
          'left_items',
          'right_items',
          'correct_matches',
          'items',
          'correct_order',
          'order',
          'steps',
          'sequence',
          'instruction',
          'legend',
        ].includes(key)
      ) {
        return false;
      }
      return typeof val === 'string' || typeof val === 'number';
    })
    .map(([key, text]) => ({ key, text: String(text) }))
    .sort((a, b) => a.key.localeCompare(b.key));
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  const out: string[] = [];
  const seen = new Set<string>();
  for (const item of value) {
    let text = '';
    if (typeof item === 'string' || typeof item === 'number') {
      text = String(item).trim();
    } else if (item && typeof item === 'object') {
      const obj = item as Record<string, unknown>;
      text = String(obj.text || obj.label || obj.value || obj.item || '').trim();
    }
    if (!text) continue;
    const key = text.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(text);
  }
  return out;
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
      ? (options.image as { url?: string; alt?: string; concept?: string })
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
  const qtype = normalizeType(question.question_type);
  const options = (question.options || {}) as Record<string, unknown>;
  const choices = getChoices(options);

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
          choices={choices}
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
  if (choices.length < 2) {
    return (
      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        This question is missing answer choices. Tap Skip / Next if available, or
        restart the level to load a fresh question.
      </div>
    );
  }
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
        onInput={(e) => onChange((e.target as HTMLTextAreaElement).value)}
        rows={3}
        placeholder="Type your answer…"
        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-[#0F172A] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#2563EB]/20 disabled:opacity-60"
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
  const rawTemplate = String(options.template || '');
  // Normalize any run of 3+ underscores to a single blank token
  const template = rawTemplate.replace(/_{3,}/g, '___');
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
    return <ShortAnswerUI busy={busy} value={value} onChange={onChange} />;
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
  const left = asStringList(options.left ?? options.left_items);
  const right = asStringList(options.right ?? options.right_items);
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

  if (left.length < 2 || right.length < 2) {
    return (
      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        This matching question is incomplete. Restart the level to load a fresh question.
      </div>
    );
  }

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
  // Canonical order = correct sequence (backend stores both as correct order)
  const canonical = useMemo(() => {
    const items = asStringList(
      options.items ?? options.correct_order ?? options.order ?? options.steps ?? options.sequence,
    );
    return items;
  }, [options]);

  // Stable shuffled presentation keyed by question id
  const displayPool = useMemo(() => {
    const arr = canonical.map((text, index) => ({ id: index, text }));
    let seed = questionId * 2654435761;
    for (let i = arr.length - 1; i > 0; i -= 1) {
      seed = (seed * 1664525 + 1013904223) >>> 0;
      const j = seed % (i + 1);
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }, [canonical, questionId]);

  const orderedIds = useMemo(() => {
    if (!value) return [] as number[];
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) {
        // Prefer id-based payload; fall back to matching text against canonical
        if (parsed.every((x) => typeof x === 'number')) {
          return parsed.map(Number);
        }
        const texts = parsed.map(String);
        return texts
          .map((t) => canonical.findIndex((c) => c === t))
          .filter((i) => i >= 0);
      }
    } catch {
      return value
        .split('|')
        .map((t) => canonical.findIndex((c) => c === t))
        .filter((i) => i >= 0);
    }
    return [];
  }, [value, canonical]);

  const remaining = displayPool.filter((item) => !orderedIds.includes(item.id));

  const emit = (ids: number[]) => {
    // Persist the ordered TEXT sequence — matches backend grading
    onChange(JSON.stringify(ids.map((id) => canonical[id])));
  };

  const add = (id: number) => {
    if (busy || orderedIds.includes(id)) return;
    emit([...orderedIds, id]);
  };
  const removeLast = () => {
    if (busy || !orderedIds.length) return;
    emit(orderedIds.slice(0, -1));
  };
  const reset = () => onChange('');

  if (canonical.length < 3) {
    return (
      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        This ordering question is missing its items. Restart the level to load a fresh
        question.
      </div>
    );
  }

  return (
    <div className="mt-6 space-y-4">
      <p className="text-sm text-[#64748B]">Tap items in the correct order.</p>
      <div className="min-h-[3rem] rounded-xl border border-dashed border-[#BFDBFE] bg-[#EFF6FF]/50 px-3 py-3 space-y-2">
        {orderedIds.length === 0 ? (
          <p className="text-xs text-[#94A3B8]">Your sequence appears here…</p>
        ) : (
          orderedIds.map((id, idx) => (
            <div
              key={`ord-${id}`}
              className="rounded-lg border border-[#BFDBFE] bg-white px-3 py-2 text-sm text-[#0F172A]"
            >
              <span className="mr-2 font-semibold text-[#2563EB]">{idx + 1}.</span>
              {canonical[id]}
            </div>
          ))
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {remaining.map((item) => (
          <button
            key={`pool-${item.id}`}
            type="button"
            disabled={busy}
            onClick={() => add(item.id)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm hover:border-[#2563EB]"
          >
            {item.text}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          disabled={busy || !orderedIds.length}
          onClick={removeLast}
          className="text-xs font-medium text-[#64748B] hover:text-[#0F172A]"
        >
          Undo
        </button>
        <button
          type="button"
          disabled={busy || !orderedIds.length}
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
  const qtype = normalizeType(question.question_type);
  const v = value.trim();
  if (!v) return false;
  const options = (question.options || {}) as Record<string, unknown>;

  if (qtype === 'matching') {
    try {
      const parsed = JSON.parse(v);
      const left = asStringList(options.left ?? options.left_items);
      if (left.length < 2) return false;
      if (Array.isArray(parsed)) return parsed.length === left.length;
      if (parsed && typeof parsed === 'object') {
        return Object.keys(parsed).length === left.length;
      }
    } catch {
      return v.includes(':');
    }
    return false;
  }

  if (qtype === 'ordering') {
    const items = asStringList(
      options.items ?? options.correct_order ?? options.order ?? options.steps,
    );
    if (items.length < 3) return false;
    try {
      const parsed = JSON.parse(v);
      return Array.isArray(parsed) && parsed.length === items.length;
    } catch {
      return false;
    }
  }

  if (qtype === 'fill_blank') {
    const template = String(options.template || '').replace(/_{3,}/g, '___');
    const answers = Array.isArray(options.answers) ? (options.answers as string[]) : [];
    // UI falls back to a single textarea when template is missing
    if (!template) return Boolean(v);
    const expected =
      answers.length || Math.max(1, (template.match(/___/g) || []).length || 1);
    const parts = v.split('|');
    return parts.length >= expected && parts.slice(0, expected).every((p) => p.trim());
  }

  if (qtype === 'true_false') {
    return v.toLowerCase() === 'true' || v.toLowerCase() === 'false';
  }

  if (
    qtype === 'mcq' ||
    qtype === 'scenario' ||
    qtype === 'image_mcq' ||
    qtype === 'diagram_label'
  ) {
    const choices = getChoices(options);
    if (choices.length < 2) return false;
    return choices.some((c) => c.key === v || c.text === v);
  }

  // short_answer and anything else: any non-empty trimmed text
  return Boolean(v);
}
