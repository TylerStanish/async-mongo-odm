from unittest.mock import Mock


class AsyncMock(Mock):
    """
    This class is taken from https://stackoverflow.com/a/34828288, thanks to user 'e-satis'
    """

    def __call__(self, *args, **kwargs):
        sup = super()

        async def coro():
            return sup.__call__(*args, **kwargs)

        return coro()

    def __await__(self):
        return self().__await__()
