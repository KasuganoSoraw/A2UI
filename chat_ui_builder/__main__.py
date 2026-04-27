from __future__ import annotations

import os
import sys

import uvicorn

CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
  sys.path.insert(0, CURRENT_DIR)

from app import app
from settings import settings


def main() -> None:
  uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
  main()
