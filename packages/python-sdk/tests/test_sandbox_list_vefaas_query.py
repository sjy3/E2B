import pytest

import e2b.sandbox_async.paginator as async_paginator_mod
import e2b.sandbox_sync.paginator as sync_paginator_mod
from e2b.api.client.types import UNSET
from e2b.exceptions import InvalidArgumentException
from e2b.sandbox.sandbox_api import SandboxQuery
from e2b.sandbox_async.paginator import AsyncSandboxPaginator
from e2b.sandbox_sync.paginator import SandboxPaginator


VEFAAS_API_URL = "https://api.vefaas-e2b.sandbox-cn-beijing.volcapig.com"


class _Response:
    status_code = 200
    headers = {}
    parsed = []


def test_sync_list_maps_template_to_vefaas_function_metadata(monkeypatch, test_api_key):
    captured = {}
    monkeypatch.setattr(sync_paginator_mod, "get_api_client", lambda config: object())

    def sync_detailed(**kwargs):
        captured.update(kwargs)
        return _Response()

    monkeypatch.setattr(
        sync_paginator_mod.get_v2_sandboxes, "sync_detailed", sync_detailed
    )

    paginator = SandboxPaginator(
        query=SandboxQuery(metadata={"foo": "bar"}, template="aaaa"),
        api_key=test_api_key,
        api_url=f"{VEFAAS_API_URL}/",
    )

    paginator.next_items()

    assert captured["metadata"] == "foo=bar&vefaas_function_id=aaaa"
    assert captured["template"] is UNSET


def test_sync_list_maps_template_using_e2b_api_url_env(monkeypatch, test_api_key):
    captured = {}
    monkeypatch.setenv("E2B_API_URL", f"{VEFAAS_API_URL}/")
    monkeypatch.setattr(sync_paginator_mod, "get_api_client", lambda config: object())

    def sync_detailed(**kwargs):
        captured.update(kwargs)
        return _Response()

    monkeypatch.setattr(
        sync_paginator_mod.get_v2_sandboxes, "sync_detailed", sync_detailed
    )

    paginator = SandboxPaginator(
        query=SandboxQuery(template="aaaa"),
        api_key=test_api_key,
    )

    paginator.next_items()

    assert captured["metadata"] == "vefaas_function_id=aaaa"
    assert captured["template"] is UNSET


@pytest.mark.asyncio
async def test_async_list_maps_template_to_vefaas_function_metadata(
    monkeypatch, test_api_key
):
    captured = {}
    monkeypatch.setattr(async_paginator_mod, "get_api_client", lambda config: object())

    async def asyncio_detailed(**kwargs):
        captured.update(kwargs)
        return _Response()

    monkeypatch.setattr(
        async_paginator_mod.get_v2_sandboxes, "asyncio_detailed", asyncio_detailed
    )

    paginator = AsyncSandboxPaginator(
        query=SandboxQuery(metadata={"foo": "bar"}, template="aaaa"),
        api_key=test_api_key,
        api_url=f"{VEFAAS_API_URL}/",
    )

    await paginator.next_items()

    assert captured["metadata"] == "foo=bar&vefaas_function_id=aaaa"
    assert captured["template"] is UNSET


def test_list_keeps_template_filter_on_non_vefaas_api_urls(monkeypatch, test_api_key):
    captured = {}
    monkeypatch.setattr(sync_paginator_mod, "get_api_client", lambda config: object())

    def sync_detailed(**kwargs):
        captured.update(kwargs)
        return _Response()

    monkeypatch.setattr(
        sync_paginator_mod.get_v2_sandboxes, "sync_detailed", sync_detailed
    )

    paginator = SandboxPaginator(
        query=SandboxQuery(metadata={"foo": "bar"}, template="aaaa"),
        api_key=test_api_key,
        api_url="https://api.not-vefaas.test",
    )

    paginator.next_items()

    assert captured["metadata"] == "foo=bar"
    assert captured["template"] == "aaaa"


def test_list_rejects_conflicting_vefaas_function_metadata(test_api_key):
    paginator = SandboxPaginator(
        query=SandboxQuery(
            metadata={"vefaas_function_id": "bbbb"},
            template="aaaa",
        ),
        api_key=test_api_key,
        api_url=VEFAAS_API_URL,
    )

    with pytest.raises(
        InvalidArgumentException,
        match="Cannot use query.template with metadata.vefaas_function_id",
    ):
        paginator.next_items()
