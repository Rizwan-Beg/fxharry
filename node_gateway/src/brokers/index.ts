/**
 * Broker Services Registry
 * Central export for all broker implementations
 */

import type { BaseBroker } from './baseBroker';
import { OANDAService } from './oanda.service';
import { IBKRService } from './ibkr.service';
import { MT5Service } from './mt5.service';
import { BinanceService } from './binance.service';

export type BrokerType = 'oanda' | 'ibkr' | 'mt5' | 'binance';

export function createBroker(type: BrokerType, config: any): BaseBroker {
  switch (type) {
    case 'oanda':
      return new OANDAService(config.apiKey, config.accountId, config.environment);
    case 'ibkr':
      return new IBKRService(config.grpcHost, config.grpcPort);
    case 'mt5':
      return new MT5Service();
    case 'binance':
      return new BinanceService(config.apiKey, config.apiSecret, config.testnet);
    default:
      throw new Error(`Unknown broker type: ${type}`);
  }
}

export { BaseBroker } from './baseBroker';
export { OANDAService } from './oanda.service';
export { IBKRService } from './ibkr.service';
export { MT5Service } from './mt5.service';
export { BinanceService } from './binance.service';
