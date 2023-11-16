'''
Support for auto.amap.com 高德地图车机版
Author        : dscao
Github        : https://github.com/dscao
Description   : 
Date          : 2022-05-13
LastEditors   : dscao
LastEditTime  : 2023-11-16
'''
"""
name: 'autoamap'
key: 'KO8IbsmkeGDqdNrj7nBFd8htmgOFI3W38zVQYAZLnEEX4KGql41KsRWCAPrqq0g4hjSxiOYBH%2FN2lC6JNMie03tp1HaqiinC87XcXFuTg7ptcHmd5ZgQgKL0vY%2Fqcih86bLlF9RJtkoYzy3vXWbrvYZunEW91%2BJlLN25Vb8dQjnplJ%2B2IHyVmvRiZT%2FM%2BJ84Po3wkKEQB8beyoNup9VbYXjgSCQ%2F1ABvyHtsZ5Ag5w%2FTpMMSxifnGZvkqiZ9J%2FdPEe2LrG4gJSpSiN%2B22JTSIhAV1g0pNzyEjvonkIOAnuMWRJLH088TS3qa2cgaBoNyZLd56Io6%2Fskh4N9CLoCS5ENAGRMq%2Flz%2Fu%2F%2Bu8bkIWJcDL9LoTB1PTf97UTPpU4dbdJN%2Ba0GKnY3ftrgfUINSwyzzAlnqx%2FAU1ngSb79JNVXI4KaNr86X50%2B67uhnS7Aq9H9ZmnXPK0zwC6lC7rS5KKGC94rcbpVoB4Wfq7fB1EsGsSqFVxyx1NK83q4qaCieg3vdWsum8rPH%2B1V8N9dYjQ1Gw6MxZgz5L2n2l%2FW5eMiObJilZmiGL7ObKWfbkr9U2YaViHrhGQSFEmgdZfg0YkOPLLv6y7w%2FA8fKEV%2BEaL4yzg8BBpCIKRX%2B1FXNFjckyAAdVBz4II5t4WMVG6PKZ5Wx00OqsuPVSBEnzpIT7%2BZMg2L7ALP8JyZp2O1%2B6TQkVSh0l%2Fj6NlgEyIuhUiVDYa7%2BFqWqATCmeiRcF5Qls0ollAsxjCeb8VNHehmCxi80UjeW3MTJZ73rso5rYBj%2F9p0toLXMnR2Re0SR0B5asxKusJ%2Bogc%2BkdZgt15nu6EXxSdgHRDFtgcR3yERXIC4g%2FODEJc3uqMf2EZTpxz4E%2XXXXXXXXXXzSvH0iCA7kGXDh4q%2FovQaHKoLW3IO9QjNH8PH%2Bh7Rwcbzkycijv2YX7KteXXXXXXXXXX&csid=25615E59-E54D-4939-9990-XXXXXXXXX'
sessionid: 'cpuywkud2f0jvhpnigysigXXXXXXXXX'
paramdata: 'oMYpWPAUpXXXXXXXXX'
    
Component to integrate with 高德地图车机版.

For more details about this component, please refer to
https://github.com/dscao/autoamap
"""
import logging
import asyncio
import json
import time, datetime
import requests
import re
import pytz
import os

from aiohttp.client_exceptions import ClientConnectorError
from async_timeout import timeout

from dateutil.relativedelta import relativedelta 
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA

from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
from datetime import timedelta
import homeassistant.util.dt as dt_util
from homeassistant.components import zone
from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.components.device_tracker.const import CONF_SCAN_INTERVAL
from homeassistant.components.device_tracker.legacy import DeviceScanner

from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import slugify
from homeassistant.helpers.event import track_utc_time_change
from homeassistant.util import slugify
from homeassistant.util.location import distance
from homeassistant.util.json import save_json, load_json

from homeassistant.const import (
    Platform,
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
    CONF_UPDATE_INTERVAL,
)

TYPE_GEOFENCE = "Geofence"
__version__ = '2023.11.16'

_LOGGER = logging.getLogger(__name__)   
    
PLATFORMS = [Platform.DEVICE_TRACKER, Platform.SENSOR]

USER_AGENT = 'iphone OS 15.4.1'
API_URL = "http://ts.amap.com/ws/tservice/internal/link/mobile/get?ent=2&in="
        

varstinydict = {}
        
async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured autoamap."""
    # if (MAJOR_VERSION, MINOR_VERSION) < (2022, 4):
        # _LOGGER.error("Minimum supported Hass version 2022.4")
        # return False
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass, config_entry) -> bool:
    """Set up autoamap as config entry."""
    global varstinydict
    user_id = config_entry.data[CONF_USER_ID]
    api_key = config_entry.data[CONF_API_KEY]
    paramadata = config_entry.data[CONF_PARAMDATA]
    xuhao = config_entry.data[CONF_XUHAO]
    update_interval_seconds = config_entry.options.get(CONF_UPDATE_INTERVAL, 90)
    attr_show = config_entry.options.get(CONF_ATTR_SHOW, True)
    location_key = config_entry.unique_id
    
    def save_to_file(filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f)
    def read_from_file(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data        
    path = hass.config.path(f'.storage')
        
    if not os.path.exists(f'{path}/autoamap.json'):
        save_to_file(f'{path}/autoamap.json', {})            
    varstinydict = read_from_file(f'{path}/autoamap.json')
    _LOGGER.debug("varstinydict: %s", varstinydict)

    _LOGGER.debug("Using location_key: %s, user_id: %s, update_interval_seconds: %s", location_key, user_id, update_interval_seconds)

    websession = async_get_clientsession(hass)

    coordinator = autoamapDataUpdateCoordinator(
        hass, websession, api_key, user_id, paramadata, xuhao, location_key, update_interval_seconds
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = config_entry.add_update_listener(update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True

async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def update_listener(hass, config_entry):
    """Update listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class autoamapDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching autoamap data API."""

    def __init__(self, hass, session, api_key, user_id, paramdata, xuhao, location_key, update_interval_seconds):
        """Initialize."""
        self.location_key = location_key
        self.user_id = user_id
        self.api_key = api_key
        self.api_paramdata = paramdata
        self.api_xuhao = xuhao       
        
            
        self.path = hass.config.path(f'.storage')
        
        # if not os.path.exists(f'{self.path}/autoamap.json'):
            # self.save_to_file(f'{self.path}/autoamap.json', {})            
        # varstinydict = self.read_from_file(f'{self.path}/autoamap.json')
        # _LOGGER.debug("varstinydict: %s", varstinydict)
        
        update_interval = (
            datetime.timedelta(seconds=int(update_interval_seconds))
        )
        _LOGGER.debug("Data will be update every %s", update_interval)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    def save_to_file(self, filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f)

    def read_from_file(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    
    # @asyncio.coroutine
    def get_data(self, url, headerstr):
        json_text = requests.get(url, headers=headerstr).content
        json_text = json_text.decode('utf-8')
        resdata = json.loads(json_text)
        return resdata
        
    def post_data(self, url, headerstr, datastr):
        json_text = requests.post(url, headers=headerstr, data = datastr).content
        json_text = json_text.decode('utf-8')
        resdata = json.loads(json_text)
        return resdata
        

    async def _async_update_data(self):
        """Update data via library.""" 
        global varstinydict
        _LOGGER.debug("varstinydict: %s", varstinydict)
        if not varstinydict.get("laststoptime_"+self.location_key):            
            varstinydict["laststoptime_"+self.location_key] = ""
        if not varstinydict.get("lastlat_"+self.location_key):
            varstinydict["lastlat_"+self.location_key] = ""
        if not varstinydict.get("lastlon_"+self.location_key):
            varstinydict["lastlon_"+self.location_key] = ""
        if not varstinydict.get("isonline_"+self.location_key):
            varstinydict["isonline_"+self.location_key] = "no"
        if not varstinydict.get("lastonlinetime_"+self.location_key):
            varstinydict["lastonlinetime_"+self.location_key] = ""
        if not varstinydict.get("lastofflinetime_"+self.location_key):
            varstinydict["lastofflinetime_"+self.location_key] = ""        
        if not varstinydict.get("runorstop_"+self.location_key):
            varstinydict["runorstop_"+self.location_key] = "stop"
                
        try:
            async with timeout(10): 
                headers = {
                    'Host': 'ts.amap.com',
                    'Accept': 'application/json',
                    'sessionid': self.user_id,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                    'Cookie': 'sessionid=' + self.user_id,
                    }
                url = str.format(API_URL + self.api_key)
                Data = self.api_paramdata
                resdata =  await self.hass.async_add_executor_job(self.post_data, url, headers, Data)
        except (
            ClientConnectorError
        ) as error:
            raise UpdateFailed(error)
        _LOGGER.debug("Requests remaining: %s", url)
        
        data = resdata["data"]["carLinkInfoList"][self.api_xuhao]
        _LOGGER.debug("result data: %s", data)
        
        if data.get("data"):
            macaddr = data["data"]["macaddr"]
        else:
            macaddr = "未知"
            
        if data:
            querytime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            device_model = "高德地图车机版"
            sw_version = data["sysInfo"]["autodiv"]
            
            thislat = data["naviLocInfo"]["lat"]
            thislon = data["naviLocInfo"]["lon"]
            
            if data["onlineStatus"] == 1:
                status = "在线"
            elif data["onlineStatus"] == 0:
                status = "离线"
            else:
                status = "未知"
                
            if data['naviStatus'] == 1:
                naviStatus = "导航中"
            else:
                naviStatus = "未导航"
                
            if status == "离线" and (varstinydict["isonline_"+self.location_key] == "yes"):
                varstinydict["lastofflinetime_"+self.location_key] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                varstinydict["isonline_"+self.location_key] = "no"
            if status == "在线" and (varstinydict["isonline_"+self.location_key] == "no"):
                varstinydict["lastonlinetime_"+self.location_key] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                varstinydict["isonline_"+self.location_key] = "yes"            
            
            if str(thislat) != str(varstinydict["lastlat_"+self.location_key]) or str(thislon) != str(varstinydict["lastlon_"+self.location_key]):
                _LOGGER.debug("变成运动: %s ,%s ,%s", varstinydict,thislat,thislon)
                varstinydict["lastlat_"+self.location_key] = data["naviLocInfo"]["lat"]
                varstinydict["lastlon_"+self.location_key] = data["naviLocInfo"]["lon"]
                varstinydict["runorstop_"+self.location_key] = "run"                
                
            elif varstinydict["runorstop_"+self.location_key] == "run":
                _LOGGER.debug("变成静止: %s", varstinydict)
                varstinydict["laststoptime_"+self.location_key] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                varstinydict["runorstop_"+self.location_key] = "stop"
                self.save_to_file(f'{self.path}/autoamap.json', varstinydict)
                
            
        lastofflinetime = varstinydict["lastofflinetime_"+self.location_key]
        lastonlinetime = varstinydict["lastonlinetime_"+self.location_key]
        laststoptime = varstinydict["laststoptime_"+self.location_key] 
        runorstop =  varstinydict["runorstop_"+self.location_key]
        
        def time_diff (timestamp):
            result = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
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
        if laststoptime != "" and runorstop ==  "stop":
            parkingtime=time_diff(int(time.mktime(time.strptime(laststoptime, "%Y-%m-%d %H:%M:%S")))) 
        else:
            parkingtime = "未知"
                
                
        return {"location_key":self.location_key,"device_model":device_model,"sw_version":sw_version,"thislat":thislat,"thislon":thislon,"querytime":querytime,"status":status,"macaddr":macaddr,"naviStatus":naviStatus,"lastofflinetime":lastofflinetime,"lastonlinetime":lastonlinetime,"laststoptime":laststoptime,"runorstop":runorstop,"parkingtime":parkingtime}

