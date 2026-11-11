"""Model Playwright's thread ownership and resource failure paths."""

import importlib
import threading
from types import SimpleNamespace

import pytest

module = importlib.import_module(
    "pyutils_collection.playwright_functions.parallel_scrape"
)
pytestmark = [pytest.mark.unit, pytest.mark.playwright_functions]


@pytest.mark.parametrize("failure", [None, "page", "launch", "close"])
def test_worker_owns_and_cleans_its_playwright_resources(monkeypatch, failure):
    instances, contexts = [], []

    def start():
        owner = threading.get_ident()
        instance = SimpleNamespace(stopped=False, closed=False)
        instances.append(instance)

        def check_owner():
            assert threading.get_ident() == owner, "Playwright crossed threads"

        def stop():
            check_owner()
            instance.stopped = True

        def close():
            check_owner()
            instance.closed = True
            if failure == "close":
                raise RuntimeError("close failed")

        def new_context():
            check_owner()
            context = SimpleNamespace(closed=False)
            contexts.append(context)

            def new_page():
                check_owner()
                if failure == "page":
                    raise RuntimeError("page failed")
                return SimpleNamespace(owner=owner)

            def close_context():
                check_owner()
                context.closed = True

            context.set_default_timeout = lambda timeout: check_owner()
            context.new_page = new_page
            context.close = close_context
            return context

        def launch(**kwargs):
            check_owner()
            if failure == "launch":
                raise RuntimeError("launch failed")
            return SimpleNamespace(new_context=new_context, close=close)

        instance.chromium = SimpleNamespace(launch=launch)
        instance.stop = stop
        return instance

    monkeypatch.setattr(module, "sync_playwright", lambda: SimpleNamespace(start=start))

    def scrape(page, url):
        assert page.owner == threading.get_ident()
        return {"url": url}

    if failure in {"launch", "close"}:
        with pytest.raises(RuntimeError, match=f"{failure} failed"):
            module.parallel_scrape(["a", "b", "c"], scrape, max_workers=2)
    else:
        results = module.parallel_scrape(["a", "b", "c"], scrape, max_workers=2)
        assert [result["url"] for result in results] == ["a", "b", "c"]
        assert all(result["success"] is (failure is None) for result in results)
        if failure == "page":
            assert all("page failed" in result["error"] for result in results)
    assert instances and all(instance.stopped for instance in instances)
    assert all(context.closed for context in contexts)
