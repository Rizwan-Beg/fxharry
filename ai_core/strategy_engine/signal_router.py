# ai_core/strategy_engine/signal_router.py

class SignalRouter:
    def __init__(self, ws_broadcaster):
        self.ws_broadcaster = ws_broadcaster

    def broadcast_signals(self, signals):
        if not signals:
            return

        payload = {
            "type": "signal_update",
            "data": signals
        }

        self.ws_broadcaster(payload)
