import React, { useEffect, useRef, useState } from 'react';
import {
  Brain,
  Zap,
  TrendingUp,
  TrendingDown,
  Minus,
  CheckCircle,
  Clock,
  AlertTriangle,
  Activity,
  ChevronRight,
} from 'lucide-react';

interface ReasoningStep {
  step: number;
  action: string;
  detail: string;
}

interface ActiveSignal {
  strategy_id: string;
  action: string;
  confidence: number;
  reason?: string;
}

interface AIReasoning {
  symbol: string;
  trigger: string;
  model: string;
  timestamp: string;
  latency_ms: number;
  steps: ReasoningStep[];
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  recommendation: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  risk_warning: string | null;
  error?: string;
  active_signals?: ActiveSignal[];
}

interface AIBrainPanelProps {
  aiReasoning: AIReasoning | null;
  aiHistory: AIReasoning[];
  newsSentiment?: any;
}

const STEP_ICONS = [
  <Activity   key={1} className="h-4 w-4" />,
  <Zap        key={2} className="h-4 w-4" />,
  <ChevronRight key={3} className="h-4 w-4" />,
  <AlertTriangle key={4} className="h-4 w-4" />,
  <Brain      key={5} className="h-4 w-4" />,
];

function SentimentBadge({ sentiment }: { sentiment: string }) {
  const map: Record<string, { color: string; icon: JSX.Element; label: string }> = {
    BULLISH: { color: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30', icon: <TrendingUp className="h-4 w-4" />, label: 'BULLISH' },
    BEARISH: { color: 'text-red-400 bg-red-400/10 border-red-400/30',           icon: <TrendingDown className="h-4 w-4" />, label: 'BEARISH' },
    NEUTRAL: { color: 'text-gray-400 bg-gray-400/10 border-gray-400/30',         icon: <Minus className="h-4 w-4" />,        label: 'NEUTRAL' },
  };
  const cfg = map[sentiment] ?? map.NEUTRAL;
  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold border ${cfg.color}`}>
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

function RecommendationBadge({ rec }: { rec: string }) {
  const map: Record<string, string> = {
    BUY:  'bg-emerald-500 text-white shadow-emerald-500/30',
    SELL: 'bg-red-500 text-white shadow-red-500/30',
    HOLD: 'bg-amber-500 text-white shadow-amber-500/30',
  };
  return (
    <span className={`px-5 py-2 rounded-xl text-sm font-black tracking-widest shadow-lg ${map[rec] ?? map.HOLD}`}>
      {rec}
    </span>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 70 ? 'bg-emerald-500' :
    pct >= 40 ? 'bg-amber-500' :
                'bg-red-500';
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>Confidence</span>
        <span className="font-bold text-white">{pct}%</span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function TriggerBadge({ trigger }: { trigger: string }) {
  const map: Record<string, string> = {
    SIGNAL:   'bg-purple-500/20 text-purple-400 border-purple-500/30',
    PERIODIC: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    ERROR:    'bg-red-500/20 text-red-400 border-red-500/30',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${map[trigger] ?? map.PERIODIC}`}>
      {trigger}
    </span>
  );
}

function HistoryItem({ item, index }: { item: AIReasoning; index: number }) {
  const recColor: Record<string, string> = {
    BUY:  'text-emerald-400',
    SELL: 'text-red-400',
    HOLD: 'text-amber-400',
  };
  return (
    <div className="flex items-center gap-3 px-4 py-2 rounded-lg bg-gray-800/60 border border-gray-700/50 hover:border-gray-600 transition-colors">
      <div className="text-xs text-gray-500 w-16 shrink-0 font-mono">
        {item.timestamp?.slice(11, 16) || '--:--'}
      </div>
      <div className={`text-xs font-black w-10 shrink-0 ${recColor[item.recommendation] ?? 'text-gray-400'}`}>
        {item.recommendation}
      </div>
      <div className="text-xs text-gray-400 shrink-0 w-12">
        {Math.round(item.confidence * 100)}%
      </div>
      <div className="text-xs text-gray-500 truncate flex-1">
        {item.symbol} · {item.sentiment}
      </div>
      <div className="text-xs text-gray-600 shrink-0">
        {item.latency_ms}ms
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────
export function AIBrainPanel({ aiReasoning, aiHistory, newsSentiment }: AIBrainPanelProps) {
  const [pulse, setPulse] = useState(false);
  const prevTimestamp = useRef<string | null>(null);

  // Pulse animation when new reasoning arrives
  useEffect(() => {
    if (aiReasoning?.timestamp && aiReasoning.timestamp !== prevTimestamp.current) {
      prevTimestamp.current = aiReasoning.timestamp;
      setPulse(true);
      const t = setTimeout(() => setPulse(false), 1500);
      return () => clearTimeout(t);
    }
  }, [aiReasoning]);

  // ── Waiting for first analysis ────────────────────────────────────
  if (!aiReasoning) {
    return (
      <div className="flex flex-col items-center justify-center h-64 space-y-4 text-gray-500">
        <div className="relative">
          <Brain className="h-16 w-16 text-blue-500/40" />
          <div className="absolute inset-0 rounded-full border-2 border-blue-500/20 animate-ping" />
        </div>
        <p className="text-sm font-medium">AI Brain initialising…</p>
        <p className="text-xs text-gray-600">First analysis arrives within 60 seconds of IBKR data</p>
      </div>
    );
  }

  const rec = aiReasoning.recommendation;
  const recGlow =
    rec === 'BUY'  ? 'shadow-emerald-500/20' :
    rec === 'SELL' ? 'shadow-red-500/20' :
                     'shadow-amber-500/20';

  return (
    <div className="space-y-4">

      {/* ── Header ────────────────────────────────────────────────── */}
      <div className={`rounded-2xl border bg-gray-900 p-5 transition-all duration-500 ${
        pulse
          ? 'border-blue-500/60 shadow-lg shadow-blue-500/10'
          : 'border-gray-700/60'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-xl bg-blue-500/10 border border-blue-500/20 ${pulse ? 'animate-pulse' : ''}`}>
              <Brain className="h-5 w-5 text-blue-400" />
            </div>
            <div>
              <h2 className="text-white font-bold text-base">AI Brain Engine</h2>
              <p className="text-xs text-gray-500 font-mono">{aiReasoning.model}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-right">
            <div>
              <div className="text-xs text-gray-500 flex items-center gap-1 justify-end">
                <Clock className="h-3 w-3" />
                {aiReasoning.timestamp?.slice(11, 19) || '—'}
              </div>
              <div className="text-xs text-gray-600">
                {aiReasoning.latency_ms}ms · <TriggerBadge trigger={aiReasoning.trigger} />
              </div>
            </div>
          </div>
        </div>

        {/* Symbol row */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm font-bold text-blue-300 bg-blue-500/10 px-3 py-1 rounded-lg border border-blue-500/20">
            {aiReasoning.symbol}
          </span>
          <SentimentBadge sentiment={aiReasoning.sentiment} />
        </div>

        {/* ── Active Signals ──────────────────────────────────────── */}
        {aiReasoning.active_signals && aiReasoning.active_signals.length > 0 && (
          <div className="space-y-2 mb-5">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Strategy Signals
            </p>
            {aiReasoning.active_signals.map((sig, i) => (
              <div key={i} className="flex flex-col p-3 rounded-xl bg-purple-500/10 border border-purple-500/30">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-purple-300 uppercase">{sig.strategy_id}</span>
                  <RecommendationBadge rec={sig.action} />
                </div>
                <div className="flex justify-between items-center text-xs text-purple-400/80 mt-2">
                  <span className="font-semibold">Confidence: {Math.round(sig.confidence * 100)}%</span>
                </div>
                {sig.reason && (
                  <p className="text-xs text-purple-200/80 mt-2 leading-relaxed">
                    {sig.reason}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* ── Thinking Steps ──────────────────────────────────────── */}
        <div className="space-y-2 mb-5">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Reasoning Process
          </p>
          {(aiReasoning.steps || []).map((s, i) => (
            <div
              key={s.step}
              className="flex items-start gap-3 p-3 rounded-xl bg-gray-800/60 border border-gray-700/40 hover:border-gray-600/60 transition-all"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              {/* Step icon + number */}
              <div className="flex items-center gap-2 shrink-0">
                <div className="w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-xs font-bold text-blue-400">
                  {s.step}
                </div>
                <span className="text-blue-400/70">{STEP_ICONS[i]}</span>
              </div>

              {/* Action + detail */}
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-gray-300">{s.action}</p>
                <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{s.detail}</p>
              </div>

              <CheckCircle className="h-4 w-4 text-emerald-500/60 shrink-0 mt-0.5" />
            </div>
          ))}
        </div>

        {/* ── Verdict ─────────────────────────────────────────────── */}
        <div className={`rounded-xl border p-4 bg-gray-800/40 shadow-lg ${recGlow}`}>
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Verdict</p>
            <RecommendationBadge rec={rec} />
          </div>

          <ConfidenceBar value={aiReasoning.confidence} />

          <p className="text-sm text-gray-300 mt-3 leading-relaxed">
            {aiReasoning.reasoning}
          </p>

          {aiReasoning.risk_warning && (
            <div className="mt-3 flex items-start gap-2 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
              <AlertTriangle className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" />
              <p className="text-xs text-amber-300">{aiReasoning.risk_warning}</p>
            </div>
          )}

          {aiReasoning.error && (
            <div className="mt-2 flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
              <AlertTriangle className="h-4 w-4 text-red-400 mt-0.5 shrink-0" />
              <p className="text-xs text-red-300 font-mono">{aiReasoning.error}</p>
            </div>
          )}
        </div>
      </div>

      {/* ── News & Sentiment ──────────────────────────────────────── */}
      {newsSentiment && (
        <div className="rounded-2xl border border-gray-700/60 bg-gray-900 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-purple-400" />
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Macro News Sentiment
              </p>
            </div>
            <SentimentBadge sentiment={newsSentiment.sentiment} />
          </div>
          
          <p className="text-sm text-gray-300 mb-4 leading-relaxed bg-gray-800/40 p-3 rounded-lg border border-gray-700/50">
            {newsSentiment.summary}
          </p>

          {newsSentiment.headlines && newsSentiment.headlines.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-gray-500 font-semibold uppercase">Recent Headlines</p>
              <ul className="space-y-2">
                {newsSentiment.headlines.slice(0, 3).map((h: string, i: number) => (
                  <li key={i} className="text-xs text-gray-400 flex items-start gap-2">
                    <span className="text-purple-500/50 mt-0.5">•</span>
                    <span>{h}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* ── History ───────────────────────────────────────────────── */}
      {aiHistory.length > 1 && (
        <div className="rounded-2xl border border-gray-700/60 bg-gray-900 p-5">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Recent AI Decisions
          </p>
          <div className="space-y-2">
            {aiHistory.slice(1, 7).map((item, i) => (
              <HistoryItem key={`${item.timestamp}-${i}`} item={item} index={i} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
