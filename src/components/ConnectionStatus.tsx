import React from 'react';
import { Wifi, WifiOff, Activity } from 'lucide-react';

interface ConnectionStatusProps {
  status: {
    ibkr: boolean;
    websocket: boolean;
    market_data: boolean;
  };
}

export function ConnectionStatus({ status }: ConnectionStatusProps) {
  const allConnected = status?.ibkr && status?.websocket && status?.market_data;

  return (
    <div className="flex items-center space-x-2">
      {allConnected ? (
        <>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <Wifi className="h-4 w-4 text-green-400" />
            <span className="text-sm text-green-400 font-medium">Connected</span>
          </div>
        </>
      ) : (
        <>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
            <WifiOff className="h-4 w-4 text-red-400" />
            <span className="text-sm text-red-400 font-medium">Disconnected</span>
          </div>
        </>
      )}
      
      {/* Detailed Status */}
      <div className="text-xs text-gray-400 ml-2">
        <span className={status?.ibkr ? 'text-green-400' : 'text-red-400'}>IBKR</span>
        {' • '}
        <span className={status?.websocket ? 'text-green-400' : 'text-red-400'}>WS</span>
        {' • '}
        <span className={status?.market_data ? 'text-green-400' : 'text-red-400'}>Data</span>
      </div>
    </div>
  );
}