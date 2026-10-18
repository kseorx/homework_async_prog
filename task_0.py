"""
Задание 0. Разминка-ловушка «Почему не быстрее?»

Объяснение:
В функции slow_main используется цикл for с последовательным await. 
Ключевое слово await означает "дождись результата здесь и сейчас". 
Поэтому, несмотря на использование async/await, запросы выполняются строго 
по очереди: следующий не стартует, пока не закончится предыдущий. 
Event loop не может переключаться между задачами, так как они не запущены 
параллельно (конкурентно).

Починка:
Чтобы запросы пошли одновременно, нужно передать их в event loop как 
отдельные задачи с помощью asyncio.gather() или asyncio.TaskGroup().

Время выполнения (вставьте ваше значение после запуска):
- slow_main (последовательный): [4.96s]
- fast_main (конкурентный): [0.72s]
"""

import asyncio
import time
import httpx

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]

def timed(label, fn, *args):
    start = time.perf_counter()
    fn(*args)
    print(f"\n{label}: {time.perf_counter() - start:.2f}s")

async def fetch(client: httpx.AsyncClient, url: str) -> int:
    resp = await client.get(url)
    return resp.status_code

async def slow_main():
    # ЛОВУШКА: await в цикле выполняет запросы ПОСЛЕДОВАТЕЛЬНО
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in URLS:
            await fetch(client, url)

async def fast_main():
    # ПОЧИНКА: запускаем все задачи конкурентно через gather
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [fetch(client, url) for url in URLS]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    timed("slow_main", lambda: asyncio.run(slow_main()))
    timed("fast_main", lambda: asyncio.run(fast_main()))