import React from 'react';
import { ExternalLink, Clock, TrendingUp, TrendingDown, Minus, Newspaper } from 'lucide-react';

interface Article {
  title: string;
  summary: string;
  link: string;
  published: string;
  source: string;
  timestamp: number;
}

interface NewsSentiment {
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  score: number;
  summary: string;
  articles?: Article[];
  headlines?: string[];
  timestamp: number;
}

interface NewsPanelProps {
  newsSentiment?: NewsSentiment | null;
}

function SentimentBadge({ sentiment, score }: { sentiment: string, score: number }) {
  if (sentiment === 'BULLISH') {
    return (
      <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-green-500/20 text-green-400 border border-green-500/30">
        <TrendingUp className="h-3.5 w-3.5" />
        BULLISH ({score.toFixed(2)})
      </span>
    );
  }
  if (sentiment === 'BEARISH') {
    return (
      <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">
        <TrendingDown className="h-3.5 w-3.5" />
        BEARISH ({score.toFixed(2)})
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-gray-500/20 text-gray-400 border border-gray-500/30">
      <Minus className="h-3.5 w-3.5" />
      NEUTRAL ({score.toFixed(2)})
    </span>
  );
}

export function NewsPanel({ newsSentiment }: NewsPanelProps) {
  if (!newsSentiment) {
    return (
      <div className="flex flex-col items-center justify-center h-64 border border-gray-700/60 rounded-2xl bg-gray-900 shadow-xl">
        <div className="animate-pulse bg-blue-500/20 p-4 rounded-full mb-4">
          <Newspaper className="h-8 w-8 text-blue-400" />
        </div>
        <p className="text-gray-400 font-medium">Fetching Live Market News...</p>
        <p className="text-xs text-gray-500 mt-2">Waiting for next RSS sync.</p>
      </div>
    );
  }

  const articles = newsSentiment.articles || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* ── Sentiment Summary Header ───────────────────────── */}
      <div className="rounded-2xl border border-gray-700/60 bg-gray-900 p-6 shadow-xl relative overflow-hidden">
        {/* Glow Effect */}
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 opacity-50" />
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Newspaper className="h-5 w-5 text-purple-400" />
            <h2 className="text-lg font-bold text-white tracking-wide">Macro AI Analysis</h2>
          </div>
          <SentimentBadge sentiment={newsSentiment.sentiment} score={newsSentiment.score} />
        </div>
        
        <p className="text-sm text-gray-300 leading-relaxed bg-gray-800/40 p-4 rounded-xl border border-gray-700/50">
          {newsSentiment.summary}
        </p>
        <div className="mt-4 flex justify-end">
          <span className="text-xs text-gray-500 flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Last Updated: {new Date(newsSentiment.timestamp * 1000).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* ── Full Articles Feed ─────────────────────────────── */}
      <div className="rounded-2xl border border-gray-700/60 bg-gray-900 p-6 shadow-xl">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-6">
          Live News Feed
        </h3>

        {articles.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-8">No articles fetched yet.</p>
        ) : (
          <div className="space-y-4">
            {articles.map((article, idx) => (
              <a 
                key={idx} 
                href={article.link}
                target="_blank"
                rel="noreferrer"
                className="block p-4 rounded-xl bg-gray-800/30 hover:bg-gray-800/60 border border-gray-700/30 hover:border-blue-500/30 transition-all group"
              >
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1">
                    <h4 className="text-base font-semibold text-gray-200 group-hover:text-blue-400 transition-colors line-clamp-2">
                      {article.title}
                    </h4>
                    {article.summary && (
                      <p className="text-sm text-gray-400 mt-2 line-clamp-2" dangerouslySetInnerHTML={{ __html: article.summary }} />
                    )}
                  </div>
                  <ExternalLink className="h-4 w-4 text-gray-500 group-hover:text-blue-400 mt-1 shrink-0" />
                </div>
                
                <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                  <span className="px-2 py-0.5 rounded bg-gray-800 border border-gray-700 font-medium">
                    {article.source || "Feed"}
                  </span>
                  {article.published && (
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {article.published}
                    </span>
                  )}
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
