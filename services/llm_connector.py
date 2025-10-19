import asyncio
import logging
import time
from collections import deque

import httpx
from config import LLM_RATE_LIMIT

logging.basicConfig(
    filename="backend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

llm_queue = asyncio.Queue()
llm_request_timestamps = deque()


async def llm_worker():
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            func, args, kwargs, future = await llm_queue.get()
            now = time.time()

            while len(llm_request_timestamps) >= LLM_RATE_LIMIT and now - llm_request_timestamps[0] < 60:
                logging.warning("Rate limit reached.")
                await asyncio.sleep(1)
                now = time.time()

            while llm_request_timestamps and now - llm_request_timestamps[0] >= 60:
                llm_request_timestamps.popleft()

            llm_request_timestamps.append(now)

            try:
                logging.info("Sending request to the LLM.")
                result = await func(client, *args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                llm_queue.task_done()


async def start_llm_worker():
    asyncio.create_task(llm_worker())


async def send_llm_request(url: str, payload: dict):
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    await llm_queue.put((_send_request, (url, payload), {}, future))
    return await future


async def _send_request(client, url, payload):
    response = await client.post(url, json=payload)
    response.raise_for_status()
    return response.json()
