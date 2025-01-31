"""
Support for Skoda Connect Platform
"""
import logging

from . import DATA_KEY, DOMAIN, SkodaEntity
from .const import DATA
from homeassistant.components.sensor import DEVICE_CLASSES, SensorEntity
from homeassistant.const import CONF_RESOURCES

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Skoda sensors."""
    if discovery_info is None:
        return
    async_add_entities([SkodaSensor(hass.data[DATA_KEY], *discovery_info)])


async def async_setup_entry(hass, entry, async_add_devices):
    data = hass.data[DOMAIN][entry.entry_id][DATA]
    coordinator = data.coordinator
    if coordinator.data is not None:
        if CONF_RESOURCES in entry.options:
            resources = entry.options[CONF_RESOURCES]
        else:
            resources = entry.data[CONF_RESOURCES]

        async_add_devices(
            SkodaSensor(
                data, instrument.vehicle_name, instrument.component, instrument.attr
            )
            for instrument in (
                instrument
                for instrument in data.instruments
                if instrument.component == "sensor" and instrument.attr in resources
            )
        )

    return True


class SkodaSensor(SkodaEntity, SensorEntity):
    """Representation of a Skoda Sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        res = None
        try:
          # @CE@
          # TODO: pimp \\192.168.178.231\config\custom_components\skodaconnect\sensor.py with this try/except
          # Avoid this error in the logs occurring every night
          #   File "/usr/local/lib/python3.11/site-packages/skodaconnect/vehicle.py", line 2206, in outside_temperature
          #     response = int(self.attrs.get('StoredVehicleDataResponseParsed')['0x0301020001'].get('value', 0))
          #                    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
          # KeyError: '0x0301020001'          
          res = self.instrument.state
        except Exception as e:
          _LOGGER.warning(e)
        return res

    @property
    def native_unit_of_measurement(self):
        """Return the native unit of measurement."""
        return self.instrument.unit

    @property
    def device_class(self):
        """Return the class of this sensor, from DEVICE_CLASSES."""
        if self.instrument.device_class in DEVICE_CLASSES:
            return self.instrument.device_class
        return None

    @property
    def state_class(self):
        """Return the state_class for the sensor, to enable statistics"""
        state_class = None
        if self.instrument.attr in [
            'battery_level', 'adblue_level', 'fuel_level', 'charging_time_left', 'charging_power', 'charge_rate',
            'electric_range', 'combustion_range', 'combined_range', 'outside_temperature'
        ]:
            state_class = "measurement"
        return state_class

