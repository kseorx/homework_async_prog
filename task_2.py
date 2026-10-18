"""
Задание 2. Реальный I/O и обработка ошибок

Объяснение:
Таймаут (timeout=5.0) необходим, чтобы зависший сервер не заблокировал 
весь event loop навечно. Экспоненциальный backoff (1с -> 2с -> 4с) дает 
серверу время на восстановление и предотвращает шторм запросов. 
Обертка safe_fetch и return_exceptions=True в gather гарантируют, что 
ошибка на одном URL не прервет скачивание остальных.

Время выполнения: [19.97s]g
"""

import asyncio
import time
import httpx

URLS = [f"https://picsum.photos/seed/{i}/800/600" for i in range(20)]
# Битые адреса для проверки
URLS.extend([
    "https://no-such-site.invalid", 
    "https://httpbin.org/delay/10"
])

def timed(label, fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    print(f"\n{label}: {time.perf_counter() - start:.2f}s")
    return result

async def robust_fetch(client: httpx.AsyncClient, url: str) -> int:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Таймаут на каждый запрос
            resp = await client.get(url, timeout=5.0)
            resp.raise_for_status()
            return resp.status_code
        except (httpx.HTTPError, asyncio.TimeoutError, httpx.ConnectError) as e:
            if attempt == max_retries - 1:
                raise e
            # Экспоненциальный backoff: 2^0=1, 2^1=2, 2^2=4
            backoff = 2 ** attempt
            await asyncio.sleep(backoff)

async def safe_fetch(client: httpx.AsyncClient, url: str):
    """Обертка, чтобы перехватывать ошибки и не ронять gather."""
    try:
        return await robust_fetch(client, url)
    except Exception as e:
        return e

async def robust_main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = [safe_fetch(client, url) for url in URLS]
        raw_results = await asyncio.gather(*tasks)
        
        results = []
        errors = []
        for url, res in zip(URLS, raw_results):
            if isinstance(res, Exception):
                errors.append((url, type(res).__name__))
            else:
                results.append((url, res))
                
        return results, errors

def run_robust():
    results, errors = asyncio.run(robust_main())
    print(f"Успешно скачано: {len(results)}")
    print(f"Ошибок: {len(errors)}")
    for url, err in errors:
        print(f"  - {url}: {err}")

if __name__ == "__main__":
    timed("robust_main", run_robust)