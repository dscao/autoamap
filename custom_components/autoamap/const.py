
"""Constants for autoamap."""
DOMAIN = "autoamap"

PLATFORMS = ["sensor"]
REQUIRED_FILES = [
    "const.py",
    "manifest.json",
    "device_tracker.py",
    "config_flow.py",
    "translations/en.json",
]
VERSION = "2022.5.16"
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
NAME = "autoamap"

CONF_USER_ID = "user_id"
CONF_PARAMDATA = "paramdata"
CONF_XUHAO = "xuhao"
CONF_GPS_CONVER = "gps_conver"
CONF_ATTR_SHOW = "attr_show"
CONF_UPDATE_INTERVAL = "update_interval_seconds"

COORDINATOR = "coordinator"
UNDO_UPDATE_LISTENER = "undo_update_listener"


ATTR_SPEED = "speed"
ATTR_COURSE = "course"
ATTR_STATUS = "status"
ATTR_RUNORSTOP = "runorstop"
ATTR_LASTSTOPTIME = "laststoptime"
ATTR_UPDATE_TIME = "update_time"
ATTR_QUERYTIME = "query_time"
ATTR_PARKING_TIME = "parking_time"
