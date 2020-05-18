from unittest.mock import MagicMock
import asyncio


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        # pylint: disable=useless-super-delegation
        return super(AsyncMock, self).__call__(*args, **kwargs)


class AsyncMockDelayed(MagicMock):
    async def __call__(self, *args, **kwargs):
        await asyncio.sleep(0.1)
        # pylint: disable=useless-super-delegation
        return super(AsyncMockDelayed, self).__call__(*args, **kwargs)
