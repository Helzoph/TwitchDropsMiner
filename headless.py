from __future__ import annotations

import os
import asyncio
import logging
import getpass
from typing import Any, TYPE_CHECKING

from translate import _
from utils import task_wrapper
from constants import SETTINGS_PATH, State

if TYPE_CHECKING:
    from twitch import Twitch
    from utils import Game
    from inventory import TimedDrop, DropsCampaign
    from channel import Channel
    from yarl import URL

logger = logging.getLogger("TwitchDrops")

class HeadlessStatusBar:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager
        self._last_text: str = ""

    def update(self, text: str):
        if text == self._last_text:
            return
        self._last_text = text
        logger.info(text, extra={"label": "status"})

    def clear(self):
        pass

class HeadlessWebsocketStatus:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager

    def update(self, idx: int, status: str | None = None, topics: int | None = None):
        if status:
            logger.debug(f"Websocket {idx} status: {status}", extra={"label": "websocket", "idx": idx})

    def remove(self, idx: int):
        pass

class HeadlessLoginForm:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager

    async def ask_login(self) -> Any:
        logger.info("LOGIN REQUIRED", extra={"label": "login"})
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        token = input("2FA Token (leave empty if not required): ").strip()
        # We return a simple object with the required attributes
        from types import SimpleNamespace
        return SimpleNamespace(username=username, password=password, token=token)

    async def ask_enter_code(self, page_url: URL, user_code: str) -> None:
        logger.info("AUTH REQUIRED", extra={"label": "login", "url": page_url})
        logger.info("Enter code", extra={"label": "login", "code": user_code})

    def update(self, status: str, user_id: int | None):
        if user_id:
            logger.info("Login status", extra={"label": "login", "status": status, "user_id": user_id})
        else:
            logger.info(f"Login status: {status}", extra={"label": "login"})

class HeadlessTrayIcon:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager

    def change_icon(self, name: str):
        pass

    def update_title(self, drop: TimedDrop | None):
        pass

    def minimize(self):
        pass

    def restore(self):
        pass

    def stop(self):
        pass

    def notify(self, message: str, title: str | None = None, duration: float = 10):
        pass

    def grab_attention(self, sound: bool = True):
        pass

class HeadlessProgress:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager

    def display(self, drop: TimedDrop | None, *, countdown: bool = True, subone: bool = False):
        if drop:
            logger.info(
                f"Progress: {drop.campaign.game.name} - {drop.name}: {drop.progress}%",
                extra={
                    "label": "progress",
                    "game": drop.campaign.game.name,
                    "drop": drop.name,
                    "progress": drop.progress,
                }
            )

    def minute_almost_done(self) -> bool:
        return False

    def stop_timer(self):
        pass

    def start_timer(self):
        pass

class HeadlessInventory:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager

    async def add_campaign(self, campaign: DropsCampaign):
        pass

    def update_drop(self, drop: TimedDrop):
        pass

    def clear(self):
        pass

class HeadlessChannels:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager

    def display(self, channel: Channel | None = None, *, add: bool = False):
        pass

    def remove(self, channel: Channel):
        pass

    def clear(self):
        pass

    def get_selection(self) -> Channel | None:
        return None

    def set_watching(self, channel: Channel):
        logger.info("Watching channel", extra={"label": "watching", "channel": channel.name})

    def clear_watching(self):
        pass

class HeadlessConsoleOutput:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager

    def print(self, message: str):
        logger.info(message, extra={"label": "output"})


class HeadlessButton:
    def config(self, **kwargs):
        pass


class HeadlessHelp:
    def __init__(self, manager: HeadlessGUIManager):
        self._manager = manager
        self._invalidate_button = HeadlessButton()


class HeadlessGUIManager:
    def __init__(self, twitch: Twitch):
        self._twitch: Twitch = twitch
        self._close_requested = asyncio.Event()
        
        # Sub-components
        self.status = HeadlessStatusBar(self)
        self.websockets = HeadlessWebsocketStatus(self)
        self.login = HeadlessLoginForm(self)
        self.tray = HeadlessTrayIcon(self)
        self.progress = HeadlessProgress(self)
        self.inv = HeadlessInventory(self)
        self.channels = HeadlessChannels(self)
        self.output = HeadlessConsoleOutput(self)
        self.help = HeadlessHelp(self)
        
        # Internal flags
        self.close_requested_flag = False

    @property
    def close_requested(self) -> bool:
        return self._close_requested.is_set()

    def print(self, message: str):
        self.output.print(message)

    @task_wrapper
    async def _settings_watcher(self):
        try:
            last_mtime = os.path.getmtime(SETTINGS_PATH)
        except OSError:
            last_mtime = 0
        while not self.close_requested:
            await asyncio.sleep(5)
            try:
                current_mtime = os.path.getmtime(SETTINGS_PATH)
            except OSError:
                continue
            if current_mtime > last_mtime:
                last_mtime = current_mtime
                logger.info("Settings file changed, reloading...", extra={"label": "settings"})
                try:
                    self._twitch.settings.reload()
                except Exception:
                    logger.error("Failed to reload settings", exc_info=True, extra={"label": "settings"})
                    continue
                # update the language
                try:
                    _.set_language(self._twitch.settings.language)
                except ValueError:
                    # this language doesn't exist - stick to the current one
                    pass
                # trigger the state transition
                self._twitch.change_state(State.GAMES_UPDATE)

    def start(self):
        logger.info("Headless mode started", extra={"label": "lifecycle"})
        self._watcher_task = asyncio.create_task(self._settings_watcher())

    def stop(self):
        logger.info("Headless mode stopped", extra={"label": "lifecycle"})
        if hasattr(self, "_watcher_task"):
            self._watcher_task.cancel()

    def close(self, *args):
        self._close_requested.set()
        self._twitch.close()

    def close_window(self):
        pass

    async def wait_until_closed(self):
        await self._close_requested.wait()

    def prevent_close(self):
        pass

    def save(self, *, force: bool = False):
        pass

    def grab_attention(self, *, sound: bool = True):
        pass

    def set_games(self, games: set[Game]):
        pass

    def display_drop(self, drop: TimedDrop, *, countdown: bool = True, subone: bool = False):
        pass

    def clear_drop(self):
        pass

    async def coro_unless_closed(self, coro: Any) -> Any:
        tasks = [asyncio.ensure_future(coro), asyncio.ensure_future(self._close_requested.wait())]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        if self._close_requested.is_set():
            from exceptions import ExitRequest
            raise ExitRequest()
        return await next(iter(done))
