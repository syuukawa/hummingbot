#!/usr/bin/env python

import asyncio
import logging
from typing import (
    Optional
)
from wings.data_source.user_stream_tracker_data_source import UserStreamTrackerDataSource
from wings.user_stream_tracker import (
    UserStreamTrackerDataSourceType,
    UserStreamTracker
)
from wings.data_source.binance_api_user_stream_data_source import BinanceAPIUserStreamDataSource
from binance.client import Client as BinanceClient


class BinanceUserStreamTracker(UserStreamTracker):
    _bust_logger: Optional[logging.Logger] = None

    @classmethod
    def logger(cls) -> logging.Logger:
        if cls._bust_logger is None:
            cls._bust_logger = logging.getLogger(__name__)
        return cls._bust_logger

    def __init__(self,
                 data_source_type: UserStreamTrackerDataSourceType = UserStreamTrackerDataSourceType.EXCHANGE_API,
                 binance_client: Optional[BinanceClient] = None):
        super().__init__(data_source_type=data_source_type)
        self._binance_client: BinanceClient = binance_client
        self._ev_loop: asyncio.events.AbstractEventLoop = asyncio.get_event_loop()
        self._data_source: Optional[UserStreamTrackerDataSource] = None
        self._user_stream_tracking_task: Optional[asyncio.Task] = None

    @property
    def data_source(self) -> UserStreamTrackerDataSource:
        if not self._data_source:
            if self._data_source_type is UserStreamTrackerDataSourceType.EXCHANGE_API:
                self._data_source = BinanceAPIUserStreamDataSource(binance_client=self._binance_client)
            else:
                raise ValueError(f"data_source_type {self._data_source_type} is not supported.")
        return self._data_source

    @property
    def exchange_name(self) -> str:
        return "binance"

    async def start(self):
        self._user_stream_tracking_task = asyncio.ensure_future(
            self.data_source.listen_for_user_stream(self._ev_loop, self._user_stream)
        )
        await asyncio.gather(self._user_stream_tracking_task)
