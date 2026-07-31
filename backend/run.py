import os

import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server


def main() -> None:
    os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "__all__")
    config = Config("app.main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
    server = Server(config)
    server.run()


if __name__ == "__main__":
    main()
