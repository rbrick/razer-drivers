import dbus as _dbus
from razer.client.device import RazerDeviceFactory as _RazerDeviceFactory
from razer.client import constants

__version__ = '1.0.11'


class DaemonNotFound(Exception):
    pass


class DeviceManager(object):
    def __init__(self):
        # Load up the DBus
        session_bus = _dbus.SessionBus()
        try:
            self._dbus = session_bus.get_object("org.razer", "/org/razer")
        except _dbus.DBusException:
            raise DaemonNotFound("Could not connect to daemon")

        # Get interface for daemon methods
        self._dbus_daemon = _dbus.Interface(self._dbus, "razer.daemon")

        # Get interface for devices methods
        self._dbus_devices = _dbus.Interface(self._dbus, "razer.devices")

        self._device_serials = self._dbus_devices.getDevices()
        self._devices = []

        self._daemon_version = self._dbus_daemon.version()

        for serial in self._device_serials:
            device = _RazerDeviceFactory.get_device(serial)
            self._devices.append(device)

    def stop_daemon(self):
        """
        Stop Daemon
        """
        self._dbus_daemon.stop()

    def turn_off_on_screensaver(self, enable:bool):
        """
        Set wether or not to turn off the devices when screensaver is active

        If True then when the screensaver is active the devices' brightness will be set to 0.
        When the screensaver is inactive the devices' brightness will be restored
        :param enable: True to enable screensaver disable
        :type enable: bool

        :raises ValueError: If enable isnt a bool
        """
        if not isinstance(enable, bool):
            raise ValueError("Enable must be a boolean")

        if enable:
            self._dbus_devices.enableTurnOffOnScreensaver()
        else:
            self._dbus_devices.disableTurnOffOnScreensaver()

    # TODO convert to property
    def sync_effects(self, sync:bool):
        """
        Enable or disable the syncing of effects between devices

        If sync is enabled, whenever an effect is set then it will be set on all other devices if the effect is available or a similar effect if it is not.
        :param sync: Sync effects
        :type sync: bool

        :raises ValueError: If sync isnt a bool
        """
        if not isinstance(sync, bool):
            raise ValueError("Sync must be a boolean")

        self._dbus_devices.syncEffects(sync)

    @property
    def devices(self) -> list:
        """
        Gets devices

        :return: List of devices
        :rtype: list of razer.clent.devices.RazerDevice
        """

        return self._devices

    @property
    def version(self) -> str:
        """
        Returns the Python library version

        :return: Version tuple
        :rtype: str
        """
        return __version__

    @property
    def daemon_version(self):
        """
        Returns the daemon version

        :return: Daemon version
        :rtype: str
        """
        return self._daemon_version

