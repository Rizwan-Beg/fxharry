import asyncio
from concurrent import futures
from typing import AsyncIterator, List

import grpc

# Generated modules should be produced via: 
# python -m grpc_tools.protoc -I shared/proto --python_out=ai_core --grpc_python_out=ai_core shared/proto/ai_service.proto
try:
    from ai_core import ai_service_pb2 as pb2
    from ai_core import ai_service_pb2_grpc as pb2_grpc
except ImportError:
    pb2 = None
    pb2_grpc = None

from .core.logger import get_logger
from .core.config import settings
from .database.database import SessionLocal
from .database.models import Strategy
from .strategy_engine.rule_based import StrategyManager
from .strategy_engine.market_data.market_data_service import MarketDataService

logger = get_logger(__name__)


class AICoreService(pb2_grpc.AICoreServiceServicer if pb2_grpc else object):
    def __init__(self):
        self.strategy_manager = StrategyManager()
        self.market_data_service = MarketDataService()

    async def GetAccountSummary(self, request, context):  # type: ignore
        # Placeholder account summary
        return pb2.AccountSummary(
            status="ok",
            timestamp=asyncio.get_running_loop().time().__str__(),
            broker="IBKR",
            total_equity=100000.0,
            available_funds=80000.0,
            buying_power=200000.0,
        )

    async def GetPositions(self, request, context):  # type: ignore
        return pb2.Positions(positions=[])

    async def StreamMarketData(self, request, context):  # type: ignore
        symbols: List[str] = list(request.symbols)
        while True:
            data = await self.market_data_service.get_live_forex_data(symbols)
            for sym in symbols:
                md = data.get(sym)
                if md:
                    yield pb2.MarketDataUpdate(
                        symbol=sym,
                        bid=float(md["bid"]),
                        ask=float(md["ask"]),
                        last=float(md["last"]),
                        timestamp=str(md["timestamp"]),
                    )
            await asyncio.sleep(1)

    async def GenerateAISignal(self, request, context):  # type: ignore
        # Simple placeholder generating HOLD signals
        return pb2.AISignal(
            symbol=(request.symbols[0] if request.symbols else "EURUSD"),
            signal_type="HOLD",
            confidence=0.0,
            timestamp=str(asyncio.get_running_loop().time()),
        )


async def serve_async() -> None:
    if pb2_grpc is None:
        logger.error(
            "gRPC Python stubs not found. Generate with grpc_tools.protoc for ai_service.proto"
        )
        return

    server = grpc.aio.server()
    pb2_grpc.add_AICoreServiceServicer_to_server(AICoreService(), server)
    listen_addr = f"0.0.0.0:{settings.grpc_port}"
    server.add_insecure_port(listen_addr)
    logger.info(f"Starting AICore gRPC server on {listen_addr}")
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        await server.stop(0)


if __name__ == "__main__":
    asyncio.run(serve_async())