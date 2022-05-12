
"""Adds config flow for autoamap."""
import logging
import asyncio
import json
import time, datetime
import requests
import re
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_API_KEY, CONF_NAME

from collections import OrderedDict
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    CONF_USER_ID,
    CONF_PARAMDATA,
    CONF_XUHAO,
    CONF_UPDATE_INTERVAL,
    CONF_ATTR_SHOW,
    DOMAIN,
)

import voluptuous as vol

USER_AGENT = 'iphone OS 15.4.1'
API_URL = "http://ts.amap.com/ws/tservice/internal/link/mobile/get?ent=2&in=" 

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class autoamaplowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return autoamapOptionsFlow(config_entry)

    def __init__(self):
        """Initialize."""
        self._errors = {}
    
    def post_data(self, url, headerstr, datastr):
        json_text = requests.post(url, headers=headerstr, data = datastr).content
        json_text = json_text.decode('utf-8')
        resdata = json.loads(json_text)
        return resdata

    async def async_step_user(self, user_input={}):
        self._errors = {}
        if user_input is not None:
            # Check if entered host is already in HomeAssistant
            existing = await self._check_existing(user_input[CONF_NAME])
            if existing:
                return self.async_abort(reason="already_configured")

            # If it is not, continue with communication test  
            headers = {
                    'Host': 'ts.amap.com',
                    'Accept': 'application/json',
                    'sessionid': user_input["user_id"],
                    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                    'Cookie': 'sessionid=' + user_input["user_id"],
                    }
            url = str.format(API_URL + user_input["api_key"])
            Data = user_input["paramdata"]
            xuhao = user_input["xuhao"]

            redata =  await self.hass.async_add_executor_job(self.post_data, url, headers, Data)         
            _LOGGER.debug("Requests: %s", redata)
            
            status = redata["result"]=="true" and len(redata["data"]["carLinkInfoList"]) > user_input['xuhao']
            if status == True:
                await self.async_set_unique_id(f"autoamap-{user_input['user_id']}--{user_input['xuhao']}".replace(".","_"))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            else:
                self._errors["base"] = "communication"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):

        # Defaults
        device_name = "autoamap"
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default=device_name)] = str
        data_schema[vol.Required(CONF_API_KEY ,default ="9o1XKgwNYv4xxxxxxxx&csid=836xxxx-EB91-4xxx-84xx-A5xxxxxxxxxx")] = str
        data_schema[vol.Required(CONF_USER_ID ,default ="xr42asymxxxxxxxxxxxxxxxxxxxxxxxx")] = str
        data_schema[vol.Required(CONF_PARAMDATA ,default ="oMYpxxxxxxxxxxxx")] = str
        data_schema[vol.Required(CONF_XUHAO ,default =0 )] = int

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def async_step_import(self, user_input):
        """Import a config entry.

        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(title="configuration.yaml", data={})

    async def _check_existing(self, host):
        for entry in self._async_current_entries():
            if host == entry.data.get(CONF_NAME):
                return True

class autoamapOptionsFlow(config_entries.OptionsFlow):
    """Config flow options for autoamap."""

    def __init__(self, config_entry):
        """Initialize autoamap options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, 90),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=3600)),vol.Optional(
                        CONF_ATTR_SHOW,
                        default=self.config_entry.options.get(CONF_ATTR_SHOW, True),
                    ): bool
                }
            ),
        )
