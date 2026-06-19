import React from 'react';
import { Activity, Target, Clock, ShieldAlert, BarChart3, TrendingUp, CheckCircle, XCircle } from 'lucide-react';

interface StrategyDiagnosticsPanelProps {
  diagnostics: any;
  rejectedSignals: any[];
}

export function StrategyDiagnosticsPanel({ diagnostics, rejectedSignals }: StrategyDiagnosticsPanelProps) {
  if (!diagnostics) {
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 flex flex-col items-center justify-center h-full">
        <Activity className="h-10 w-10 text-gray-500 mb-2 animate-pulse" />
        <p className="text-gray-400 font-medium">Waiting for strategy diagnostics...</p>
      </div>
    );
  }

  const { session, session_score: raw_session_score, regime, llm_macro_score, indicators } = diagnostics;
  const m15_bias = indicators?.m15_bias;
  
  // Scale session score (0-100) down to max 20 points
  const session_score = Math.floor((raw_session_score || 0) * 0.2);
  
  // Calculate a projected total score based on current live metrics
  const projectedTechScore = 35; // Base technical score if a signal were to fire now
  const regimeScore = regime?.regime === 'STRONG_TREND' ? 20 : regime?.regime === 'WEAK_TREND' ? 10 : 0;
  const projectedTotalScore = projectedTechScore + session_score + regimeScore + llm_macro_score;
  const scoreColor = projectedTotalScore >= 80 ? 'text-green-400' : projectedTotalScore >= 60 ? 'text-yellow-400' : 'text-red-400';
  const progressColor = projectedTotalScore >= 80 ? 'bg-green-500' : projectedTotalScore >= 60 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg flex flex-col h-full overflow-hidden">
      
      {/* Header */}
      <div className="p-4 border-b border-gray-700 bg-gray-800/80 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Target className="h-5 w-5 text-blue-400" />
          <h2 className="text-lg font-bold text-white">Live Strategy Engine</h2>
        </div>
        <span className="text-xs text-gray-500 uppercase tracking-wider font-semibold">Quality Scorer (Layer 7)</span>
      </div>

      <div className="p-5 space-y-6 overflow-y-auto">
        
        {/* Conviction Meter */}
        <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-700/50">
          <div className="flex justify-between items-end mb-2">
            <div>
              <p className="text-sm text-gray-400 font-medium mb-1">Projected Execution Score</p>
              <div className="flex items-baseline gap-2">
                <span className={`text-3xl font-black ${scoreColor}`}>{projectedTotalScore}</span>
                <span className="text-gray-500 font-bold">/ 100</span>
              </div>
            </div>
            <div className="text-right">
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${projectedTotalScore >= 80 ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                {projectedTotalScore >= 80 ? 'EXECUTION READY' : 'WAITING FOR CONFIRMATION'}
              </span>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="h-3 w-full bg-gray-800 rounded-full overflow-hidden mt-3 border border-gray-700">
            <div 
              className={`h-full ${progressColor} transition-all duration-1000 ease-in-out`} 
              style={{ width: `${Math.min(100, Math.max(0, projectedTotalScore))}%` }}
            />
          </div>
          <div className="flex justify-between text-[10px] text-gray-500 mt-1 font-bold uppercase tracking-wider">
            <span>0</span>
            <span>Execution Threshold (80)</span>
            <span>100</span>
          </div>
        </div>

        {/* Scoring Breakdown Matrix */}
        <div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <BarChart3 className="h-4 w-4" /> Score Breakdown
          </h3>
          
          <div className="grid grid-cols-2 gap-3">
            {/* Session Card */}
            <div className="bg-gray-700/20 p-3 rounded-lg border border-gray-600/30">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400 font-semibold flex items-center gap-1"><Clock className="h-3 w-3"/> Session</span>
                <span className="text-sm font-bold text-blue-400">+{session_score} pts</span>
              </div>
              <p className="text-sm text-gray-200 font-bold truncate">{session?.replace(/_/g, ' ')}</p>
              <p className="text-[10px] text-gray-500 mt-1 uppercase">Max 20 marks</p>
            </div>

            {/* Regime Card */}
            <div className="bg-gray-700/20 p-3 rounded-lg border border-gray-600/30">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400 font-semibold flex items-center gap-1"><TrendingUp className="h-3 w-3"/> Regime</span>
                <span className="text-sm font-bold text-purple-400">
                  +{regime?.regime === 'STRONG_TREND' ? 20 : regime?.regime === 'WEAK_TREND' ? 10 : 0} pts
                </span>
              </div>
              <p className="text-sm text-gray-200 font-bold truncate">{regime?.regime?.replace(/_/g, ' ')}</p>
              <p className="text-[10px] text-gray-500 mt-1 uppercase">ADX: {regime?.adx?.toFixed(1)}</p>
            </div>

            {/* Macro LLM Card */}
            <div className="bg-gray-700/20 p-3 rounded-lg border border-gray-600/30">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400 font-semibold flex items-center gap-1"><ShieldAlert className="h-3 w-3"/> Macro Bias</span>
                <span className="text-sm font-bold text-amber-400">+{llm_macro_score} pts</span>
              </div>
              <p className="text-sm text-gray-200 font-bold">LLM Sentiment</p>
              <p className="text-[10px] text-gray-500 mt-1 uppercase">Max 20 marks</p>
            </div>

            {/* Technical Base Card */}
            <div className="bg-gray-700/20 p-3 rounded-lg border border-gray-600/30">
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-400 font-semibold flex items-center gap-1"><Activity className="h-3 w-3"/> Technical</span>
                <span className="text-sm font-bold text-emerald-400">Base +35 pts</span>
              </div>
              <p className="text-sm text-gray-200 font-bold">M5 Alignment</p>
              <p className="text-[10px] text-gray-500 mt-1 uppercase">Added upon signal generation</p>
            </div>
          </div>
        </div>

        {/* Live Technical Indicators */}
        <div>
          <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Live Indicators (Apex)</h3>
          <div className="grid grid-cols-4 gap-2 text-center">
            <div className="bg-gray-900/40 p-2 rounded-lg border border-gray-700">
              <p className="text-[10px] text-gray-500 uppercase">SMA 10</p>
              <p className="text-sm font-mono text-gray-200">{indicators?.sma_10?.toFixed(5) || '---'}</p>
            </div>
            <div className="bg-gray-900/40 p-2 rounded-lg border border-gray-700">
              <p className="text-[10px] text-gray-500 uppercase">SMA 30</p>
              <p className="text-sm font-mono text-gray-200">{indicators?.sma_30?.toFixed(5) || '---'}</p>
            </div>
            <div className="bg-gray-900/40 p-2 rounded-lg border border-gray-700">
              <p className="text-[10px] text-gray-500 uppercase">RSI 14</p>
              <p className={`text-sm font-mono ${indicators?.rsi_14 > 70 ? 'text-red-400' : indicators?.rsi_14 < 30 ? 'text-green-400' : 'text-gray-200'}`}>
                {indicators?.rsi_14?.toFixed(1) || '---'}
              </p>
            </div>
            <div className="bg-gray-900/40 p-2 rounded-lg border border-gray-700">
              <p className="text-[10px] text-gray-500 uppercase">M15 Bias</p>
              <p className={`text-sm font-bold ${m15_bias === 1 ? 'text-green-400' : m15_bias === -1 ? 'text-red-400' : 'text-gray-400'}`}>
                {m15_bias === 1 ? 'BULL' : m15_bias === -1 ? 'BEAR' : 'FLAT'}
              </p>
            </div>
          </div>
        </div>

        {/* Rejected Signals Log */}
        {rejectedSignals && rejectedSignals.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Recent Vetoed Signals</h3>
            <div className="space-y-3">
              {rejectedSignals.slice(0, 10).map((sig, idx) => (
                <div key={idx} className="bg-red-500/5 p-3 rounded-lg border border-red-500/20">
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-red-400" />
                      <span className="text-sm font-bold text-gray-200">{sig.action} {sig.symbol}</span>
                    </div>
                    <span className="text-xs font-mono text-red-400 font-bold bg-red-500/10 px-2 py-0.5 rounded">
                      Total: {sig.trade_score || 'N/A'}/100
                    </span>
                  </div>
                  
                  {/* Score Breakdown for specific signal */}
                  {sig.score_breakdown && (
                    <div className="grid grid-cols-4 gap-1 mb-2 bg-gray-900/50 p-2 rounded">
                      <div className="text-center">
                        <p className="text-[9px] text-gray-500 uppercase">Tech</p>
                        <p className="text-xs font-mono text-emerald-400">+{sig.score_breakdown.technical}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-[9px] text-gray-500 uppercase">Session</p>
                        <p className="text-xs font-mono text-blue-400">+{sig.score_breakdown.session}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-[9px] text-gray-500 uppercase">Regime</p>
                        <p className="text-xs font-mono text-purple-400">+{sig.score_breakdown.regime}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-[9px] text-gray-500 uppercase">Macro</p>
                        <p className="text-xs font-mono text-amber-400">+{sig.score_breakdown.llm_macro}</p>
                      </div>
                    </div>
                  )}

                  <p className="text-xs text-red-300/80 leading-tight border-l-2 border-red-500/30 pl-2 ml-1">{sig.reason}</p>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
