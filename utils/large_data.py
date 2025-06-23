import asyncio

async def data_stream(n):
    for i in range(n):
        await asyncio.sleep(0.01)
        yield i

async def process_stream(stream):
    total = 0
    async for value in stream:
        print(f"Processing: {value}")
        total += value
    print(f"✅ Total: {total}")
