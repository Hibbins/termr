import subprocess
import signal
import time
import threading
from typing import Optional
from .models import RadioStation, PlaybackStatus
import socket
import re
import requests
import ssl
import urllib.parse
import string


class VLCPlayer:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.current_station: Optional[RadioStation] = None
        self.status = PlaybackStatus()
        self.volume = 100
        self.app = None
        self._metadata_thread = None
        self._stop_metadata = threading.Event()
        self._icy_thread = None
        self._stop_icy = threading.Event()

    def set_app(self, app):
        self.app = app

    def _check_vlc_available(self) -> bool:
        try:
            result = subprocess.run(
                ["cvlc", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def play(self, station: RadioStation, volume: int = None) -> bool:
        if not self._check_vlc_available():
            if self.app:
                self.app.notify("VLC (cvlc) is not available", severity="error")
            return False

        self.stop()
        self._stop_metadata.set()
        self._stop_metadata = threading.Event()

        if volume is not None:
            self.volume = volume

        try:
            self.process = subprocess.Popen(
                [
                    "cvlc",
                    station.url,
                    "--intf", "rc",
                    "--no-video",
                    "--no-metadata-network-access",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
                text=True
            )
            time.sleep(0.2)
            if self.process.poll() is not None:
                msg = f"VLC process exited early with code {self.process.returncode}"
                print(f"DEBUG: {msg}")
                err = self.process.stderr.read() if self.process.stderr else ""
                print(f"DEBUG: VLC stderr: {err}")
                self.current_station = None
                self.status.station = None
                self.status.is_playing = False
                return False
            if self.process.stdin:
                self.process.stdin.write("info\n")
                self.process.stdin.flush()
            self.set_volume(self.volume)
            self.current_station = station
            self.status.station = station
            self.status.is_playing = True
            self.status.is_paused = False
            self.status.current_time = 0.0
            self._metadata_thread = threading.Thread(target=self._read_metadata, daemon=True)
            self._metadata_thread.start()
            if hasattr(self, '_stop_icy') and isinstance(self._stop_icy, threading.Event):
                self._stop_icy.clear()
            else:
                self._stop_icy = threading.Event()
            self._icy_thread = threading.Thread(target=self._read_icy_metadata, args=(station.url,), daemon=True)
            self._icy_thread.start()
            return True
        except (subprocess.SubprocessError, OSError) as e:
            self.current_station = None
            self.status.station = None
            self.status.is_playing = False
            return False

    def _read_metadata(self):
        if not self.process or not self.process.stdout:
            return
        while not self._stop_metadata.is_set():
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                if "title:" in line.lower() or "now playing" in line.lower():
                    meta = line.strip().replace("title:", "").replace("now playing:", "").strip()
                    if self.app:
                        self.app.set_metadata(meta, self.current_station.id if self.current_station else None)
            except Exception:
                break

    def _read_icy_metadata(self, url):
        stream_socket = None
        try:
            meta_last = None
            if url.endswith('.m3u') or url.endswith('.pls'):
                try:
                    resp = requests.get(url, timeout=10)
                    resp.raise_for_status()
                    lines = resp.text.splitlines()
                    if not lines:
                        return
                    stream_url = None
                    if url.endswith('.m3u'):
                        for line in lines:
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            stream_url = line
                            break
                    elif url.endswith('.pls'):
                        for line in lines:
                            if line.lower().startswith('file') and '=' in line:
                                stream_url = line.split('=', 1)[1].strip()
                                break
                    if stream_url:
                        url = stream_url
                        if url.endswith('.m3u') or url.endswith('.pls'):
                            return
                    else:
                        return
                except Exception:
                    return
            parsed = urllib.parse.urlparse(url)
            scheme = parsed.scheme or "http"
            host = parsed.hostname
            port = parsed.port or (443 if scheme == "https" else 80)
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            stream_socket.settimeout(10)
            if scheme == "https":
                context = ssl.create_default_context()
                stream_socket = context.wrap_socket(stream_socket, server_hostname=host)
            stream_socket.connect((host, port))
            req = (
                f"GET {path} HTTP/1.0\r\n"
                f"Host: {host}\r\n"
                f"Icy-MetaData: 1\r\n"
                f"Connection: close\r\n\r\n"
            )
            stream_socket.sendall(req.encode("utf-8"))
            headers = b""
            while b"\r\n\r\n" not in headers:
                headers += stream_socket.recv(1)
            headers_decoded = headers.decode("utf-8", errors="ignore")
            metaint = 0
            for line in headers_decoded.splitlines():
                if line.lower().startswith("icy-metaint:"):
                    metaint = int(line.split(":")[1].strip())
                    break
            if not metaint:
                return
            while not self._stop_icy.is_set():
                _ = stream_socket.recv(metaint)
                meta_len_byte = stream_socket.recv(1)
                if not meta_len_byte:
                    break
                meta_len = meta_len_byte[0] * 16
                if meta_len == 0:
                    continue
                meta = stream_socket.recv(meta_len).decode("utf-8", errors="ignore")
                m = re.search(r"StreamTitle='([^']*)';", meta)
                if m:
                    title = m.group(1)
                    title_safe = ''.join(c if c in string.printable else '?' for c in title)
                    if title_safe and title_safe != meta_last:
                        meta_last = title_safe
                        if self.app:
                            self.app.set_metadata(title_safe, self.current_station.id if self.current_station else None)
        except Exception:
            pass
        finally:
            if stream_socket:
                try:
                    stream_socket.close()
                except Exception:
                    pass

    def stop(self) -> None:
        self._stop_metadata.set()
        if hasattr(self, '_stop_icy'):
            self._stop_icy.set()
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
        self.current_station = None
        self.status.station = None
        self.status.is_playing = False
        self.status.is_paused = False
        self.status.current_time = 0.0

    def pause(self) -> bool:
        if not self.process or not self.status.is_playing:
            return False

        try:
            self.process.send_signal(signal.SIGSTOP)
            self.status.is_paused = True
            return True
        except (OSError, ProcessLookupError):
            return False

    def resume(self) -> bool:
        if not self.process or not self.status.is_paused:
            return False

        try:
            self.process.send_signal(signal.SIGCONT)
            self.status.is_paused = False
            return True
        except (OSError, ProcessLookupError):
            return False

    def toggle_pause(self) -> bool:
        if self.status.is_paused:
            return self.resume()
        else:
            return self.pause()

    def is_playing(self) -> bool:
        if not self.process:
            return False
        
        return self.process.poll() is None and self.status.is_playing

    def get_status(self) -> PlaybackStatus:
        if self.process and self.process.poll() is not None:
            self.status.is_playing = False
            self.status.is_paused = False
            self.current_station = None
            self.status.station = None
        
        return self.status

    def get_current_station(self) -> Optional[RadioStation]:
        return self.current_station 

    def set_volume(self, volume: int) -> None:
        self.volume = volume
        if self.process and self.process.poll() is None:
            try:
                if self.process.stdin:
                    self.process.stdin.write(f"volume {self.volume}\n")
                    self.process.stdin.flush()
            except Exception as e:
                print(f"Exception in set_volume: {e}")
