"""Load information about the current build environment."""

import platform
import psutil
from subprocess import CalledProcessError
from pydantic import Field
from pydantic_settings import BaseSettings


class Resources(BaseSettings):
    """Get information about the current system we're running in."""

    # A descriptor of the machine we're running on.
    machine: str = Field(default_factory=platform.platform)

    # The version of Python we're running on.
    python_version: str = Field(default_factory=platform.python_version)

    # The number of cores available to us.
    cores: int = Field(default_factory=psutil.cpu_count)

    # The amount of memory available to us in gigabytes.
    main_memory: float = Field(
        default_factory=lambda: psutil.virtual_memory().total / float(1024**3)
    )

    # The amount of swap memory available to us in gigabytes.
    swap_memory: float = Field(
        default_factory=lambda: psutil.swap_memory().total / float(1024**3)
    )

    # The amount of disk space available to us on / in gigabytes.
    storage: float = Field(
        default_factory=lambda: psutil.disk_usage("/").total / float(1024**3)
    )

    def enable_swap(self):
        """Enable swap memory."""

        from mads.build import log, shell

        if self.swap_memory > 0:
            log.info("Swap memory is already enabled.")
            return True

        try:
            # Create a swap file that is half the size of the available storage.
            swap_gbs = int(psutil.disk_usage("/").free / float(1024**3) / 2)
            shell(f"fallocate -l {swap_gbs}G /swapfile")

            # Set the permissions on the swap file.
            shell("chmod 600 /swapfile")

            # Designate the swap file as swap space.
            shell("mkswap /swapfile")

            # Enable the swap file.
            shell("swapon /swapfile")

            # Recompute the amount of swap memory available.
            self.swap_memory = psutil.swap_memory().total / float(1024**3)

            return True

        except CalledProcessError:
            log.error("Failed to enable swap memory.")
            return False
