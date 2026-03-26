import threading
import os
import time
import logging

from pathlib import Path

from app.services.summarization_service import SummarizationService
from app.core.job_queue import job_queue, job_results, cleanup_jobs
from app.core.config import TEMP_DIR
from app.utils.file_utils import save_temp_file


logger = logging.getLogger("yegi.worker")

last_cleanup = 0

def worker():
    global last_cleanup

def cleanup_temp_files(ttl=3600):
    now = time.time()

    for file in Path(TEMP_DIR).glob("*.pdf"):
        if now - file.stat().st_mtime > ttl:
            try:
                file.unlink()
            except:
                pass

def worker():
    global last_cleanup
    service = SummarizationService()

    while True:
        job_id, data = job_queue.get()

        if job_id not in job_results:
            job_results[job_id] = {}

        job_results[job_id]["status"] = "processing"
        job_results[job_id]["started_at"] = time.time()
        logger.info(f"Processing job {job_id}")

        try:
            result = service.summarize(**data)

            job_results[job_id].update({
                "status": "completed",
                "result": result,
                "finished_at": time.time()
            })
            logger.info(f"Job completed {job_id}")

        except Exception as e:
            job_results[job_id].update({
                "status": "failed",
                "error": str(e),
                "finished_at": time.time()
            })
            logger.error(f"Job failed {job_id} | error={str(e)}")

        finally:
            try:
                if os.path.exists(data["file_path"]):
                    os.remove(data["file_path"])
            except Exception as e:
                print(f"Error deleting temp file: {e}")

            job_queue.task_done()

            now = time.time()
            if now - last_cleanup > 10:
                cleanup_jobs()
                cleanup_temp_files()
                last_cleanup = now


for _ in range(3):
    threading.Thread(target=worker, daemon=True).start()