import asyncio
import websockets
import json
from datetime import datetime
from backend.storage import create_connection, create_table, insert_tick

BINANCE_WS_URL = "wss://fstream.binance.com/ws"

async def stream_binance_data(symbols=["btcusdt", "ethusdt"]):
    connection = create_connection()
    if not connection:
        return
    create_table(connection)

    streams = "/".join([f"{s.lower()}@trade" for s in symbols])
    url = f"{BINANCE_WS_URL}/{streams}"
    print(f"Connecting to {url} ...")

    async with websockets.connect(url) as ws:
        print("✅ Connected to Binance WebSocket.\nStreaming live data...\n")
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                tick = {
                    "symbol": data.get("s"),
                    "price": float(data.get("p")),
                    "quantity": float(data.get("q")),
                    "timestamp": datetime.fromtimestamp(data.get("T") / 1000.0)
                }

                print(tick)
                insert_tick(connection, tick)

            except Exception as e:
                print("⚠️ Error:", e)
                break

if __name__ == "__main__":
    try:
        asyncio.run(stream_binance_data(["btcusdt", "ethusdt"]))
    except KeyboardInterrupt:
        print("\n🛑 Stream stopped by user.")
