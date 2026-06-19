# QuantX Trade Decision Pipeline

Based on the architecture and codebase of the QuantX project, deciding and placing a trade involves a highly sophisticated, multi-stage pipeline before an order is actually routed to a broker. 

Here is the step-by-step process of everything that happens before a trade is placed:

### 1. Market Data Ingestion & Feature Extraction
* **Tick Processing:** Live price ticks (from brokers like IBKR or Polygon) are ingested by the `MarketDataService` and passed to the `StrategyManager`.
* **Feature Generation:** The `FeatureEngine` continuously updates its internal state with the new price, calculating technical indicators and structural features required by the AI models.

### 2. Context & Environment Detection
Before any technical strategy is evaluated, the system establishes "context" to understand the broader market conditions:
* **Regime Detection:** The `RegimeDetector` analyzes recent price closes to identify the current market state (e.g., trending, ranging, high volatility).
* **Session Filtering:** The `SessionFilter` identifies the active trading session (e.g., London, New York overlap) and assigns a *session quality score* since some pairs trade better during specific times.
* **LLM Macro Sentiment:** The system retrieves a dynamic macroeconomic bias score that is continuously updated in the background by a Generative AI agent reading news and sentiment.

### 3. Strategy Technical Evaluation
The `StrategyManager` evaluates the features against all active strategies concurrently. The active strategies include:
* Rule-based strategies (like Apex Multi-timeframe trend-following).
* Machine Learning models (`MLStrategy`).
* Smart Money Concepts (`SmartMoneyStrategy` analyzing 4H -> 1H -> 5M structures).

Each active strategy attempts to generate a raw signal (BUY/SELL) and assigns it a preliminary **Technical Score** (up to 40 points).

### 4. Trade Quality Scoring & Thresholds
If a raw signal is generated, it is evaluated by the `TradeQualityScorer`. This scorer calculates a comprehensive `total_score` (0-100) by combining:
1. The Strategy's **Technical Score**.
2. **Regime Data** compatibility.
3. **Session Score**.
4. **LLM Sentiment Bias**.

The trade **must pass a minimum quality threshold** (currently set to a score of `80`) to be considered a valid setup. Whether the signal passes or fails, all data is logged to a `FeatureStore` database for future ML training.

### 5. Dynamic Risk Management
If the signal passes the quality threshold, it is handed over to the `RiskManager`, which acts as the ultimate gatekeeper:
* **Dynamic Position Sizing:** Risk is dynamically scaled based on the trade's quality score. An "A+ Setup" (Score 95+) risks 2.0% of the account, a standard setup (85+) risks 1.0%, and a marginal setup (80+) risks 0.5%.
* **Hard Risk Limits & Rejection:** The `assess_trade_risk` function runs a gauntlet of safety checks:
  * **Daily Loss Limit:** Rejects the trade if the account has already hit the maximum daily loss (2%).
  * **Drawdown Limit:** Rejects the trade if the portfolio is in a drawdown exceeding 20%.
  * **Correlation Exposure:** Checks if taking this trade overexposes the portfolio to correlated assets (e.g., already holding max allocation of EURUSD and trying to buy GBPUSD).
  * **Volatility Risk:** Penalizes the risk score if trading highly volatile instruments (like XAUUSD or GBPJPY).

### 6. Final Approval & Execution
* If the `RiskManager` returns `approved: True` and assigns a safe risk level (LOW/MEDIUM), the system finally generates a formal order object.
* This order is then routed down to the Execution Engine (like the `IBKRService` or the Node.js API Gateway) to be placed on the live market.
* The trade is then tracked in the database (`trading.db`), and the real-time React dashboard is updated via WebSockets.
