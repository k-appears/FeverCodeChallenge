from datetime import datetime

import httpx
import pybreaker
import pytest
import tenacity
from httpx import Response
from starlette import status

from app.domain.entities.provider_a.provider_a import (
    ProviderABaseEvent,
    ProviderAEvent,
    ProviderAZone,
)
from app.infrastructure.api.external_providers.provider_a import ProviderA

URL = "https://example.org/"


async def test_parse_events_no_url():
    with pytest.raises(ValueError) as exec_info:
        provider = ProviderA(provider_url="")
        await provider.parse("")
    assert str(exec_info.value) == "'conf.url' is not set or is empty in config.yml file"


async def test_parse_events_no_events():
    with pytest.raises(ValueError) as exec_info:
        provider = ProviderA(provider_url="http://localhost")
        await provider.parse("")
    assert str(exec_info.value) == "Response string is empty"


async def test_parse_invalid_xml():
    provider = ProviderA(provider_url="http://localhost")
    with pytest.raises(ValueError) as exec_info:
        await provider.parse("<invalid>xml</invalid>")
    assert str(exec_info.value) == "XML Parsing Error: root element not found (actual: invalid, expected: eventList)"


async def test_parse_invalid_fields():
    provider = ProviderA(provider_url="http://localhost")
    xml = """<?xml version="1.0" encoding="utf-8"?>
    <eventList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="1.0" xsi:noNamespaceSchemaLocation="eventList.xsd">
        <output>
          <base_event>
          </base_event>
        </output>
    </eventList>
    """
    with pytest.raises(ValueError) as exec_info:
        await provider.parse(xml)
    assert "4 validation errors for EventList" in str(exec_info.value)
    assert "output.base_events.0.base_event_id" in str(exec_info.value)
    assert "output.base_events.0.sell_mode" in str(exec_info.value)
    assert "output.base_events.0.title" in str(exec_info.value)
    assert "output.base_events.0.events" in str(exec_info.value)


async def test_parse_valid_events():
    xml = """<?xml version="1.0" encoding="utf-8"?>
    <eventList xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0"
    xsi:noNamespaceSchemaLocation="eventList.xsd">
       <output>
          <base_event base_event_id="291" sell_mode="online" title="Camela en concierto">
              <event event_start_date="2021-06-30T21:00:00" event_end_date="2021-06-30T22:00:00" event_id="291"
              sell_from="2020-07-01T00:00:00" sell_to="2021-06-30T20:00:00" sold_out="false">
                <zone zone_id="40" capacity="240" price="20.00" name="Platea" numbered="true" />
                <zone zone_id="38" capacity="50" price="15.00" name="Grada 2" numbered="false" />
                <zone zone_id="30" capacity="90" price="30.00" name="A28" numbered="true" />
             </event>
          </base_event>
        </output>
    </eventList>
    """
    provider = ProviderA(provider_url="http://localhost")
    [result] = await provider.parse(xml)

    assert isinstance(result, ProviderABaseEvent)
    assert result.base_event_id == 291
    assert result.sell_mode == "online"
    assert result.title == "Camela en concierto"
    assert result.organizer_company_id is None
    assert len(result.events) == 1
    assert result.events[0] == ProviderAEvent(
        event_id=291,
        event_start_date=datetime(2021, 6, 30, 21, 0),
        event_end_date=datetime(2021, 6, 30, 22, 0),
        sell_from=datetime(2020, 7, 1, 0, 0),
        sell_to=datetime(2021, 6, 30, 20, 0),
        sold_out=False,
        zones=[
            ProviderAZone(zone_id=40, capacity=240, price=20.0, name="Platea", numbered=True),
            ProviderAZone(zone_id=38, capacity=50, price=15.0, name="Grada 2", numbered=False),
            ProviderAZone(zone_id=30, capacity=90, price=30.0, name="A28", numbered=True),
        ],
    )


async def test_fetch_xml_success(respx_mock):
    xml_content = "<root><item>1</item><item>2</item></root>"
    provider_route = respx_mock.get(URL).mock(return_value=Response(200, content=xml_content))

    provider = ProviderA(provider_url=URL)
    response = await provider.extract()

    provider_route.calls.assert_called_once()

    assert response == xml_content


async def test_retrieve_400_error(respx_mock):
    provider_route = respx_mock.get(URL).mock(return_value=Response(status.HTTP_400_BAD_REQUEST))
    provider = ProviderA(provider_url=URL)
    provider.extract.retry.wait = tenacity.wait_fixed(0)
    assert isinstance(provider.breaker.state, pybreaker.CircuitClosedState)

    with pytest.raises(httpx.HTTPStatusError) as exec_info:
        await provider.extract()

    provider_route.calls.assert_called_once()
    assert exec_info.value.response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(provider.breaker.state, pybreaker.CircuitClosedState)


async def test_retrieve_500_error_circuit_breaker_open(respx_mock):
    provider_route = respx_mock.get(URL).mock(return_value=Response(status.HTTP_500_INTERNAL_SERVER_ERROR))
    provider = ProviderA(provider_url=URL)
    assert isinstance(provider.breaker.state, pybreaker.CircuitClosedState)
    provider.extract.retry.wait = tenacity.wait_fixed(0)

    with pytest.raises(pybreaker.CircuitBreakerError) as exec_info:
        await provider.extract()

    assert provider_route.calls.call_count == provider.extract.retry.stop.max_attempt_number
    assert exec_info.value.args[0] == "Failures threshold reached, circuit breaker opened"
    assert isinstance(provider.breaker.state, pybreaker.CircuitOpenState)
    provider.breaker.close()


@pytest.mark.parametrize("side_effect", [httpx.ConnectError, httpx.TimeoutException])
async def test_connection_transport_error_circuit_breaker_open(respx_mock, side_effect):
    provider_route = respx_mock.get(URL).mock(side_effect=side_effect)
    provider = ProviderA(URL)
    provider.extract.retry.wait = tenacity.wait_fixed(0)
    assert isinstance(provider.breaker.state, pybreaker.CircuitClosedState)

    with pytest.raises(pybreaker.CircuitBreakerError) as exec_info:
        await provider.extract()

    assert provider_route.calls.call_count == provider.extract.retry.stop.max_attempt_number
    assert exec_info.value.args[0] == "Failures threshold reached, circuit breaker opened"
    assert isinstance(provider.breaker.state, pybreaker.CircuitOpenState)
    provider.breaker.close()
