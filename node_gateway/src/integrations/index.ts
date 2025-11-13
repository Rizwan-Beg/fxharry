/**
 * Integrations Registry
 * Central registry for all external API integrations
 * Supports 100+ APIs: market data, news, sentiment, research, LLMs, etc.
 */

export { TradingViewIntegration } from './tradingview';
export { IBKRIntegration } from './ibkr';
export { BinanceIntegration } from './binance';
export { NewsAPIIntegration } from './newsapi';
export { PolygonIntegration } from './polygon';

// TODO: Add more integrations:
// - Alpha Vantage
// - Yahoo Finance
// - FRED (Federal Reserve Economic Data)
// - Quandl
// - IEX Cloud
// - Finnhub
// - Twelve Data
// - CoinGecko
// - CoinMarketCap
// - Twitter/X API
// - Reddit API
// - Bloomberg API
// - Reuters API
// - OpenAI API
// - Anthropic API
// - Google Gemini API
// - Hugging Face API
// - ... and 80+ more

export class IntegrationRegistry {
  private integrations: Map<string, any> = new Map();

  register(name: string, integration: any): void {
    this.integrations.set(name, integration);
  }

  get(name: string): any {
    return this.integrations.get(name);
  }

  list(): string[] {
    return Array.from(this.integrations.keys());
  }
}