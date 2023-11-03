"""Support for the autoamap service."""
import logging
import time, datetime
import requests
import re
import json
from aiohttp.client_exceptions import ClientConnectorError
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from .helper import gcj02towgs84, wgs84togcj02, gcj02_to_bd09

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
    CONF_GPS_CONVER,
    COORDINATOR,
    DOMAIN,
    UNDO_UPDATE_LISTENER,
    CONF_ATTR_SHOW,
    MANUFACTURER,
    ATTR_SPEED,
    ATTR_COURSE,
    ATTR_STATUS,
    ATTR_DEVICE_STATUS,
    ATTR_RUNORSTOP,
    ATTR_LASTSTOPTIME,
    ATTR_LAST_UPDATE,
    ATTR_QUERYTIME,
    ATTR_PARKING_TIME,
    ATTR_ADDRESS,
    CONF_ADDRESSAPI,
    CONF_API_KEY,
    CONF_MAP_GCJ_LAT,
    CONF_MAP_GCJ_LNG,
    CONF_MAP_BD_LAT,
    CONF_MAP_BD_LNG, 
)

PARALLEL_UPDATES = 1
_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(seconds=60)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add autoamap entities from a config_entry."""
    name = config_entry.data[CONF_NAME]
    gps_conver = config_entry.options.get(CONF_GPS_CONVER, True)
    attr_show = config_entry.options.get(CONF_ATTR_SHOW, True)
    addressapi = config_entry.options.get(CONF_ADDRESSAPI, "none")
    api_key = config_entry.options.get(CONF_API_KEY, "")
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    _LOGGER.debug("user_id: %s ,coordinator result: %s", name, coordinator.data)

    async_add_entities([autoamapEntity(hass, name, gps_conver, attr_show, addressapi, api_key, coordinator)], False)


class autoamapEntity(TrackerEntity):
    """Representation of a tracker condition."""
    _attr_has_entity_name = True
    _attr_name = None
    _attr_translation_key = "autoamap_device_tracker"
    def __init__(self, hass, name, gps_conver, attr_show, addressapi, api_key, coordinator):
        self._hass = hass
        self._addressapi = addressapi
        self._api_key = api_key
        self.coordinator = coordinator
        _LOGGER.debug("coordinator: %s", coordinator.data)
        self._name = name
        self._gps_conver = gps_conver
        self._attrs = {}
        self._attr_show = attr_show
        self._coords = []
        self._coords_old = []
        self._address = ""
        if self._gps_conver == True:
            self._coords = gcj02towgs84(self.coordinator.data["thislon"], self.coordinator.data["thislat"])
        else:
            self._coords = [self.coordinator.data["thislon"], self.coordinator.data["thislat"]]

    # @property
    # def name(self):            
        # return self._name
        
     
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
        return True

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
        return self._coords[1]

    @property
    def longitude(self):
        return self._coords[0]
        
    @property
    def location_accuracy(self):
        return 0        

    @property
    def state_attributes(self): 
        attrs = super(autoamapEntity, self).state_attributes
        #data = self.coordinator.data.get("result")
        data = self.coordinator.data
        if data:             
            attrs[ATTR_DEVICE_STATUS] = data["status"]
            attrs["navistatus"] = data["naviStatus"]
            attrs["macaddr"] = data["macaddr"]            
            if self._attr_show == True:
                attrs[ATTR_RUNORSTOP] = data["runorstop"]
                attrs[ATTR_LASTSTOPTIME] = data["laststoptime"]
                attrs["lastofflinetime"] = data["lastofflinetime"]
                attrs["lastonlinetime"] = data["lastonlinetime"]
                attrs[ATTR_PARKING_TIME] = data["parkingtime"]  
                attrs[ATTR_QUERYTIME] = data["querytime"]
                attrs[ATTR_ADDRESS] = self._address
                if self._gps_conver == True:
                    attrs[CONF_MAP_GCJ_LAT] = self.coordinator.data["thislat"]
                    attrs[CONF_MAP_GCJ_LNG] = self.coordinator.data["thislon"]
                    bddata = gcj02_to_bd09(self.coordinator.data["thislon"], self.coordinator.data["thislat"])
                    attrs[CONF_MAP_BD_LAT] = bddata[1]
                    attrs[CONF_MAP_BD_LNG] = bddata[0]
                else:
                    gcjdata = wgs84togcj02(self.coordinator.data["thislon"], self.coordinator.data["thislat"])
                    attrs[CONF_MAP_GCJ_LAT] = gcjdata[1]
                    attrs[CONF_MAP_GCJ_LNG] = gcjdata[0]
                    bddata = gcj02_to_bd09(gcjdata[0], gcjdata[1])
                    attrs[CONF_MAP_BD_LAT] = bddata[1]
                    attrs[CONF_MAP_BD_LNG] = bddata[0]
        return attrs    


    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update autoamap entity."""
        #_LOGGER.debug("device tracker_update: %s", self.coordinator.data["MESSAGE"]["HD_STATE_TIME"])
        _LOGGER.debug(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)
        _LOGGER.debug("刷新device_tracker数据")
        #await self.coordinator.async_request_refresh()
        _LOGGER.debug(self._addressapi)
        if self._gps_conver == True:
            self._coords = gcj02towgs84(self.coordinator.data["thislon"], self.coordinator.data["thislat"])
        else:
            self._coords = [self.coordinator.data["thislon"], self.coordinator.data["thislat"]]
            
        if self._coords_old != self._coords:
            try: 
                if self._addressapi == "baidu" and self._api_key:
                    _LOGGER.debug("baidu:"+self._api_key)
                    addressdata = await self._hass.async_add_executor_job(self.get_baidu_geocoding, self._coords[1], self._coords[0])
                    self._address = addressdata['result']['formatted_address'] + addressdata['result']['sematic_description']
                    self._coords_old = self._coords
                elif self._addressapi == "gaode" and self._api_key:
                    _LOGGER.debug("gaode:"+self._api_key)
                    gcjdata = wgs84togcj02(self._coords[0], self._coords[1])
                    addressdata = await self._hass.async_add_executor_job(self.get_gaode_geocoding, gcjdata[1], gcjdata[0])
                    self._address = addressdata['regeocode']['formatted_address']
                    self._coords_old = self._coords
                else:
                    self._address = ""                
                _LOGGER.debug(self._coords_old)
            except (
                ClientConnectorError
            ) as error:
                self._address = self._address or ""
                raise UpdateFailed(error)
                
    def get_data(self, url):
        json_text = requests.get(url).content
        json_text = json_text.decode('utf-8')
        json_text = re.sub(r'\\','',json_text)
        json_text = re.sub(r'"{','{',json_text)
        json_text = re.sub(r'}"','}',json_text)
        resdata = json.loads(json_text)
        return resdata
            
    def get_baidu_geocoding(self, lat, lng):
        api_url = 'https://api.map.baidu.com/reverse_geocoding/v3/'
        location = str("{:.6f}".format(lat))+','+str("{:.6f}".format(lng))
        url = api_url+'?ak='+self._api_key+'&output=json&coordtype=wgs84ll&extensions_poi=1&location='+location       
        response = self.get_data(url)
        _LOGGER.debug(response)
        return response
        
    def get_gaode_geocoding(self, lat, lng):
        api_url = 'https://restapi.amap.com/v3/geocode/regeo'
        location = str("{:.6f}".format(lng))+','+str("{:.6f}".format(lat))
        url = api_url+'?key='+self._api_key+'&output=json&coordinate=wgs84&extensions=base&location='+location       
        response = self.get_data(url)
        _LOGGER.debug(response)
        return response
