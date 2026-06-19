import { useState, useEffect, useRef } from 'react';
import { X, Code, Save, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { createWS } from '../services/ws';

interface StrategyCodeModalProps {
    isOpen: boolean;
    onClose: () => void;
    strategyId: string;
    strategyName: string;
}

export function StrategyCodeModal({ isOpen, onClose, strategyId, strategyName }: StrategyCodeModalProps) {
    const [code, setCode] = useState('');
    const [originalCode, setOriginalCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const wsRef = useRef<any>(null);

    useEffect(() => {
        if (isOpen && strategyId) {
            // Create a new WS connection for code fetching
            const ws = createWS();
            wsRef.current = ws;

            // Listen for strategy code response
            ws.on('strategy_code', (data: any) => {
                setLoading(false);
                if (data.error) {
                    setError(data.error);
                } else {
                    setCode(data.code || '');
                    setOriginalCode(data.code || '');
                    setError('');
                }
            });

            // Listen for save response
            ws.on('strategy_code_update', (data: any) => {
                setSaving(false);
                if (data.success) {
                    setSuccessMsg(data.message || 'Strategy saved successfully!');
                    setOriginalCode(code);
                    setIsEditing(false);
                    // Clear success message after 3s
                    setTimeout(() => setSuccessMsg(''), 3000);
                } else {
                    setError(data.error || 'Failed to save strategy code');
                }
            });

            // Request code when WS is ready
            const originalOnOpen = ws.ws.onopen;
            ws.ws.onopen = (ev: Event) => {
                if (originalOnOpen) (originalOnOpen as any)(ev);
                fetchStrategyCode(ws);
            };

            // If already connected, fetch immediately
            if (ws.ws.readyState === WebSocket.OPEN) {
                fetchStrategyCode(ws);
            }

            return () => {
                ws.ws.close();
                wsRef.current = null;
            };
        }
    }, [isOpen, strategyId]);

    const fetchStrategyCode = (ws: any) => {
        setLoading(true);
        setError('');
        setSuccessMsg('');
        ws.send('strategy_code_command', {
            command: 'GET_STRATEGY_CODE',
            strategy_id: strategyId,
        });
    };

    const handleSave = () => {
        if (!wsRef.current) return;
        setSaving(true);
        setError('');
        setSuccessMsg('');
        wsRef.current.send('strategy_code_command', {
            command: 'UPDATE_STRATEGY_CODE',
            strategy_id: strategyId,
            code: code,
        });
    };

    const handleCancelEdit = () => {
        setCode(originalCode);
        setIsEditing(false);
        setError('');
    };

    const hasChanges = code !== originalCode;

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black bg-opacity-70"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] mx-4 flex flex-col border border-gray-700">

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-700">
                    <div className="flex items-center space-x-3">
                        <Code className="h-6 w-6 text-blue-400" />
                        <div>
                            <h2 className="text-xl font-bold">{strategyName} - Code</h2>
                            <p className="text-sm text-gray-400">Strategy ID: {strategyId}</p>
                        </div>
                    </div>

                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <X className="h-6 w-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <Loader className="h-6 w-6 text-blue-400 animate-spin mr-2" />
                            <div className="text-gray-400">Loading strategy code...</div>
                        </div>
                    ) : (
                        <>
                            {/* Success banner */}
                            {successMsg && (
                                <div className="mb-4 p-3 bg-green-900/20 border border-green-700 rounded-lg flex items-center space-x-2">
                                    <CheckCircle className="h-5 w-5 text-green-400" />
                                    <span className="text-green-400 text-sm">{successMsg}</span>
                                </div>
                            )}

                            {/* Error banner */}
                            {error && (
                                <div className="mb-4 p-3 bg-red-900/20 border border-red-700 rounded-lg flex items-center space-x-2">
                                    <AlertCircle className="h-5 w-5 text-red-400" />
                                    <span className="text-red-400 text-sm">{error}</span>
                                </div>
                            )}

                            {/* Code editor */}
                            <div className="relative">
                                <textarea
                                    value={code}
                                    onChange={(e) => isEditing && setCode(e.target.value)}
                                    readOnly={!isEditing}
                                    className={`w-full h-96 p-4 bg-gray-900 border rounded-lg font-mono text-sm text-gray-300 focus:outline-none resize-y ${isEditing
                                            ? 'border-blue-500 bg-gray-950'
                                            : 'border-gray-600 cursor-default'
                                        }`}
                                    placeholder="Strategy code will appear here..."
                                    spellCheck={false}
                                />
                                {hasChanges && isEditing && (
                                    <div className="absolute top-2 right-2 px-2 py-1 bg-yellow-600/80 text-xs rounded text-white">
                                        Unsaved changes
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-6 border-t border-gray-700">
                    <div className="text-sm text-gray-400">
                        {isEditing ? '✏️ Editing mode' : '👁️ Read-only mode'}
                    </div>

                    <div className="flex space-x-3">
                        {isEditing ? (
                            <>
                                <button
                                    onClick={handleCancelEdit}
                                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSave}
                                    disabled={saving || !hasChanges}
                                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors text-sm ${saving || !hasChanges
                                            ? 'bg-blue-800 opacity-50 cursor-not-allowed'
                                            : 'bg-blue-600 hover:bg-blue-700'
                                        }`}
                                >
                                    {saving ? (
                                        <Loader className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <Save className="h-4 w-4" />
                                    )}
                                    <span>{saving ? 'Saving...' : 'Save & Reload'}</span>
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setIsEditing(true)}
                                disabled={loading}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-sm"
                            >
                                Enable Editing
                            </button>
                        )}

                        <button
                            onClick={onClose}
                            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
                        >
                            Close
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
