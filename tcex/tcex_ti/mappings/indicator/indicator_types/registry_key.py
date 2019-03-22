# -*- coding: utf-8 -*-
"""ThreatConnect TI Registry Key"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class RegistryKey(Indicator):
    """Unique API calls for RegistryKey API Endpoints"""

    def __init__(self, tcex, key_name, value_name, value_type, **kwargs):
        """Initialize Class Properties.

        Args:
            key_name (str): The key_name value for this Indicator.
            value_name (str): The value_name value for this Indicator.
            value_type (str): The value_type value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(RegistryKey, self).__init__(tcex, 'registryKeys', **kwargs)
        self.data['key_name'] = key_name
        self.data['value_name'] = value_name
        self.data['value_type'] = value_type

    def can_create(self):
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if (
            self.data.get('key_name')
            and self.data.get('value_name')
            and self.data.get('value_type')
        ):
            return True
        return False

    def _set_unique_id(self, json_response):
        """

        :param json_response:
        """
        self.unique_id = json_response.get('key_name', '')
