"""
Задание 3 (*). Вынос CPU-bound-вычислений

Объяснение:
Функция heavy (sha256) нагружает процессор (CPU-bound). Если вызвать её 
напрямую в корутине, она не уступает управление event loop, и ticker 
(печатающий точки) замирает — loop заблокирован. 
Решение: вынести тяжелые вычисления в отдельный процесс через 
loop.run_in_executor и ProcessPoolExecutor. Это освобождает GIL и event loop, 
позволяя ticker'у продолжать работать.

Время выполнения: cpu_main: [3.13s]
"""

import asyncio
import time
import hashlib
import httpx
from concurrent.futures import ProcessPoolExecutor

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(5)] # 5 картинок для наглядности

def timed(label, fn, *args):
    start = time.perf_counter()
    fn(*args)
    print(f"\n{label}: {time.perf_counter() - start:.2f}s")

def heavy(body: bytes) -> str:
    return hashlib.sha256(body * 1000).hexdigest()

async def ticker():
    while True:
        print(".", end="", flush=True)
        await asyncio.sleep(0.1)

async def cpu_main():
    tick_task = asyncio.create_task(ticker())
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Скачиваем картинки
        resps = await asyncio.gather(*[client.get(url) for url in URLS])
        bodies = [r.content for r in resps]
        
        # 1. Запуск «в лоб» (точки должны замереть)
        print("\n--- Запуск «в лоб» (event loop заблокирован) ---\n")
        for body in bodies:
            heavy(body)
            
        # 2. Запуск через ProcessPoolExecutor (точки снова бегут)
        print("\n--- Запуск через ProcessPoolExecutor (event loop свободен) ---\n")
        loop = asyncio.get_running_loop()
        with ProcessPoolExecutor() as pool:
            tasks = [loop.run_in_executor(pool, heavy, body) for body in bodies]
            await asyncio.gather(*tasks)
            
    tick_task.cancel()
    try:
        await tick_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    timed("cpu_main", lambda: asyncio.run(cpu_main()))