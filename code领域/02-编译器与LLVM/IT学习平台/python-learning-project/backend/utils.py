import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class InMemoryCache:
    
    def __init__(self):
        self.cache: Dict[str, tuple] = {}
    
    def set(self, key: str, value: any, ttl: Optional[int] = None):
        expiry = None
        if ttl:
            expiry = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expiry)
    
    def get(self, key: str) -> Optional[any]:
        if key not in self.cache:
            return None
        
        value, expiry = self.cache[key]
        if expiry and datetime.now() > expiry:
            del self.cache[key]
            return None
        
        return value
    
    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        self.cache.clear()


class AsyncWorker:
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks: List[asyncio.Task] = []
    
    async def run_task(self, coro):
        async with self.semaphore:
            return await coro
    
    async def add_task(self, coro):
        task = asyncio.create_task(self.run_task(coro))
        self.tasks.append(task)
    
    async def wait_all(self):
        await asyncio.gather(*self.tasks)
        self.tasks.clear()


class RateLimiter:
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[datetime]] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        now = datetime.now()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < timedelta(seconds=self.time_window)
        ]
        
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        self.requests[identifier].append(now)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        if identifier not in self.requests:
            return self.max_requests
        
        now = datetime.now()
        valid_requests = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < timedelta(seconds=self.time_window)
        ]
        
        return max(0, self.max_requests - len(valid_requests))


class TaskQueue:
    
    def __init__(self):
        self.queue: List[Dict] = []
        self.completed: List[Dict] = []
    
    def add_task(self, task_id: str, task_data: Dict):
        self.queue.append({
            'id': task_id,
            'data': task_data,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        })
    
    def get_next_task(self) -> Optional[Dict]:
        if not self.queue:
            return None
        
        task = self.queue.pop(0)
        task['status'] = 'processing'
        task['started_at'] = datetime.now().isoformat()
        return task
    
    def complete_task(self, task_id: str, result: Dict):
        for task in self.queue + self.completed:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['result'] = result
                task['completed_at'] = datetime.now().isoformat()
                if task in self.queue:
                    self.queue.remove(task)
                    self.completed.append(task)
                return task
        return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        for task in self.queue + self.completed:
            if task['id'] == task_id:
                return task
        return None
    
    def get_all_tasks(self) -> Dict:
        return {
            'pending': [t for t in self.queue if t['status'] == 'pending'],
            'processing': [t for t in self.queue if t['status'] == 'processing'],
            'completed': self.completed
        }