import pytest
from starlette import status
from starlette.testclient import TestClient

from app import main
from app.application.dtos.events import ResponseEventDTO


@pytest.mark.integration
async def test_update_events_integration(docker_dependencies):
    with TestClient(main.app) as client:
        response = client.get("/search", params={"starts_at": "2021-01-01T00:00:00Z", "ends_at": "2022-01-02T00:00:00"})
        assert response.status_code == status.HTTP_200_OK
        response = ResponseEventDTO.model_validate(response.json())
        assert len(response.data.events) == 3
        assert response.error is None
        assert all(
            event.id in {"1591", "322", "291"} for event in response.data.events
        ), f"Not found 1591, 322, 291 in {response.data.events}"
