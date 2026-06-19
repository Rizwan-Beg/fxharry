"""
LLM-powered AI Brain Engine using the universal OpenAI SDK.
By default, this is configured to use Groq, but it can be easily swapped
to OpenAI, local Ollama, or any other provider by changing the base_url and api_key.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional

from ai_core.core.logger import get_logger

logger = get_logger(__name__)


class LLMAgent:
    """
    AI reasoning agent.
    Analyzes live market data step-by-step and produces structured trading advice.
    """

    STEP_ICONS = {
        1: "📊",
        2: "⚡",
        3: "🎯",
        4: "🛡️",
        5: "🧠",
    }

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self._client = None
        self._initialized = False
        logger.info(f"LLMAgent created — model: {self.model_name}")

    # ------------------------------------------------------------------
    # Client initialization (lazy)
    # ------------------------------------------------------------------
    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")

        # By default, use Groq. To switch to OpenAI, remove the base_url.
        # To switch to Ollama, set base_url="http://localhost:11434/v1" and api_key="ollama"
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("API key is not set in environment / .env file")

        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1" # Remove or change this line to switch providers
        )
        self._initialized = True
        logger.info("✅ AsyncOpenAI client initialized (configured for Groq)")
        return self._client

    # ------------------------------------------------------------------
    # Core reasoning method
    # ------------------------------------------------------------------
    async def reason(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask the LLM to reason step-by-step about the current market state.

        Returns a structured dict with steps, sentiment, recommendation,
        confidence, reasoning text, and risk warning.
        """
        t0 = time.time()

        # ── Build human-readable context for the prompt ──────────────
        candles = context.get("candles", {})
        m1  = candles.get("1m",  {})
        m5  = candles.get("5m",  {})
        m15 = candles.get("15m", {})

        def fmt_candle(c: dict) -> str:
            if not c:
                return "N/A"
            return (
                f"O={c.get('open', '?'):.5f} "
                f"H={c.get('high', '?'):.5f} "
                f"L={c.get('low',  '?'):.5f} "
                f"C={c.get('close','?'):.5f}"
            )

        spread_pips = round(context.get("spread", 0) * 10_000, 1)

        sig_list = context.get("signals", [])
        if sig_list:
            signals_text = "; ".join(
                f"{s.get('strategy_id','?')}→{s.get('action','?')} "
                f"(conf {s.get('confidence', 0):.0%})"
                for s in sig_list
            )
        else:
            signals_text = "None so far"

        # ── Prompt ───────────────────────────────────────────────────
        news = context.get('news', {})
        news_text = f"Sentiment: {news.get('sentiment', 'NEUTRAL')} ({news.get('score', 0):.2f})\n    News Summary: {news.get('summary', 'None')}"

        prompt = f"""You are an expert AI forex trading analyst. Analyze this live market snapshot and think step by step.

═══ LIVE MARKET DATA ═══
Symbol  : {context.get('symbol', 'EURUSD')}
Price   : Bid {context.get('bid', 0):.5f} / Ask {context.get('ask', 0):.5f}  (spread {spread_pips} pips)
1m  Bar : {fmt_candle(m1)}
5m  Bar : {fmt_candle(m5)}
15m Bar : {fmt_candle(m15)}
Signals : {signals_text}
News    : {news_text}
Balance : ${context.get('balance', 'N/A')}
Positions: {context.get('position_count', 0)} open
Trigger : {context.get('trigger', 'PERIODIC')}
═══════════════════════

Think through exactly FIVE steps. Return ONLY valid JSON — no markdown, no explanation outside the JSON:

{{
  "steps": [
    {{"step": 1, "action": "Market Structure Analysis", "detail": "<one sentence about price structure, trend direction, key levels>"}},
    {{"step": 2, "action": "Momentum & Candle Patterns", "detail": "<one sentence about momentum from candle shapes and price velocity>"}},
    {{"step": 3, "action": "Signal Evaluation", "detail": "<one sentence evaluating the active strategy signals above>"}},
    {{"step": 4, "action": "Risk Assessment", "detail": "<one sentence on spread, session timing, volatility risk>"}},
    {{"step": 5, "action": "Final Decision", "detail": "<one sentence final call and the primary reason>"}}
  ],
  "sentiment": "BULLISH",
  "recommendation": "HOLD",
  "confidence": 0.72,
  "reasoning": "<2-3 sentence professional market summary>",
  "risk_warning": "<string if notable risk, otherwise null>"
}}

Rules:
- sentiment must be BULLISH, BEARISH, or NEUTRAL
- recommendation must be BUY, SELL, or HOLD
- confidence is a float 0.0–1.0
- Keep each step detail under 15 words
- risk_warning is null (JSON null) if there is nothing notable"""

        # ── Call LLM ─────────────────────────────────────────────────
        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional forex trading AI. "
                            "Always respond with raw JSON only — no markdown fences, no prose outside JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.25,
                max_tokens=700,
            )

            raw = response.choices[0].message.content.strip()

            # Strip accidental markdown fences
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()

            result: Dict[str, Any] = json.loads(raw)

            # Attach metadata
            result["symbol"]     = context.get("symbol", "EURUSD")
            result["trigger"]    = context.get("trigger", "PERIODIC")
            result["model"]      = self.model_name
            result["latency_ms"] = round((time.time() - t0) * 1000)
            result["timestamp"]  = time.strftime("%Y-%m-%dT%H:%M:%S")
            result["active_signals"] = context.get("signals", [])

            logger.info(
                f"🧠 AI [{result['symbol']}] "
                f"{result.get('sentiment','?')} | "
                f"{result.get('recommendation','?')} | "
                f"conf={result.get('confidence', 0):.0%} | "
                f"{result['latency_ms']}ms"
            )
            return result

        except json.JSONDecodeError as exc:
            logger.error(f"LLM returned invalid JSON: {exc} | raw={raw[:200]}")
            return self._fallback(context, f"JSON parse error: {exc}")
        except Exception as exc:
            logger.error(f"LLM reasoning failed: {exc}", exc_info=True)
            return self._fallback(context, str(exc))

    # ------------------------------------------------------------------
    # Fallback when LLM is unavailable
    # ------------------------------------------------------------------
    def _fallback(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        return {
            "steps": [
                {"step": 1, "action": "Market Structure Analysis",  "detail": "AI offline — rule-based data only"},
                {"step": 2, "action": "Momentum & Candle Patterns", "detail": "Candle data available in main feed"},
                {"step": 3, "action": "Signal Evaluation",          "detail": "Strategy signals still active"},
                {"step": 4, "action": "Risk Assessment",            "detail": "Manual review recommended"},
                {"step": 5, "action": "Final Decision",             "detail": "HOLD until AI analysis restores"},
            ],
            "sentiment":     "NEUTRAL",
            "recommendation": "HOLD",
            "confidence":    0.0,
            "reasoning":     "AI reasoning engine temporarily unavailable. Rule-based strategies remain active.",
            "risk_warning":  "AI analysis offline — manual oversight recommended",
            "symbol":        context.get("symbol", "EURUSD"),
            "trigger":       "ERROR",
            "model":         self.model_name,
            "latency_ms":    0,
            "timestamp":     time.strftime("%Y-%m-%dT%H:%M:%S"),
            "error":         error[:200],
        }

    # ------------------------------------------------------------------
    # Generate signals from reasoning (optional — Phase 2 bridge)
    # ------------------------------------------------------------------
    async def generate_signals(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        If LLM confidence is high enough, produce a trading signal.
        Currently advisory only (not auto-executed).
        """
        reasoning = await self.reason(market_data)
        if (
            reasoning.get("recommendation") in ("BUY", "SELL")
            and float(reasoning.get("confidence", 0)) >= 0.75
        ):
            return [
                {
                    "strategy_id": "llm_brain",
                    "symbol":      market_data.get("symbol", "EURUSD"),
                    "action":      reasoning["recommendation"],
                    "confidence":  reasoning["confidence"],
                    "reason":      reasoning.get("reasoning", ""),
                    "timestamp":   reasoning["timestamp"],
                }
            ]
        return []