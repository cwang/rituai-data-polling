import pytest
from main import poll, fetch


@pytest.mark.skip()
@pytest.mark.asyncio()
async def test_poll():
    urls = ["https://www.oreilly.com/feed/", "https://ft.com/world?format=rss"]
    result = await poll("demo@retuai.email", urls)
    assert result is not None
    assert len(result) > 0
    print(result)


@pytest.mark.asyncio()
async def test_fetch():
    await fetch()
