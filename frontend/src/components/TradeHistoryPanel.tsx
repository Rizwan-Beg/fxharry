import React from 'react';
import { History, ArrowUpRight, ArrowDownLeft, Clock } from 'lucide-react';

interface Trade {
    id: number;
    symbol: string;
    action: string;
    quantity: number;
    entry_price: number;
    exit_price?: number;
    pnl?: number;
    status: string;
    entry_time: string;
    exit_time?: string;
}

interface TradeHistoryPanelProps {
    trades: Trade[];
}

export function TradeHistoryPanel({ trades }: TradeHistoryPanelProps) {
    if (!trades || trades.length === 0) {
        return (
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 text-center">
                <h3 className="text-lg font-semibold mb-2 flex items-center justify-center space-x-2">
                    <History className="h-5 w-5 text-gray-400" />
                    <span>Trade History</span>
                </h3>
                <p className="text-gray-400">No trades found in history.</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <History className="h-5 w-5 text-blue-400" />
                    <h3 className="text-lg font-semibold">Recent Trades</h3>
                </div>
                <div className="text-sm text-gray-400">
                    Last 50 trades
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-gray-700/50">
                        <tr>
                            <th className="p-3 font-medium text-gray-400">Time</th>
                            <th className="p-3 font-medium text-gray-400">Symbol</th>
                            <th className="p-3 font-medium text-gray-400">Type</th>
                            <th className="p-3 font-medium text-gray-400">Qty</th>
                            <th className="p-3 font-medium text-gray-400">Entry</th>
                            <th className="p-3 font-medium text-gray-400">P&L</th>
                            <th className="p-3 font-medium text-gray-400">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                        {trades.map((trade) => (
                            <tr key={trade.id} className="hover:bg-gray-700/30 transition-colors">
                                <td className="p-3 text-gray-300">
                                    <div className="flex items-center space-x-1">
                                        <Clock className="h-3 w-3 text-gray-500" />
                                        <span>{new Date(trade.entry_time).toLocaleTimeString()}</span>
                                    </div>
                                </td>
                                <td className="p-3 font-medium">{trade.symbol}</td>
                                <td className="p-3">
                                    <span className={`flex items-center space-x-1 ${trade.action === 'BUY' ? 'text-green-400' : 'text-red-400'
                                        }`}>
                                        {trade.action === 'BUY' ? (
                                            <ArrowUpRight className="h-3 w-3" />
                                        ) : (
                                            <ArrowDownLeft className="h-3 w-3" />
                                        )}
                                        <span>{trade.action}</span>
                                    </span>
                                </td>
                                <td className="p-3 text-gray-300">{trade.quantity.toLocaleString()}</td>
                                <td className="p-3 text-gray-300">{trade.entry_price?.toFixed(5)}</td>
                                <td className={`p-3 font-medium ${(trade.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                    }`}>
                                    {trade.pnl ? `$${trade.pnl.toFixed(2)}` : '-'}
                                </td>
                                <td className="p-3">
                                    <span className={`px-2 py-0.5 rounded-full text-xs ${trade.status === 'FILLED' ? 'bg-green-900/50 text-green-400 border border-green-800' :
                                            trade.status === 'CLOSED' ? 'bg-gray-700 text-gray-300' :
                                                'bg-yellow-900/30 text-yellow-400 border border-yellow-800'
                                        }`}>
                                        {trade.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
