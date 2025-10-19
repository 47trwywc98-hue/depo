"""Utility to preview the static site via a lightweight HTTP server."""
from __future__ import annotations

import argparse
import contextlib
import http.server
import os
import socket
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

DEFAULT_PORT = 8000


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Start a lightweight HTTP server for local preview and open the site in "
            "your default web browser."
        )
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to bind the preview server (default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open the site in the default browser.",
    )
    return parser.parse_args(argv)


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


class SilentRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        sys.stdout.write("[http] " + (format % args) + "\n")


def start_server(port: int) -> socketserver.TCPServer:
    repo_root = get_repo_root()
    os.chdir(repo_root)
    handler = SilentRequestHandler
    server = socketserver.TCPServer(("", port), handler, bind_and_activate=False)
    with contextlib.suppress(OSError):
        server.allow_reuse_address = True
    server.server_bind()
    server.server_activate()
    return server


def wait_for_port(port: int, timeout: float = 2.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as sock:
            try:
                sock.connect(("127.0.0.1", port))
            except OSError:
                time.sleep(0.05)
            else:
                return True
    return False


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        server = start_server(args.port)
    except OSError as exc:
        sys.stderr.write(f"Sunucu başlatılamadı: {exc}\n")
        return 1

    url = f"http://localhost:{args.port}/index.html"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Önizleme sunucusu {args.port} portunda çalışıyor. Çıkmak için Ctrl+C.")

    if not args.no_open:
        if wait_for_port(args.port):
            print(f"Tarayıcıda açılıyor: {url}")
            webbrowser.open(url, new=2, autoraise=True)
        else:
            print(
                "Sunucu porta bağlanamadı. Lütfen tarayıcınızda adresi elle açın: "
                + url
            )

    try:
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
