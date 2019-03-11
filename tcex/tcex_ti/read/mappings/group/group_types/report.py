from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group



class Report(Group):
    """ThreatConnect Batch Report Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_name (str, kwargs): The name for the attached file for this Group.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                                               file content.
            publish_date (str, kwargs): The publish datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super(Report, self).__init__(tcex, 'reports')
        # file data/content to upload

    def file_content(self, file_content, update_if_exists=True):
        """Set Document or Report file data."""

        self._data['fileContent'] = file_content
        request = self._base_request()
        request['fileContent'] = file_content
        request['update_if_exists'] = update_if_exists
        return self._tc_requests._upload(request)

    def file_name(self, file_name):
        """Return Email to."""
        self._data['fileName'] = file_name
        request = self._base_request()
        request['fileName'] = file_name
        return self._tc_requests.update(request)

    def file_size(self, file_size):
        """Return Email to."""
        self._data['fileSize'] = file_size
        request = self._base_request()
        request['fileSize'] = file_size
        return self._tc_requests.update(request)

    def status(self, status):
        """Return Email to."""
        self._data['status'] = status
        request = self._base_request()
        request['status'] = status
        return self._tc_requests.update(request)

    def malware(self, malware, password, file_name):
        self._data['malware'] = malware
        self._data['password'] = password
        self._data['fileName'] = file_name
        request = self._base_request()
        request['malware'] = malware
        request['password'] = password
        request['fileName'] = file_name
        return self._tc_requests.update(request)

    def publish_date(self, publish_date):
        """Return Email to."""
        publish_date = self._utils.format_datetime(
            publish_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

        self._data['publishDate'] = publish_date
        request = self._base_request()
        request['publishDate'] = publish_date
        return self._tc_requests.update(request)

