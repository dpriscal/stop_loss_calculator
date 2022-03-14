import os
import sys

import pytest
from starlette.testclient import TestClient

sys.path.insert(0, "/stop_loss_calculator")

from app.main import api


@pytest.fixture(scope="function")
def testclient():
    with TestClient(api) as client:
        # Application 'startup' handlers are called on entering the block.
        yield client
    # Application 'shutdown' handlers are called on exiting the block.
