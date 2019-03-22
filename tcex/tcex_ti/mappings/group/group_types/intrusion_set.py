# -*- coding: utf-8 -*-
"""ThreatConnect TI Intrusion Set """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class IntrusionSet(Group):
    """Unique API calls for IntrustionSet API Endpoints"""

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super(IntrusionSet, self).__init__(tcex, 'intrusionSets', name, **kwargs)
        self.api_entity = 'intrusionSet'
