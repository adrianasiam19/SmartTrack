'use client';

import { motion } from 'framer-motion';
import type { MathVizConfig } from '../lib/learningContent';

interface MathVisualizerProps {
  config: MathVizConfig;
  animated?: boolean;
}

export default function MathVisualizer({
  config,
  animated = true,
}: MathVisualizerProps) {
  const animProps = animated
    ? { initial: { opacity: 0, scale: 0.95 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.4 } }
    : {};

  switch (config.type) {
    case 'number-line':
      return <NumberLine config={config} {...animProps} />;
    case 'bar-chart':
      return <BarChart config={config} {...animProps} />;
    case 'coordinate-plane':
      return <CoordinatePlane config={config} {...animProps} />;
    case 'venn-diagram':
      return <VennDiagram config={config} {...animProps} />;
    case 'tree-diagram':
      return <TreeDiagram config={config} {...animProps} />;
    case 'punnett-square':
      return <PunnettSquare config={config} {...animProps} />;
    case 'fraction-pie':
      return <FractionPie config={config} {...animProps} />;
    default:
      return null;
  }
}

// ── Number Line ──

function NumberLine({
  config,
  ...animProps
}: MathVisualizerProps & Record<string, unknown>) {
  const { data = [], range = { min: -5, max: 5 }, width = 400, height = 80 } = config;
  const padding = 30;
  const innerW = width - padding * 2;
  const rangeSpan = range.max - range.min;
  const xScale = (val: number) => padding + ((val - range.min) / rangeSpan) * innerW;
  const midY = height / 2;
  const tickMarks: number[] = [];
  for (let i = Math.ceil(range.min); i <= Math.floor(range.max); i++) {
    tickMarks.push(i);
  }

  return (
    <motion.svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      className="my-4"
      {...animProps}
    >
      {/* Line */}
      <line
        x1={padding}
        y1={midY}
        x2={width - padding}
        y2={midY}
        stroke="rgba(163,230,53,0.5)"
        strokeWidth="2"
      />
      {/* Arrows */}
      <polygon
        points={`${width - padding},${midY} ${width - padding - 8},${midY - 5} ${width - padding - 8},${midY + 5}`}
        fill="rgba(163,230,53,0.5)"
      />
      <polygon
        points={`${padding},${midY} ${padding + 8},${midY - 5} ${padding + 8},${midY + 5}`}
        fill="rgba(163,230,53,0.5)"
      />
      {/* Tick marks */}
      {tickMarks.map((val) => (
        <g key={val}>
          <line
            x1={xScale(val)}
            y1={midY - 6}
            x2={xScale(val)}
            y2={midY + 6}
            stroke="rgba(255,255,255,0.3)"
            strokeWidth="1.5"
          />
          <text
            x={xScale(val)}
            y={midY + 20}
            textAnchor="middle"
            fill="rgba(255,255,255,0.5)"
            fontSize="12"
          >
            {val}
          </text>
        </g>
      ))}
      {/* Zero label */}
      <line
        x1={xScale(0)}
        y1={midY - 8}
        x2={xScale(0)}
        y2={midY + 8}
        stroke="rgba(163,230,53,0.8)"
        strokeWidth="2"
      />
      {/* Data points */}
      {data.map((val: number, idx: number) => (
        <motion.circle
          key={idx}
          cx={xScale(val)}
          cy={midY}
          r="6"
          fill="rgba(163,230,53,0.9)"
          stroke="#84cc16"
          strokeWidth="2"
          initial={{ r: 0 }}
          animate={{ r: 6 }}
          transition={{ delay: 0.3 + idx * 0.15 }}
        />
      ))}
    </motion.svg>
  );
}

// ── Bar Chart ──

function BarChart({
  config,
  ...animProps
}: MathVisualizerProps & Record<string, unknown>) {
  const { data = [3, 7, 5, 8, 4, 6], labels = ['A', 'B', 'C', 'D', 'E', 'F'], width = 360, height = 200 } = config;
  const padding = { top: 10, bottom: 30, left: 10, right: 10 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;
  const maxVal = Math.max(...data, 1);
  const barW = innerW / data.length * 0.7;
  const gap = innerW / data.length * 0.3;

  return (
    <motion.svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      className="my-4"
      {...animProps}
    >
      {/* Bars */}
      {data.map((val: number, idx: number) => {
        const barH = (val / maxVal) * innerH;
        const x = padding.left + idx * (barW + gap) + gap / 2;
        const y = padding.top + innerH - barH;
        return (
          <g key={idx}>
            <motion.rect
              x={x}
              y={height - padding.bottom}
              width={barW}
              height={0}
              fill={`url(#barGrad${idx % 4})`}
              rx="4"
              initial={false}
              animate={{ y, height: barH }}
              transition={{ delay: 0.1 * idx, duration: 0.5, ease: 'easeOut' }}
            />
            <text
              x={x + barW / 2}
              y={y - 4}
              textAnchor="middle"
              fill="rgba(163,230,53,0.9)"
              fontSize="11"
              fontWeight="bold"
            >
              {val}
            </text>
            <text
              x={x + barW / 2}
              y={height - 6}
              textAnchor="middle"
              fill="rgba(255,255,255,0.5)"
              fontSize="10"
            >
              {labels[idx] || ''}
            </text>
          </g>
        );
      })}
      <defs>
        <linearGradient id="barGrad0" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#a3e635" />
          <stop offset="100%" stopColor="#84cc16" />
        </linearGradient>
        <linearGradient id="barGrad1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#34d399" />
          <stop offset="100%" stopColor="#10b981" />
        </linearGradient>
        <linearGradient id="barGrad2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="100%" stopColor="#3b82f6" />
        </linearGradient>
        <linearGradient id="barGrad3" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f87171" />
          <stop offset="100%" stopColor="#ef4444" />
        </linearGradient>
      </defs>
    </motion.svg>
  );
}

// ── Coordinate Plane ──

function CoordinatePlane({
  config,
  ...animProps
}: MathVisualizerProps & Record<string, unknown>) {
  const { data = [], range = { min: -5, max: 5 }, width = 300, height = 300 } = config;
  const padding = 30;
  const innerW = width - padding * 2;
  const innerH = height - padding * 2;
  const rangeSpan = range.max - range.min;
  const xScale = (val: number) => padding + ((val - range.min) / rangeSpan) * innerW;
  const yScale = (val: number) => padding + ((range.max - val) / rangeSpan) * innerH;

  const ticks: number[] = [];
  for (let i = Math.ceil(range.min); i <= Math.floor(range.max); i++) {
    ticks.push(i);
  }

  return (
    <motion.svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      className="my-4"
      {...animProps}
    >
      {/* Grid */}
      {ticks.map((val) => (
        <g key={val}>
          <line
            x1={padding}
            y1={yScale(val)}
            x2={width - padding}
            y2={yScale(val)}
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="1"
          />
          <line
            x1={xScale(val)}
            y1={padding}
            x2={xScale(val)}
            y2={height - padding}
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="1"
          />
        </g>
      ))}
      {/* Axes */}
      <line
        x1={xScale(0)}
        y1={padding}
        x2={xScale(0)}
        y2={height - padding}
        stroke="rgba(163,230,53,0.5)"
        strokeWidth="1.5"
      />
      <line
        x1={padding}
        y1={yScale(0)}
        x2={width - padding}
        y2={yScale(0)}
        stroke="rgba(163,230,53,0.5)"
        strokeWidth="1.5"
      />
      {/* Axis labels */}
      <text x={width / 2} y={height - 4} textAnchor="middle" fill="rgba(255,255,255,0.3)" fontSize="11">x</text>
      <text x={10} y={height / 2 + 4} textAnchor="middle" fill="rgba(255,255,255,0.3)" fontSize="11">y</text>
      {/* Tick labels */}
      {ticks.map((val) => (
        <g key={val}>
          <text x={xScale(val)} y={yScale(0) + 14} textAnchor="middle" fill="rgba(255,255,255,0.35)" fontSize="9">
            {val === 0 ? '' : val}
          </text>
          <text x={xScale(0) - 8} y={yScale(val) + 3} textAnchor="end" fill="rgba(255,255,255,0.35)" fontSize="9">
            {val === 0 ? '' : val}
          </text>
        </g>
      ))}
      {/* Origin */}
      <text x={xScale(0) - 8} y={yScale(0) + 14} textAnchor="end" fill="rgba(255,255,255,0.5)" fontSize="9">0</text>
      {/* Data points */}
      {data.map((val: number, idx: number) => {
        if (idx % 2 !== 0) return null;
        const x = data[idx];
        const y = data[idx + 1];
        if (x === undefined || y === undefined) return null;
        return (
          <g key={idx}>
            <motion.circle
              cx={xScale(x)}
              cy={yScale(y)}
              r="5"
              fill="rgba(251,191,36,0.8)"
              stroke="#f59e0b"
              strokeWidth="2"
              initial={{ r: 0 }}
              animate={{ r: 5 }}
              transition={{ delay: 0.3 + idx * 0.1 }}
            />
            <text
              x={xScale(x) + 8}
              y={yScale(y) - 6}
              fill="rgba(251,191,36,0.8)"
              fontSize="10"
            >
              ({x},{y})
            </text>
          </g>
        );
      })}
    </motion.svg>
  );
}

// ── Venn Diagram ──

function VennDiagram({
  config,
  ...animProps
}: MathVisualizerProps & Record<string, unknown>) {
  const { data = [3, 5, 4, 2], labels = ['A', 'B'], width = 280, height = 200 } = config;
  // data: [only A, both, only B, neither]
  const cx = width / 2;
  const cy = height / 2 + 10;
  const r = 70;
  const offsetX = 28;

  return (
    <motion.svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      className="my-4"
      {...animProps}
    >
      {/* Neither */}
      {data[3] !== undefined && (
        <text
          x={width - 20}
          y={height - 10}
          textAnchor="end"
          fill="rgba(255,255,255,0.3)"
          fontSize="11"
        >
          Neither: {data[3]}
        </text>
      )}
      {/* Set A */}
      <motion.circle
        cx={cx - offsetX}
        cy={cy}
        r={r}
        fill="rgba(96,165,250,0.15)"
        stroke="rgba(96,165,250,0.6)"
        strokeWidth="2"
        initial={{ r: 0 }}
        animate={{ r }}
        transition={{ duration: 0.4 }}
      />
      {/* Set B */}
      <motion.circle
        cx={cx + offsetX}
        cy={cy}
        r={r}
        fill="rgba(251,191,36,0.15)"
        stroke="rgba(251,191,36,0.6)"
        strokeWidth="2"
        initial={{ r: 0 }}
        animate={{ r }}
        transition={{ duration: 0.4, delay: 0.1 }}
      />
      {/* Labels */}
      <text
        x={cx - offsetX - r / 2}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        fill="rgba(96,165,250,0.8)"
        fontSize="14"
        fontWeight="bold"
      >
        {labels[0] || 'A'}
      </text>
      <text
        x={cx + offsetX + r / 2}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        fill="rgba(251,191,36,0.8)"
        fontSize="14"
        fontWeight="bold"
      >
        {labels[1] || 'B'}
      </text>
      {/* Values */}
      <text
        x={cx - offsetX - 20}
        y={cy + 20}
        textAnchor="middle"
        fill="rgba(255,255,255,0.6)"
        fontSize="13"
        fontWeight="bold"
      >
        {data[0]}
      </text>
      <text
        x={cx}
        y={cy - 2}
        textAnchor="middle"
        fill="rgba(255,255,255,0.7)"
        fontSize="13"
        fontWeight="bold"
      >
        {data[2]}
      </text>
      <text
        x={cx + offsetX + 20}
        y={cy + 20}
        textAnchor="middle"
        fill="rgba(255,255,255,0.6)"
        fontSize="13"
        fontWeight="bold"
      >
        {data[1]}
      </text>
    </motion.svg>
  );
}

// ── Tree Diagram ──

function TreeDiagram({
  config,
  ...animProps
}: MathVisualizerProps & Record<string, unknown>) {
  const { labels = ['H', 'T'], width = 300, height = 200 } = config;
  const startX = width / 2;
  const startY = 15;
  const levelH = 55;
  const branchW = 60;

  const branches = [
    { x1: startX, y1: startY, x2: startX - branchW, y2: startY + levelH, label: labels[0] || 'H', prob: '1/2' },
    { x1: startX, y1: startY, x2: startX + branchW, y2: startY + levelH, label: labels[1] || 'T', prob: '1/2' },
  ];

  const leafNodes = [
    { x: startX - branchW, y: startY + levelH, label: labels[0] || 'H', prob: '1/4' },
    { x: startX + branchW, y: startY + levelH, label: labels[1] || 'T', prob: '1/4' },
  ];

  return (
    <motion.svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      className="my-4"
      {...animProps}
    >
      {/* Root */}
      <motion.circle
        cx={startX}
        cy={startY}
        r="6"
        fill="rgba(163,230,53,0.8)"
        initial={{ r: 0 }}
        animate={{ r: 6 }}
      />
      {/* Branches */}
      {branches.map((b, idx) => (
        <g key={idx}>
          <motion.line
            x1={b.x1}
            y1={b.y1}
            x2={b.x2}
            y2={b.y2}
            stroke="rgba(255,255,255,0.3)"
            strokeWidth="1.5"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: 0.2 + idx * 0.1, duration: 0.3 }}
          />
          <motion.circle
            cx={b.x2}
            cy={b.y2}
            r="5"
            fill="rgba(255,255,255,0.15)"
            stroke="rgba(255,255,255,0.3)"
            strokeWidth="1"
            initial={{ r: 0 }}
            animate={{ r: 5 }}
            transition={{ delay: 0.3 + idx * 0.1 }}
          />
          <text
            x={(b.x1 + b.x2) / 2 + (idx === 0 ? -12 : 12)}
            y={(b.y1 + b.y2) / 2 - 4}
            textAnchor="middle"
            fill="rgba(163,230,53,0.7)"
            fontSize="10"
          >
            {b.prob}
          </text>
          <text
            x={b.x2}
            y={b.y2 + 16}
            textAnchor="middle"
            fill="rgba(255,255,255,0.6)"
            fontSize="11"
          >
            {b.label}
          </text>
        </g>
      ))}
      {/* Leaf probabilities */}
      {leafNodes.map((n, idx) => (
        <text
          key={idx}
          x={n.x}
          y={n.y + 32}
          textAnchor="middle"
          fill="rgba(163,230,53,0.6)"
          fontSize="10"
        >
          P({n.label}) = {n.prob}
        </text>
      ))}
    </motion.svg>
  );
}

// ── Punnett Square ──

function PunnettSquare({
  config,
  ...animProps
}: MathVisualizerProps & Record<string, unknown>) {
  const { labels = ['T', 't'], data, width = 200, height = 200 } = config;
  const size = width - 40;
  const cellSize = size / 2;
  const offsetX = 20;
  const offsetY = 20;

  // Default outcomes if no data
  const outcomes = data?.length
    ? data
    : ['TT', 'Tt', 'Tt', 'tt'];

  const rowLabels = [labels[0] || 'T', labels[1] || 't'];
  const colLabels = [labels[0] || 'T', labels[1] || 't'];

  const cellColors = [
    'rgba(163,230,53,0.12)',
    'rgba(163,230,53,0.08)',
    'rgba(163,230,53,0.08)',
    'rgba(251,191,36,0.12)',
  ];

  return (
    <motion.svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      className="my-4"
      {...animProps}
    >
      {/* Parent labels */}
      <text x={offsetX + cellSize} y={offsetY - 6} textAnchor="middle" fill="rgba(96,165,250,0.7)" fontSize="11" fontWeight="bold">
        {rowLabels[0]}
      </text>
      <text x={offsetX + size - cellSize / 2} y={offsetY - 6} textAnchor="middle" fill="rgba(96,165,250,0.7)" fontSize="11" fontWeight="bold">
        {rowLabels[1]}
      </text>
      <text x={offsetX - 6} y={offsetY + cellSize} textAnchor="end" fill="rgba(251,191,36,0.7)" fontSize="11" fontWeight="bold">
        {colLabels[0]}
      </text>
      <text x={offsetX - 6} y={offsetY + size - cellSize / 2} textAnchor="end" fill="rgba(251,191,36,0.7)" fontSize="11" fontWeight="bold">
        {colLabels[1]}
      </text>

      {/* Grid lines */}
      <rect
        x={offsetX}
        y={offsetY}
        width={size}
        height={size}
        fill="none"
        stroke="rgba(255,255,255,0.2)"
        strokeWidth="1.5"
      />
      <line x1={offsetX + cellSize} y1={offsetY} x2={offsetX + cellSize} y2={offsetY + size} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
      <line x1={offsetX} y1={offsetY + cellSize} x2={offsetX + size} y2={offsetY + cellSize} stroke="rgba(255,255,255,0.2)" strokeWidth="1" />

      {/* Cells */}
      {outcomes.map((outcome: string | number, idx: number) => {
        const row = Math.floor(idx / 2);
        const col = idx % 2;
        const cx = offsetX + col * cellSize + cellSize / 2;
        const cy = offsetY + row * cellSize + cellSize / 2;

        return (
          <g key={idx}>
            <motion.rect
              x={offsetX + col * cellSize + 2}
              y={offsetY + row * cellSize + 2}
              width={cellSize - 4}
              height={cellSize - 4}
              rx="4"
              fill={cellColors[idx]}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 + idx * 0.1 }}
            />
            <motion.text
              x={cx}
              y={cy + 1}
              textAnchor="middle"
              dominantBaseline="central"
              fill="rgba(255,255,255,0.8)"
              fontSize="16"
              fontWeight="bold"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + idx * 0.1, type: 'spring', stiffness: 200 }}
            >
              {outcome}
            </motion.text>
          </g>
        );
      })}

      {/* Ratio label */}
      <text
        x={width / 2}
        y={height - 4}
        textAnchor="middle"
        fill="rgba(255,255,255,0.3)"
        fontSize="10"
      >
        Genotype ratio: 1 : 2 : 1
      </text>
    </motion.svg>
  );
}

// ── Fraction Pie ──

function FractionPie({
  config,
  ...animProps
}: MathVisualizerProps & Record<string, unknown>) {
  const { data = [3, 4], labels = ['Shaded', 'Total'], width = 180, height = 200 } = config;
  const cx = width / 2;
  const cy = 80;
  const r = 60;
  const numerator = data[0] || 0;
  const denominator = data[1] || 1;
  const fraction = numerator / denominator;
  const angle = fraction * 360;

  function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  const start = polarToCartesian(cx, cy, r, 0);
  const end = polarToCartesian(cx, cy, r, Math.min(angle, 359.9));
  const largeArc = angle > 180 ? 1 : 0;

  let pathD = '';
  if (fraction >= 1) {
    // Full circle
    const mid = polarToCartesian(cx, cy, r, 180);
    pathD = `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 0 1 ${mid.x} ${mid.y} A ${r} ${r} 0 0 1 ${end.x} ${end.y} Z`;
  } else if (fraction <= 0) {
    pathD = `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 0 1 ${start.x} ${start.y} Z`;
  } else {
    pathD = `M ${cx} ${cy} L ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y} Z`;
  }

  return (
    <motion.svg
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      className="my-4"
      {...animProps}
    >
      {/* Full circle outline */}
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="rgba(255,255,255,0.05)"
        stroke="rgba(255,255,255,0.2)"
        strokeWidth="2"
      />
      {/* Shaded portion */}
      <motion.path
        d={pathD}
        fill="rgba(96,165,250,0.5)"
        stroke="rgba(96,165,250,0.8)"
        strokeWidth="1.5"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      />
      {/* Label */}
      <text
        x={cx}
        y={cy}
        textAnchor="middle"
        dominantBaseline="central"
        fill="rgba(255,255,255,0.8)"
        fontSize="20"
        fontWeight="bold"
      >
        {numerator}/{denominator}
      </text>
      <text
        x={cx}
        y={cy + r + 22}
        textAnchor="middle"
        fill="rgba(255,255,255,0.4)"
        fontSize="11"
      >
        {fraction === 1 ? '1 whole' : `${Math.round(fraction * 100)}%`}
      </text>
    </motion.svg>
  );
}
