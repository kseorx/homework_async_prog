"""
Задание 1. Синхронно vs асинхронно

Объяснение разницы:
Синхронный код блокирует поток на время каждого сетевого запроса (I/O-bound), 
заставляя процессор простаивать. Асинхронный код (asyncio) использует event loop, 
который переключается на другие задачи в моменты ожидания ответа от сети, 
позволяя скачивать все картинки конкурентно в рамках одного потока.

Время выполнения (вставьте ваше значение):
- sync_main (requests): [20.69s]
- fast_main (httpx + asyncio): [0.79s]
"""

import asyncio
import time
import httpx
import requests

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]

def timed(label, fn, *args):
    start = time.perf_counter()
    fn(*args)
    print(f"\n{label}: {time.perf_counter() - start:.2f}s")

def sync_main():
    for url in URLS:
        requests.get(url)

async def fetch_async(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url)
    return resp.status_code

async def fast_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [fetch_async(client, url) for url in URLS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    timed("sync_main", sync_main)
    timed("fast_main", lambda: asyncio.run(fast_main()))