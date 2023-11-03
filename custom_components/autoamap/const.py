
"""Constants for autoamap."""
DOMAIN = "autoamap"

REQUIRED_FILES = [
    "const.py",
    "manifest.json",
    "device_tracker.py",
    "config_flow.py",
    "translations/en.json",
    "translations/zh-Hans.json",
]
VERSION = "2023.11.3"
ISSUE_URL = "https://github.com/dscao/autoamap/issues"

STARTUP = """
-------------------------------------------------------------------
{name}
Version: {version}
This is a custom component
If you have any issues with this you need to open an issue here:
{issueurl}
-------------------------------------------------------------------
"""

from homeassistant.const import (
    ATTR_DEVICE_CLASS,
)

ATTR_ICON = "icon"
ATTR_LABEL = "label"
MANUFACTURER = "auto.amap.com."
NAME = "高德地图机车版"

CONF_USER_ID = "user_id"
CONF_PARAMDATA = "paramdata"
CONF_XUHAO = "xuhao"
CONF_GPS_CONVER = "gps_conver"
CONF_ATTR_SHOW = "attr_show"
CONF_UPDATE_INTERVAL = "update_interval_seconds"
CONF_SENSORS = "sensors"
CONF_MAP_GCJ_LAT = "map_gcj_lat"
CONF_MAP_GCJ_LNG = "map_gcj_lng"
CONF_MAP_BD_LAT = "map_bd_lat"
CONF_MAP_BD_LNG = "map_bd_lng"
CONF_ADDRESSAPI = "addressapi"
CONF_API_KEY = "api_key"

COORDINATOR = "coordinator"
UNDO_UPDATE_LISTENER = "undo_update_listener"

KEY_ADDRESS = "address"
KEY_QUERYTIME = "querytime"
KEY_PARKING_TIME = "parkingtime"
KEY_LASTSTOPTIME = "laststoptime"

ATTR_SPEED = "speed"
ATTR_COURSE = "course"
ATTR_STATUS = "status"
ATTR_DEVICE_STATUS = "device_status"
ATTR_RUNORSTOP = "runorstop"
ATTR_LASTSTOPTIME = "laststoptime"
ATTR_LAST_UPDATE = "update_time"
ATTR_QUERYTIME = "querytime"
ATTR_PARKING_TIME = "parkingtime"
ATTR_ADDRESS = "address"

