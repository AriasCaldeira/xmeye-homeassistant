camera.py

import asyncio
import logging
import os
from socket import AF_INET, SOCK_STREAM, socket as Socket
from stat import S_IRUSR, S_IWUSR

import voluptuous as vol
import aiofiles

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, CONF_NAME

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    username = entry.data[CONF_USERNAME]
    password = entry.data.get(CONF_PASSWORD, "")

    _LOGGER.info("Connecting to %s:%i using %s", host, port, username)

    from dvrip.io import DVRIPClient

    client = DVRIPClient(Socket(AF_INET, SOCK_STREAM))
    client.connect((host, port), username, password)

    info = client.systeminfo()
    _LOGGER.info("Connected to %s. Found %i video-in", info.board, info.videoin)

    cameras = [
        XMEyeCamera(hass, client, i, (host, port))
        for i in range(int(info.videoin))
    ]

    async_add_entities(cameras)


class XMEyeCamera(Camera):
    def __init__(self, hass, client, channel, remote):
        super().__init__()
        self.hass = hass
        self._client = client
        self._channel = int(channel)
        self._remote = remote
        self._info = self._client.systeminfo()
        self._name = f"{self._info.board}_{channel}"
        self._named_pipe = f"/tmp/{self._name}.pipe"
        self._ffmpeg = hass.data.get("ffmpeg")
        self._reader_task = None
        self._sock = None

        self._ensure_pipe()
        self._start_reader_task()

    def _ensure_pipe(self):
        if os.path.exists(self._named_pipe):
            os.unlink(self._named_pipe)
        os.mkfifo(self._named_pipe, S_IRUSR | S_IWUSR)

    def _start_reader_task(self):
        self._reader_task = self.hass.loop.create_task(self._reader_loop())

    async def _reader_loop(self):
        from dvrip.monitor import Stream

        try:
            self._sock = Socket(AF_INET, SOCK_STREAM)
            self._sock.connect(self._remote)
            reader = self._client.monitor(self._sock, self._channel, Stream.HD)

            async with aiofiles.open(self._named_pipe, mode='wb') as pipe:
                while True:
                    chunk = reader.read(256)
                    if not chunk:
                        break
                    await pipe.write(chunk)
                    await pipe.flush()
        except Exception as e:
            _LOGGER.error("Error in reader loop: %s", e)

    @property
    def name(self):
        return self._name

    @property
    def model(self):
        return self._info.board

    @property
    def should_poll(self):
        return False

    async def async_camera_image(self):
        from haffmpeg.tools import ImageFrame, IMAGE_JPEG

        ffmpeg = ImageFrame(self._ffmpeg.binary, loop=self.hass.loop)
        try:
            image = await ffmpeg.get_image(self._named_pipe, output_format=IMAGE_JPEG)
            return image
        except Exception as e:
            _LOGGER.error("Failed to capture image from camera %s: %s", self._name, e)
            return None

    async def async_will_remove_from_hass(self):
        if self._reader_task:
            self._reader_task.cancel()
        if self._sock:
            self._sock.close()
        if os.path.exists(self._named_pipe):
            os.unlink(self._named_pipe)