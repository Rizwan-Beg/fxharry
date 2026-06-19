from typing import Dict, Any

class TradeQualityScorer:
    """
    Trade Quality Scoring System (Layer 7).
    Generates a 0-100 conviction score based on:
    - Technical Conviction (0-40 points)
    - Market Regime Alignment (0-20 points)
    - Session Liquidity/Quality (0-20 points)
    - LLM Macro Sentiment (0-20 points)
    """
    
    def __init__(self, min_threshold: int = 80):
        self.min_threshold = min_threshold
        
    def score_trade(
        self, 
        technical_score: int, 
        regime_data: Dict[str, Any], 
        session_score: int, 
        llm_sentiment_score: int,
        action: str
    ) -> Dict[str, Any]:
        """
        Calculate total trade conviction.
        
        Args:
            technical_score: 0-40, derived from H4/M5 alignment.
            regime_data: Output from RegimeDetector (e.g. {'regime': 'STRONG_TREND', 'adx': 30})
            session_score: 0-20, scaled from SessionFilter (which outputs 0-100, so we scale by 0.2)
            llm_sentiment_score: 0-20, derived from daily LLM macro analysis.
            action: "LONG" or "SHORT"
            
        Returns:
            Dict containing the final score, breakdown, and whether it passed the threshold.
        """
        # 1. Technical Score (Max 40)
        t_score = max(0, min(40, technical_score))
        
        # 2. Regime Score (Max 20)
        regime = regime_data.get('regime', 'RANGING')
        r_score = 0
        if regime == "STRONG_TREND":
            r_score = 20
        elif regime == "WEAK_TREND":
            r_score = 10
        elif regime == "HIGH_VOLATILITY":
            # Risky, penalize slightly but allow if other factors are perfect
            r_score = 5
        else: # RANGING
            # If technicals rely on range, this should be inverted by the caller,
            # but standard systems trend follow.
            r_score = 0
            
        # 3. Session Score (Max 20)
        # SessionFilter outputs 0-100. Scale to 20.
        s_score = int(session_score * 0.2)
        
        # 4. LLM Sentiment Score (Max 20)
        # Assume LLM outputs 0-20 directly based on directional alignment.
        l_score = max(0, min(20, llm_sentiment_score))
        
        total_score = t_score + r_score + s_score + l_score
        
        passed = total_score >= self.min_threshold
        
        return {
            "total_score": total_score,
            "passed_threshold": passed,
            "action": action,
            "breakdown": {
                "technical": t_score,
                "regime": r_score,
                "session": s_score,
                "llm_macro": l_score
            },
            "context": f"Regime: {regime}, Session: {session_score}/100"
        }
