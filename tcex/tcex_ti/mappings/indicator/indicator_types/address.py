# -*- coding: utf-8 -*-
"""ThreatConnect TI Address"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class Address(Indicator):
    """Unique API calls for Address API Endpoints"""

    def __init__(self, tcex, ip, **kwargs):
        """Initialize Class Properties.

        Args:
            ip (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(Address, self).__init__(tcex, 'addresses', **kwargs)
        self._api_entity = 'address'
        self.data['ip'] = ip

    def can_create(self):
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get('ip'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """

        :param json_response:
        """
        self.unique_id = json_response.get('ip', '')

    def dns_resolution(self):
        """

        :return:
        """
        return self.tc_requests.dns_resolution(self.api_type, self.api_sub_type, self.unique_id)
