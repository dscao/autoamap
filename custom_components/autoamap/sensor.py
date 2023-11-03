"""Support for Traccar device tracking."""
from __future__ import annotations

import logging

import time, datetime

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import UnitOfElectricPotential, PERCENTAGE

from homeassistant.const import CONF_NAME

from .const import (
    COORDINATOR,
    DOMAIN,
    MANUFACTURER,
    CONF_SENSORS,
    ATTR_ADDRESS,
    ATTR_PARKING_TIME,
    ATTR_LASTSTOPTIME,
    ATTR_QUERYTIME,
    KEY_ADDRESS,
    KEY_LASTSTOPTIME,
    KEY_PARKING_TIME,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=KEY_ADDRESS,
        name="address",
        icon="mdi:map"
    ),
    SensorEntityDescription(
        key=KEY_PARKING_TIME,
        name="parkingtime",
        icon="mdi:timer-stop-outline"
    ),
    SensorEntityDescription(
        key=KEY_LASTSTOPTIME,
        name="laststoptime",
        icon="mdi:timer-stop"
    )
)

SENSOR_TYPES_MAP = { description.key: description for description in SENSOR_TYPES }
#_LOGGER.debug("SENSOR_TYPES_MAP: %s" ,SENSOR_TYPES_MAP)

SENSOR_TYPES_KEYS = { description.key for description in SENSOR_TYPES }
#_LOGGER.debug("SENSOR_TYPES_KEYS: %s" ,SENSOR_TYPES_KEYS)
SCAN_INTERVAL = datetime.timedelta(seconds=60)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add gooddriver entities from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    device_name = config_entry.data[CONF_NAME]
    enabled_sensors = [s for s in config_entry.options.get(CONF_SENSORS, []) if s in SENSOR_TYPES_KEYS]
    
    _LOGGER.debug("user_id: %s ,coordinator sensors: %s", device_name, coordinator.data)
    _LOGGER.debug("enabled_sensors: %s" ,enabled_sensors)
    
    sensors = []
    for sensor_type in enabled_sensors:
        _LOGGER.debug("sensor_type: %s" ,sensor_type)
        sensors.append(gooddriverSensorEntity(device_name, SENSOR_TYPES_MAP[sensor_type], coordinator))
        
    async_add_entities(sensors, False)

class gooddriverSensorEntity(CoordinatorEntity):
    """Define an bjtoon_health_code entity."""
    
    _attr_has_entity_name = True
      
    def __init__(self, device_name, description, coordinator):
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = description
        self._unique_id = f"{DOMAIN}-{device_name}-{description.key}"
        self._device_name = device_name
        self.coordinator = coordinator
        
        _LOGGER.debug("SensorEntity coordinator: %s", coordinator.data)

        #self._attr_name = f"{self.entity_description.name}"
        self._attr_translation_key = f"{self.entity_description.name}"
        if self.entity_description.key == KEY_PARKING_TIME:
            self._state = self.coordinator.data.get(ATTR_PARKING_TIME)
        elif self.entity_description.key == KEY_LASTSTOPTIME:
            self._state = self.coordinator.data.get(ATTR_LASTSTOPTIME)
        elif self.entity_description.key == KEY_ADDRESS:
            if self.coordinator.data.get(ATTR_ADDRESS):                
                self._state = self.coordinator.data.get(ATTR_ADDRESS)
            else:
                self._state = "unknown"
            
        self._attrs = {ATTR_QUERYTIME: self.coordinator.data["querytime"]}
        
        _LOGGER.debug(self._state)

    @property
    def unique_id(self):
        return self._unique_id
        
    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.data["location_key"])},
            "name": self._device_name,
            "manufacturer": MANUFACTURER,
            "entry_type": DeviceEntryType.SERVICE,
            "model": self.coordinator.data["device_model"],
            "sw_version": self.coordinator.data["sw_version"],
        }

    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return True

    @property
    def native_value(self):
        """Return battery value of the device."""
        return self._state

    @property
    def state(self):
        """Return the state."""
        return self._state
    
    @property
    def state_attributes(self): 
        attrs = {}
        data = self.coordinator.data
        if data:            
            attrs["querytime"] = data["querytime"]        
        return attrs
        

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update gooddriver entity."""
        _LOGGER.debug("刷新sensor数据")
        #await self.coordinator.async_request_refresh()
        if self.entity_description.key == KEY_PARKING_TIME:
            self._state = self.coordinator.data.get(ATTR_PARKING_TIME)
        elif self.entity_description.key == KEY_LASTSTOPTIME:
            self._state = self.coordinator.data.get(ATTR_LASTSTOPTIME)
        elif self.entity_description.key == KEY_ADDRESS:
            if self.coordinator.data.get(ATTR_ADDRESS):                
                self._state = self.coordinator.data.get(ATTR_ADDRESS)
            else:
                self._state = "unknown"
            
        self._attrs = {ATTR_QUERYTIME: self.coordinator.data["querytime"]}
        
        
