import React from 'react';
import { X, History, ArrowUpRight, ArrowDownLeft, Clock } from 'lucide-react';

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

interface TradeHistoryModalProps {
    isOpen: boolean;
    onClose: () => void;
    trades: Trade[];
}

export function TradeHistoryModal({ isOpen, onClose, trades }: TradeHistoryModalProps) {
    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="fixed inset-4 md:inset-10 lg:inset-20 bg-gray-800 rounded-lg border border-gray-700 shadow-2xl z-50 overflow-hidden flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-gray-700 flex items-center justify-between bg-gray-800/95 backdrop-blur">
                    <div className="flex items-center space-x-3">
                        <History className="h-6 w-6 text-blue-400" />
                        <h2 className="text-2xl font-bold">Trade History</h2>
                    </div>
                    <div className="flex items-center space-x-4">
                        <div className="text-sm text-gray-400">
                            {trades.length} total trades
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-auto p-6">
                    {trades.length === 0 ? (
                        <div className="h-full flex items-center justify-center text-gray-400">
                            <div className="text-center">
                                <History className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                                <p className="text-lg">No trades found in history</p>
                                <p className="text-sm mt-2">Trades will appear here once executed</p>
                            </div>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-gray-700/50 sticky top-0">
                                    <tr>
                                        <th className="p-3 font-medium text-gray-400">Time</th>
                                        <th className="p-3 font-medium text-gray-400">Symbol</th>
                                        <th className="p-3 font-medium text-gray-400">Type</th>
                                        <th className="p-3 font-medium text-gray-400">Quantity</th>
                                        <th className="p-3 font-medium text-gray-400">Entry Price</th>
                                        <th className="p-3 font-medium text-gray-400">Exit Price</th>
                                        <th className="p-3 font-medium text-gray-400">P&L</th>
                                        <th className="p-3 font-medium text-gray-400">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-700">
                                    {trades.map((trade) => (
                                        <tr key={trade.id} className="hover:bg-gray-700/30 transition-colors">
                                            <td className="p-3 text-gray-300">
                                                <div className="flex flex-col">
                                                    <span className="text-xs text-gray-500">
                                                        {new Date(trade.entry_time).toLocaleDateString()}
                                                    </span>
                                                    <div className="flex items-center space-x-1">
                                                        <Clock className="h-3 w-3 text-gray-500" />
                                                        <span>{new Date(trade.entry_time).toLocaleTimeString()}</span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="p-3 font-medium">{trade.symbol}</td>
                                            <td className="p-3">
                                                <span className={`flex items-center space-x-1 ${trade.action === 'BUY' ? 'text-green-400' : 'text-red-400'
                                                    }`}>
                                                    {trade.action === 'BUY' ? (
                                                        <ArrowUpRight className="h-4 w-4" />
                                                    ) : (
                                                        <ArrowDownLeft className="h-4 w-4" />
                                                    )}
                                                    <span className="font-medium">{trade.action}</span>
                                                </span>
                                            </td>
                                            <td className="p-3 text-gray-300">{trade.quantity.toLocaleString()}</td>
                                            <td className="p-3 text-gray-300 font-mono">{trade.entry_price?.toFixed(5)}</td>
                                            <td className="p-3 text-gray-300 font-mono">
                                                {trade.exit_price ? trade.exit_price.toFixed(5) : '-'}
                                            </td>
                                            <td className={`p-3 font-medium ${(trade.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                                                }`}>
                                                {trade.pnl ? `$${trade.pnl.toFixed(2)}` : '-'}
                                            </td>
                                            <td className="p-3">
                                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${trade.status === 'FILLED' ? 'bg-green-900/50 text-green-400 border border-green-800' :
                                                        trade.status === 'CLOSED' ? 'bg-gray-700 text-gray-300 border border-gray-600' :
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
                    )}
                </div>
            </div>
        </>
    );
}
