# -*- coding: utf-8 -*-
"""ThreatConnect TI Mutex"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class Mutex(Indicator):
    """Unique API calls for Mutex API Endpoints"""

    def __init__(self, tcex, mutex, **kwargs):
        """Initialize Class Properties.

        Args:
            mutex (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(Mutex, self).__init__(tcex, 'mutexes', **kwargs)
        self.data['mutex'] = mutex
        self.api_entity = 'mutex'

    def can_create(self):
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get('mutex'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """

        :param json_response:
        """
        self.unique_id = json_response.get('mutex', '')
