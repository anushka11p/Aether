import asyncio
import json
import sys
import websockets

async def test(task: str):
    uri = "ws://127.0.0.1:8000/ws/run"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"task": task}))
        while True:
            message = await ws.recv()
            data = json.loads(message)
            print(data)
            if data.get("type") == "done":
                break

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "Explain why vector databases matter for AI agent memory, in 3 short paragraphs."
    asyncio.run(test(task))