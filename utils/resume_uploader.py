from __future__ import annotations
from pathlib import Path
import shutil
import time
from urllib.parse import urlparse, unquote
import requests

DEFAULT_BASE_DIR = Path(__file__).resolve().parent
RETRIES = 3
BACKOFF = 1  # seconds


def get_filename(url: str, response: requests.Response) -> str:
    """Helper to extract a clean filename from a URL or response headers."""
    cd = response.headers.get("content-disposition", "")
    for part in cd.split(";"):
        part = part.strip()
        if "filename=" in part.lower():
            return part.split("=")[1].strip('"')
            
    parsed_url = urlparse(url)
    return unquote(Path(parsed_url.path).name) or "resume"


def upload_resume(id: str, url: str, base_dir: Path | str = DEFAULT_BASE_DIR, timeout: int = 30) -> str:
    """Download or copy file from `url` into `base_dir/<id>/` and return its absolute path."""
    if not id or not url:
        raise ValueError("Both 'id' and 'url' must be provided")

    # FIX: Safely convert base_dir to a Path object whether main.py passes a string or a Path object
    base_path = Path(base_dir)
    dest_dir = base_path / str(id)
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Identify if it's a local file or an HTTP link
    is_local = url.startswith("file://") or Path(url).exists()
    src_path = Path(urlparse(url).path if url.startswith("file://") else url)

    for attempt in range(1, RETRIES + 1):
        try:
            if is_local:
                if not src_path.is_file():
                    raise ValueError(f"Local path is not a valid file: {src_path}")
                filename = unquote(src_path.name) or "resume"
                dest_path = dest_dir / filename
                
                shutil.copy2(src_path, dest_path)
            else:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                
                filename = get_filename(url, response)
                dest_path = dest_dir / filename
                
                dest_path.write_bytes(response.content)

            return str(dest_path.resolve())

        except (requests.RequestException, OSError):
            if attempt == RETRIES:
                raise
            time.sleep(BACKOFF * (2 ** (attempt - 1)))