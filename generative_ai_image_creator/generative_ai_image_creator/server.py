"""HTTP server exposing the creative studio app and API."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .config import AppConfig
from .creative_engine import LocalCreativeEngine
from .prompt_optimizer import PromptOptimizer
from .repository import CreativeRepository
from .service import CreativeStudioService


def build_service(config: AppConfig) -> CreativeStudioService:
    repository = CreativeRepository(config.db_path)
    engine = LocalCreativeEngine(config.generated_dir)
    optimizer = PromptOptimizer()
    return CreativeStudioService(repository, engine, optimizer)


class CreativeStudioHandler(SimpleHTTPRequestHandler):
    service: CreativeStudioService
    config: AppConfig

    def __init__(self, *args, directory: str | None = None, **kwargs):
        super().__init__(*args, directory=str(self.config.static_dir), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self._json({"status": "ok"})
        if parsed.path == "/api/images":
            use_case = parse_qs(parsed.query).get("use_case", [None])[0]
            return self._json(self.service.list_creatives(use_case=use_case))
        if parsed.path.startswith("/generated/"):
            return self._serve_generated(parsed.path)
        if parsed.path in {"/", "/index.html"}:
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(content_length) or b"{}")
        if parsed.path == "/api/generate":
            return self._json(self.service.generate(payload), status=HTTPStatus.CREATED)
        if parsed.path.startswith("/api/images/") and parsed.path.endswith("/rate"):
            creative_id = int(parsed.path.split("/")[3])
            return self._json(self.service.rate_creative(creative_id, int(payload.get("rating", 0)), bool(payload.get("favorite", False))))
        if parsed.path.startswith("/api/images/") and parsed.path.endswith("/edit"):
            creative_id = int(parsed.path.split("/")[3])
            return self._json(self.service.edit_creative(creative_id, payload), status=HTTPStatus.CREATED)
        return self._json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _serve_generated(self, path: str) -> None:
        relative = path.removeprefix("/generated/")
        target = self.config.generated_dir / relative
        if not target.exists():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "image/svg+xml")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(config: AppConfig) -> ThreadingHTTPServer:
    handler_class = type(
        "ConfiguredCreativeStudioHandler",
        (CreativeStudioHandler,),
        {"service": build_service(config), "config": config},
    )
    httpd = ThreadingHTTPServer((config.host, config.port), handler_class)
    print(f"Marketing Creative Studio running at http://{config.host}:{config.port}")
    return httpd


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Marketing Creative Studio web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    config = AppConfig.default()
    config = AppConfig(
        base_dir=config.base_dir,
        db_path=config.db_path,
        generated_dir=config.generated_dir,
        static_dir=config.static_dir,
        host=args.host,
        port=args.port,
    )
    server = run_server(config)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
