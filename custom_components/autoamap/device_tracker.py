"""Support for the autoamap service."""
import logging
import time, datetime

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.device_registry import DeviceEntryType

#from homeassistant.helpers.entity import Entity

from homeassistant.const import (
    CONF_NAME,
    CONF_API_KEY,
    ATTR_GPS_ACCURACY,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    STATE_HOME,
    STATE_NOT_HOME, 
    MAJOR_VERSION, 
    MINOR_VERSION,    
)

from .const import (
    CONF_USER_ID,
    CONF_PARAMDATA,
    CONF_XUHAO,
    CONF_MAP_LAT,
    CONF_MAP_LNG,
    COORDINATOR,
    DOMAIN,
    UNDO_UPDATE_LISTENER,
    CONF_ATTR_SHOW,
    MANUFACTURER,
    ATTR_SPEED,
    ATTR_COURSE,
    ATTR_STATUS,
    ATTR_RUNORSTOP,
    ATTR_LASTSTOPTIME,
    ATTR_UPDATE_TIME,
    ATTR_QUERYTIME,
    ATTR_PARKING_TIME,
)

PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add autoamap entities from a config_entry."""
    name = config_entry.data[CONF_NAME]
    map_lat = config_entry.options.get(CONF_MAP_LAT, 0.00240)
    map_lng = config_entry.options.get(CONF_MAP_LNG, -0.00540)
    attr_show = config_entry.options.get(CONF_ATTR_SHOW, True)
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    _LOGGER.debug("user_id: %s ,coordinator result: %s", name, coordinator.data)

    async_add_entities([autoamapEntity(name, map_lat, map_lng, attr_show, coordinator)], False)


class autoamapEntity(TrackerEntity):
    """Representation of a tracker condition."""
    
    def __init__(self, name, map_lat, map_lng, attr_show, coordinator):
        
        self.coordinator = coordinator
        _LOGGER.debug("coordinator: %s", coordinator.data)
        self._name = name
        self._map_lat = map_lat
        self._map_lng = map_lng
        self._attrs = {}
        self._attr_show = attr_show

    @property
    def name(self):            
        return self._name
        
     
    @property
    def unique_id(self):
        """Return a unique_id for this entity."""
        _LOGGER.debug("device_tracker_unique_id: %s", self.coordinator.data["location_key"])
        return self.coordinator.data["location_key"]

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.data["location_key"])},
            "name": self._name,
            "manufacturer": MANUFACTURER,
            "entry_type": DeviceEntryType.SERVICE,
            "model": self.coordinator.data["device_model"],
            "sw_version": self.coordinator.data["sw_version"],
        }
    @property
    def should_poll(self):
        """Return the polling requirement of the entity."""
        return False

    # @property
    # def available(self):
        # """Return True if entity is available."""
        # return self.coordinator.last_update_success 

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:car"
        
    @property
    def source_type(self):
        return "gps"

    @property
    def latitude(self):                
        return (float(self.coordinator.data["thislat"]) + self._map_lat)

    @property
    def longitude(self):
        return (float(self.coordinator.data["thislon"]) + self._map_lng)
        
    @property
    def location_accuracy(self):
        return 10        

    @property
    def state_attributes(self): 
        attrs = super(autoamapEntity, self).state_attributes
        #data = self.coordinator.data.get("result")
        data = self.coordinator.data
        if data:             
            attrs[ATTR_STATUS] = data["status"]
            attrs["navistatus"] = data["naviStatus"]
            attrs["macaddr"] = data["macaddr"]        
            attrs[ATTR_QUERYTIME] = data["querytime"]
            if self._attr_show == True:
                attrs[ATTR_RUNORSTOP] = data["runorstop"]
                attrs[ATTR_LASTSTOPTIME] = data["laststoptime"]
                attrs["lastofflinetime"] = data["lastofflinetime"]
                attrs["lastonlinetime"] = data["lastonlinetime"]
                attrs[ATTR_PARKING_TIME] = data["parkingtime"]  
        return attrs    


    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update autoamap entity."""
        _LOGGER.debug("device tracker_update: %s", self.coordinator.data["MESSAGE"]["HD_STATE_TIME"])
        _LOGGER.debug(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)
        await self.coordinator.async_request_refresh()
