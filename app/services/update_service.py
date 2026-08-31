import json
import re
import urllib.request
from PySide6.QtCore import QThread, Signal, QObject

APP_VERSION = "v1.4.0"
GITHUB_REPO = "candy-blue/comic-utils"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"

def parse_version(ver_str):
    """ Parse semantic version like 'v1.3.2' or '1.3.2' into tuple (1, 3, 2) """
    if not ver_str:
        return (0, 0, 0)
    ver_clean = re.sub(r'^[^\d]*', '', ver_str)
    parts = []
    for part in ver_clean.split('.'):
        num = ''
        for ch in part:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

class UpdateCheckWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def run(self):
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(api_url, headers={"User-Agent": "ComicUtils-App"})
            latest_tag = None
            release_notes = ""
            release_url = f"{GITHUB_URL}/releases/latest"
            download_url = None

            try:
                with urllib.request.urlopen(req, timeout=6) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    latest_tag = data.get("tag_name", "")
                    release_notes = data.get("body", "")
                    release_url = data.get("html_url", release_url)
                    assets = data.get("assets", [])
                    for asset in assets:
                        if asset.get("name", "").endswith(".exe"):
                            download_url = asset.get("browser_download_url")
                            break
            except Exception:
                # Fallback to redirect extraction if GitHub API is rate limited
                redir_url = f"{GITHUB_URL}/releases/latest"
                redir_req = urllib.request.Request(redir_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(redir_req, timeout=6) as response:
                    final_url = response.geturl()
                    latest_tag = final_url.split("/")[-1]
                    release_url = final_url

            if not latest_tag:
                self.error.emit("无法获取最新版本信息")
                return

            current_tuple = parse_version(APP_VERSION)
            latest_tuple = parse_version(latest_tag)
            has_update = latest_tuple > current_tuple

            if not download_url:
                download_url = f"{GITHUB_URL}/releases/download/{latest_tag}/ComicUtils.exe"

            result = {
                "has_update": has_update,
                "current_version": APP_VERSION,
                "latest_version": latest_tag,
                "release_url": release_url,
                "download_url": download_url,
                "release_notes": release_notes or "常规更新与体验优化。"
            }
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class UpdateDownloadWorker(QThread):
    progress = Signal(int, int, int) # current, total, percent
    finished = Signal(str) # file_path
    error = Signal(str)

    def __init__(self, download_url, save_path):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def run(self):
        try:
            req = urllib.request.Request(self.download_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as response:
                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 64 * 1024
                
                with open(self.save_path, "wb") as f:
                    while not self.is_cancelled:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = int((downloaded / total_size) * 100) if total_size > 0 else 0
                        self.progress.emit(downloaded, total_size, percent)

            if self.is_cancelled:
                self.error.emit("下载已取消")
            else:
                self.finished.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))
