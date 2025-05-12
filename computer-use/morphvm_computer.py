import asyncio
import base64
import io
import platform
import os
from PIL import Image

import pyautogui
from morphcloud.computer import Computer
from dotenv import load_dotenv

load_dotenv()

os.environ['MORPH_API_KEY'] = os.getenv("MORPH_API_KEY")
class LocalComputer:
    """Use pyautogui to take screenshots and perform actions on the local computer."""

    def __init__(self):
        self.computer = Computer.new(ttl_seconds=600)
        self.desktop_url = self.computer.desktop_url()
        print(self.desktop_url)
        self.dims = self.computer.dimensions
        self.size = self.dims

    @property
    def environment(self):
        system = platform.system()
        if system == "Windows":
            return "windows"
        elif system == "Darwin":
            return "mac"
        elif system == "Linux":
            return "linux"
        else:
            raise NotImplementedError(f"Unsupported operating system: '{system}'")

    @property
    def dimensions(self):
        return self.computer.dimensions
        if not self.size:
            screenshot = pyautogui.screenshot()
            self.size = screenshot.size
        return self.size

    async def screenshot(self):
        screenshot = self.computer.screenshot()
        return screenshot


    async def click(self, x: int, y: int, button: str = "left") -> None:
        width, height = self.size
        if 0 <= x < width and 0 <= y < height:
            button = "middle" if button == "wheel" else button
            self.computer.click(x, y, button)

    async def double_click(self, x: int, y: int) -> None:
        width, height = self.size
        if 0 <= x < width and 0 <= y < height:
            self.computer.double_click(x, y)

    async def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        self.computer.scroll(x, y, scroll_x, scroll_y)

    async def type(self, text: str) -> None:
        self.computer.type_text(text)

    async def wait(self, ms: int = 100) -> None:
        self.computer.wait(ms)

    async def move(self, x: int, y: int) -> None:
        self.computer.move_mouse(x, y)

    async def keypress(self, keys: list[str]) -> None:
        keys = [key.lower() for key in keys]
        keymap = {
            "arrowdown": "down",
            "arrowleft": "left",
            "arrowright": "right",
            "arrowup": "up",
        }
        keys = [keymap.get(key, key) for key in keys]
        for key in keys:
            self.computer.key_press(key)
            # pyautogui.keyDown(key)
        for key in keys:
            self.computer.key_press(key)
            # pyautogui.keyUp(key)

    async def drag(self, path: list[tuple[int, int]]) -> None:
        if len(path) <= 1:
            pass
        else:
            path = [{'x': point[0], 'y': point[1]} for point in path]
            self.computer.drag(path)

    async def browser(self):
        return self.computer.browser
    
    async def sandbox(self):
        return self.computer.sandbox
    
