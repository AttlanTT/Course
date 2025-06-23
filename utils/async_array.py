import asyncio

async def async_map(array, func, delay=0):
    results = []
    for item in array:
        await asyncio.sleep(delay)
        results.append(await func(item))
    return results

async def async_filter(array, func, delay=0):
    results = []
    for item in array:
        await asyncio.sleep(delay)
        if await func(item):
            results.append(item)
    return results

async def run_with_abort(coro, timeout):
    try:
        return await asyncio.wait_for(coro, timeout)
    except asyncio.TimeoutError:
        print("⚠️ Aborted due to timeout")
        return None
