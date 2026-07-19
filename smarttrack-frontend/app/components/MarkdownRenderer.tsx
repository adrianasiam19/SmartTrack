'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Components } from 'react-markdown';

interface MarkdownRendererProps {
  content: string;
  /** Use compact spacing for chat bubbles */
  compact?: boolean;
  /** Class name to apply to the wrapper */
  className?: string;
}

/**
 * MarkdownRenderer — Renders markdown content as beautifully styled HTML.
 *
 * Designed with textbook-like readability:
 *   - Generous line-height (1.8) for maximum legibility
 *   - Wide spacing between sections
 *   - Large, clear headings
 *   - Comfortable padding in tables and code blocks
 */
export default function MarkdownRenderer({
  content,
  compact = false,
  className = '',
}: MarkdownRendererProps) {
  const spacing = compact
    ? {
        p: 'text-sm mb-2 leading-[1.7]',
        h1: 'text-base font-bold mb-2 mt-3',
        h2: 'text-[15px] font-bold mb-1.5 mt-3',
        h3: 'text-sm font-bold mb-1 mt-2',
        h4: 'text-xs font-bold mb-1 mt-1.5',
        ul: 'mb-2 space-y-0.5',
        ol: 'mb-2 space-y-0.5',
        pre: 'mb-2',
        blockquote: 'mb-2',
        table: 'mb-2',
        hr: 'my-3',
      }
    : {
        p: 'text-[15px] mb-4 leading-[1.85]',
        h1: 'text-[22px] font-bold mb-4 mt-8',
        h2: 'text-[18px] font-bold mb-3 mt-7',
        h3: 'text-[16px] font-bold mb-2.5 mt-6',
        h4: 'text-[14px] font-bold mb-2 mt-4',
        ul: 'mb-4 space-y-1.5',
        ol: 'mb-4 space-y-1.5',
        pre: 'mb-4',
        blockquote: 'mb-4',
        table: 'mb-4',
        hr: 'my-6',
      };

  const components: Components = {
    // ── Headings ──────────────────────────────────────────────────────────
    h1: ({ children }) => (
      <h1 className={`${spacing.h1} text-[#1E293B] pb-3 border-b-2 border-gray-200 first:mt-0`}>
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className={`${spacing.h2} text-[#1E293B] flex items-center gap-3`}>
        <span className="w-1 h-6 bg-[#2563EB] rounded-full inline-block flex-shrink-0" />
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className={`${spacing.h3} text-[#1E293B]`}>
        {children}
      </h3>
    ),
    h4: ({ children }) => (
      <h4 className={`${spacing.h4} text-[#475569] uppercase tracking-wider`}>
        {children}
      </h4>
    ),

    // ── Paragraph ─────────────────────────────────────────────────────────
    p: ({ children }) => (
      <p className={`${spacing.p} text-[#475569]`}>
        {children}
      </p>
    ),

    // ── Bold / Strong ─────────────────────────────────────────────────────
    strong: ({ children }) => (
      <strong className="font-bold text-[#1E293B]">{children}</strong>
    ),

    // ── Emphasis / Italic ─────────────────────────────────────────────────
    em: ({ children }) => (
      <em className="italic text-[#475569]">{children}</em>
    ),

    // ── Links ─────────────────────────────────────────────────────────────
    a: ({ href, children }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-[#2563EB] underline decoration-[#93C5FD] underline-offset-2 hover:text-[#1D4ED8] hover:decoration-[#2563EB] transition-colors"
      >
        {children}
      </a>
    ),

    // ── Unordered List ────────────────────────────────────────────────────
    ul: ({ children }) => (
      <ul className={`${spacing.ul} pl-6`}>
        {children}
      </ul>
    ),
    li: ({ children }) => (
      <li className="text-[#475569] leading-[1.7] list-disc marker:text-[#2563EB] marker:text-base">
        {children}
      </li>
    ),

    // ── Ordered List ──────────────────────────────────────────────────────
    ol: ({ children }) => (
      <ol className={`${spacing.ol} pl-6 list-decimal`}>
        {children}
      </ol>
    ),

    // ── Inline Code ───────────────────────────────────────────────────────
    code: ({ className: cName, children }) => {
      if (cName) {
        return (
          <code className={`text-sm font-mono ${cName}`}>{children}</code>
        );
      }
      return (
        <code className="px-2 py-0.5 bg-[#EEF2FF] text-[#4F46E5] text-sm font-mono rounded-md border border-[#C7D2FE]">
          {children}
        </code>
      );
    },

    // ── Code Blocks ───────────────────────────────────────────────────────
    pre: ({ children }) => (
      <pre className={`${spacing.pre} bg-[#1E293B] text-[#E2E8F0] rounded-xl p-5 overflow-x-auto text-sm font-mono leading-relaxed border border-gray-700 shadow-inner`}>
        {children}
      </pre>
    ),

    // ── Blockquotes ───────────────────────────────────────────────────────
    blockquote: ({ children }) => (
      <blockquote className={`${spacing.blockquote} border-l-[3px] border-[#2563EB] bg-[#EFF6FF] rounded-r-xl py-3 px-5 text-[#475569] italic leading-[1.7]`}>
        {children}
      </blockquote>
    ),

    // ── Tables ────────────────────────────────────────────────────────────
    table: ({ children }) => (
      <div className={`${spacing.table} overflow-x-auto rounded-xl border border-gray-200 shadow-sm`}>
        <table className="w-full text-sm border-collapse">
          {children}
        </table>
      </div>
    ),
    thead: ({ children }) => (
      <thead className="bg-gradient-to-r from-[#EEF2FF] to-[#E0E7FF]">
        {children}
      </thead>
    ),
    tbody: ({ children }) => (
      <tbody className="divide-y divide-gray-100">{children}</tbody>
    ),
    tr: ({ children }) => (
      <tr className="even:bg-[#F8FAFC] hover:bg-[#EEF2FF]/50 transition-colors duration-150">
        {children}
      </tr>
    ),
    th: ({ children }) => (
      <th className="px-5 py-3 text-left text-xs font-bold text-[#1E293B] uppercase tracking-wider border-b-2 border-gray-200">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="px-5 py-3.5 text-[#475569] leading-[1.7] border-b border-gray-100 last-of-type:border-b-0">
        {children}
      </td>
    ),

    // ── Horizontal Rule ───────────────────────────────────────────────────
    hr: () => (
      <div className={`${spacing.hr} border-t border-gray-200`} />
    ),
  };

  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content || ''}
      </ReactMarkdown>
    </div>
  );
}
