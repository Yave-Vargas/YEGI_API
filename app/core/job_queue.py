import uuid
from queue import Queue
import time

job_queue = Queue()
job_results = {}

def create_job(data):
    job_id = str(uuid.uuid4())
    job_queue.put((job_id, data))
    job_results[job_id] = {
        "status": "pending",
        "created_at": time.time()
    }
    return job_id

def get_job_result(job_id):
    return job_results.get(job_id, {"status": "not_found"})

def cleanup_jobs(ttl=3600):
    now = time.time()
    to_delete = [
        job_id for job_id, job in job_results.items()
        if now - job.get("created_at", now) > ttl
    ]
    for job_id in to_delete:
        del job_results[job_id]