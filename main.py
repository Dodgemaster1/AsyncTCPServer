import asyncio
import ctypes
import logging
import os
import platform
import sys
from src.server import run_servers
from src.setup_logger import setup_logger


# Disable quick edit mode for console in windows
def disable_quick_edit():
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.GetStdHandle(-10)
    mode = ctypes.c_uint32()

    kernel32.GetConsoleMode(handle, ctypes.byref(mode))

    new_mode = mode.value & ~0x0040
    kernel32.SetConsoleMode(handle, new_mode)



if __name__ == '__main__':
    setup_logger()
    log = logging.getLogger(__name__)
    log.debug(sys.version)
    log.debug(f"PID = {os.getpid()}")

    if platform.system() == 'Windows':
        disable_quick_edit()

    asyncio.run(run_servers())
