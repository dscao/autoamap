"""Support for the autoamap service."""
import logging
import time, datetime
from datetime import datetime, timedelta

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

laststoptime = "未知"
lastlat = "未知"
lastlon = "未知"
runorstop = "未知"
thislat = "未知"
thislon = "未知"
lastofflinetime = "未知"
lastonlinetime = "未知"
isonline = "未知"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add autoamap entities from a config_entry."""
    name = config_entry.data[CONF_NAME] 
    xuhao = config_entry.data[CONF_XUHAO]
    attr_show = config_entry.options.get(CONF_ATTR_SHOW, True)
    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]
    _LOGGER.debug("user_id: %s ,coordinator result: %s", name, coordinator.data["result"])

    async_add_entities([autoamapEntity(name, attr_show, xuhao, coordinator)], False)


class autoamapEntity(TrackerEntity):
    """Representation of a tracker condition."""
    
    def __init__(self, name, attr_show, xuhao, coordinator):
        
        self.coordinator = coordinator
        _LOGGER.debug("coordinator macaddr: %s", coordinator.data["data"]["carLinkInfoList"][xuhao])
        self._name = name
        self._attrs = {}
        self._attr_show = attr_show
        self._xuhao = xuhao
        
        

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
        return "GPS"

    @property
    def latitude(self):
        
        global laststoptime
        global lastlat
        global lastlon
        global thislat
        global thislon
        global runorstop
        global lastofflinetime
        global lastonlinetime
        global isonline

        data = self.coordinator.data.get("data")["carLinkInfoList"][self._xuhao]

        _LOGGER.debug("latitude result data: %s", data)
        if data:            
            self._querytime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")           
            thislat = data["naviLocInfo"]["lat"]
            thislon = data["naviLocInfo"]["lon"]
            self._macaddr = data["data"]["macaddr"]
            
            if data["onlineStatus"] == 1:
                self._status = "在线"
            elif data["onlineStatus"] == 0:
                self._status = "离线"
            else:
                self._status = "未知"
                
            if data['naviStatus'] == 1:
                self._naviStatus = "导航中"
            else:
                self._naviStatus = "未导航"
                
            if self._status == "离线" and isonline == "yes":
                lastofflinetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                isonline = "no"
            if self._status == "在线" and isonline == "no":
                lastonlinetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                isonline = "yes"
                
                
            if thislat == lastlat and thislon == lastlon and runorstop == "运动":
                laststoptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                runorstop = "静止"
            elif thislat != lastlat or thislon != lastlon:
                lastlat = data["naviLocInfo"]["lat"]
                lastlon = data["naviLocInfo"]["lon"]
                runorstop = "运动"  
                
            def time_diff (timestamp):
                result = datetime.now() - datetime.fromtimestamp(timestamp)
                hours = int(result.seconds / 3600)
                minutes = int(result.seconds % 3600 / 60)
                seconds = result.seconds%3600%60
                if result.days > 0:
                    return("{0}天{1}小时{2}分钟".format(result.days,hours,minutes))
                elif hours > 0:
                    return("{0}小时{1}分钟".format(hours,minutes))
                elif minutes > 0:
                    return("{0}分钟{1}秒".format(minutes,seconds))
                else:
                    return("{0}秒".format(seconds)) 
            if laststoptime != "未知" and runorstop == "静止" :
                self._parking_time=time_diff(int(time.mktime(time.strptime(laststoptime, "%Y-%m-%d %H:%M:%S")))) 
            else:
                self._parking_time = "未知"
                
        return (float(thislat) + 0.00240)

    @property
    def longitude(self):
        return (float(thislon) - 0.00540)
        
    @property
    def location_accuracy(self):
        return 10        

    @property
    def state_attributes(self): 
        attrs = super(autoamapEntity, self).state_attributes
        data = self.coordinator.data.get("result")
        if data:             
            attrs[ATTR_STATUS] = self._status
            attrs["navistatus"] = self._naviStatus
            attrs["macaddr"] = self._macaddr            
            attrs[ATTR_QUERYTIME] = self._querytime
            if self._attr_show == True:
                attrs[ATTR_RUNORSTOP] = runorstop        
                attrs[ATTR_LASTSTOPTIME] = laststoptime
                attrs["lastofflinetime"] = lastofflinetime
                attrs["lastonlinetime"] = lastonlinetime  
                attrs[ATTR_PARKING_TIME] = self._parking_time    
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
