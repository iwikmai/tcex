""" standard """
import json
import re
import time

""" third-party """

""" custom """
import tcex_resources as Resources


class TcExJob(object):
    """Job processing functionality for batch indicator adds and allows
    structured group additions.
    """

    def __init__(self, tcex):
        """Initialize class data

        Args:
            tcex (instance): An instance of TcEx class
        """
        self._tcex = tcex

        # containers
        self._file_occurrences = []
        self._group_cache = {}
        self._group_associations = []
        self._groups = []
        self._indicators = []

        # batch "bad" errors
        self._batch_failures = [
            b'would exceed the number of allowed indicators'
        ]

        # keep the batch_id
        self._indicator_batch_ids = []

    def batch_action(self, action):
        """Set the default batch action for argument parser.

        Args:
            action (string): Set batch job action
        """
        # TODO: THIS MIGHT BE WRONG, I NEED TO ASK BRACEY
        if action in ['Create', 'Delete']:
            self._tcex._parser.set_defaults(batch_action=action)

    def batch_chunk(self, chunk_size):
        """Set batch chunk_size for argument parser.

        Args:
            chunk_size (integer): Set batch job chunk size
        """
        self._tcex._parser.set_defaults(batch_chunk=chunk_size)

    def batch_halt_on_error(self, halt_on_error):
        """Set batch halt on error boolean for argument parser.

        Args:
            halt_on_error (boolean): Boolean value for halt on error
        """
        if isinstance(halt_on_error, bool):
            self._tcex._parser.set_defaults(batch_halt_on_error=halt_on_error)

    def batch_poll_interval(self, interval):
        """Set batch polling interval for argument parser.

        Args:
            interval (integer): Seconds between polling
        """
        if isinstance(interval, int):
            self._tcex._parser.set_defaults(batch_poll_interval=interval)

    def batch_poll_interval_max(self, interval_max):
        """Set batch polling interval max for argument parser.

        Args:
            interval_max (integer): Max seconds before timeout on batch
        """
        if isinstance(interval_max, int):
            self._tcex._parser.set_defaults(batch_poll_interval_max=interval_max)

    def batch_write_type(self, write_type):
        """Set batch write type for argument parser.

        Args:
            write_type (string): Type of Append or Replace
        """
        if write_type in ['Append', 'Replace']:
            self._tcex._parser.set_defaults(batch_write_type=write_type)

    def batch_indicator_success(self):
        """Check completion for all batch jobs associated with this instance

        Returns:
            (dictionary): The status results from the Batch jobs.
        """

        status = {'success': 0, 'failure': 0, 'unprocessed': 0}

        resource = getattr(Resources, 'Batch')(self._tcex)
        resource.url = self._tcex._args.tc_api_path

        for batch_id in self._indicator_batch_ids:
            resource.batch_id(batch_id)
            results = resource.request()

            if (results.get('status') == 'Success' and
                'batchStatus' in results['data'] and
                results['data']['batchStatus'] == 'Completed'):

                status['success'] += results['data']['batchStatus']['successCount']
                status['failure'] += results['data']['batchStatus']['errorCount']
                status['unprocessed'] += results['data']['batchStatus']['unprocessCount']

        return status

    def batch_status(self, batch_id):
        """Check the status of a batch job

        This method will get the status of a Threatconnect API batch job.  If the batch
        job had any errors they will be automatically logged.

        Args:
            batch_id (int): Id of the batch job

        Returns:
            (boolean): Status of batch job.
        """
        status = False

        resource = getattr(Resources, 'Batch')(self._tcex)
        resource.url = self._tcex._args.tc_api_path
        resource.batch_id(batch_id)
        results = resource.request()

        self._tcex.log.info('batch id: {}'.format(batch_id))
        if results.get('status') == 'Success':
            if results['data']['status'] == 'Completed':
                status = True

                status_msg = 'Batch Job completed, totals: '
                status_msg += 'succeeded: {0}, '.format(results['data']['successCount'])
                status_msg += 'failed: {0}, '.format(results['data']['errorCount'])
                status_msg += 'unprocessed: {0}'.format(results['data']['unprocessCount'])
                self._tcex.log.info(status_msg)

                if results['data']['errorCount'] > 0:
                    self._tcex.exit_code(3)

                    resource = getattr(Resources, 'Batch')(self._tcex)
                    resource.url = self._tcex._args.tc_api_path
                    resource.errors(batch_id)
                    error_results = resource.request()

                    for error in json.loads(error_results['data']):
                        error_reason = error.get('errorReason')
                        for error_msg in self._batch_failures:
                            if re.findall(error_msg, error_reason):
                                # Critical Error
                                err = 'Batch Error: {0}'.format(error)
                                self._tcex.message_tc(err)
                                self._tcex.log.error(err)
                                self._tcex.exit(1)
                        self._tcex.log.warn('Batch Error: {0}'.format(error))
            else:
                self._tcex.log.debug('Batch Status: {}'.format(results['data']['status']))

        return status

    ## bcs - not rewriting this until I know what it is for.
    ## def get_batch_job(self, batch_id):
    ##     """what is this for?"""
    ##
    ##     batch_jobs = tc.batch_jobs()
    ##     batch_filter = batch_jobs.add_filter()
    ##     batch_filter.add_id(batch_id)

    ##     try:
    ##         batch_jobs.retrieve()
    ##     except RuntimeError as re:
    ##         self._tcex.log.error(re)
    ##         self._tcex.message_tc(re)

    ##     return batch_jobs

    def group(self, group):
        """Add group data to job

        This method will add group data to the group list.  No
        validation of the data will be performed.

        Required Data::

            {
                'name': 'adversary-001',
                'type': 'Adversary',
                'attribute': attributes,
                'tag': tags
            }

        Optional Data::

            {
                'name': 'incident-001',
                'type': 'Incident',
                'eventDate': '2015-03-7T00:00:00Z'
            }

        Args:
            group (dict | list): Dictionary or List containing group
                data
        """
        if isinstance(group, list):
            self._groups.extend(group)
        elif isinstance(group, dict):
            self._groups.append(group)

    def group_add(self, resource_type, resource_name, owner, data=None):
        """Add a group to ThreatConnect

        Args:
            resource_type (string): String with resource [group] type
            resource_name (string): The name of the group
            owner (string): The name of the TC owner for the group add
            data (Optional [dictionary]): Any optional group parameters, tags,
                or attributes

        Returns:
            (integer): The ID of the created resource
        """
        resource_id = None
        if data is None:
            data = {}

        self._tcex.log.debug(u'Adding {} "{}" in owner {}'.format(
            resource_type, resource_name, owner))
        resource_body = {'name': resource_name}
        resource = getattr(Resources, resource_type)(self._tcex)
        resource.http_method = 'POST'
        resource.owner = owner
        resource.url = self._tcex._args.tc_api_path

        # incident
        if 'eventDate' in data:
            resource_body['eventDate'] = data['eventDate']

        resource.body = json.dumps(resource_body)
        results = resource.request()

        if results.get('status') == 'Success':
            resource_id = results['data']['id']
            resource = getattr(Resources, resource_type)(self._tcex)
            resource.http_method = 'POST'
            resource.url = self._tcex._args.tc_api_path

            # add attributes
            if 'attributes' in data:
                for attribute in data['attributes']:
                    self._tcex.log.debug('Adding attribute type ({})'.format(attribute['type']))
                    resource.resource_id(resource_id)
                    resource.attribute()
                    resource.body = json.dumps(attribute)
                    results = resource.request()

            # add tags
            if 'tags' in data:
                for tag in data['tags']:
                    self._tcex.log.debug(u'Adding tag ({})'.format(tag))
                    resource.resource_id(resource_id)
                    resource.tag(tag)
                    results = resource.request()
        else:
            err = 'Failed adding group ({})'.format(resource_name)
            self._tcex.log.error(err)
            self._tcex.exit_code(3)

        return resource_id

    def group_association(self, associations):
        """Add group association data to job

        This method will add group association data to the group association
        list.  No validation of the data will be performed.

        Required Data::

            {
                'group_name': 'adversary-001',
                'group_type': 'Adversary',
                'indicator': '1.1.1.1',
                'indicator_type': 'Address'
            }

        Args:
            associations (dict | list): Dictionary or List containing group
                association data
        """
        if isinstance(associations, list):
            self._group_associations.extend(associations)
        elif isinstance(associations, dict):
            self._group_associations.append(associations)

    def group_cache(self, owner, resource_type):
        """Cache group data from TC

        The method will cache TC group data by owner and type.

        Args:
            owner (string): The name of the TC owner
            resource (dictionary): Dictonary containing resource parameters

        Returns:
            (dictionary): Dictionary of group resources
        """

        # already cached
        if owner in self._group_cache:
            if resource_type in self._group_cache[owner]:
                return self._group_cache[owner][resource_type]

        self._tcex.log.info(u'Caching group type {} for owner {}'.format(resource_type, owner))
        self._group_cache.setdefault(owner, {})
        self._group_cache[owner].setdefault(resource_type, {})

        resource = getattr(Resources, resource_type)(self._tcex)
        resource.owner = owner
        resource.url = self._tcex._args.tc_api_path
        results = resource.request()

        for group in results['data']:
            self._group_cache[owner][resource_type][group['name']] = group['id']

        return self._group_cache[owner][resource_type]

    def group_id(self, name, owner, resource_type):
        """Get the group id from the group cache

        Args:
            name(string): The name of the Group
            owner (string): The TC Owner where the resouce should be found
            resource (dictionary): Dictionary of resource parameters

        Returns:
            (dictionary): Dictionary containing group name and group id
        """
        group_id = None

        if owner not in self._group_cache:
            self.group_cache(owner, resource_type)
        elif resource_type not in self._group_cache[owner]:
            self.group_cache(owner, resource_type)

        if name in self._group_cache[owner][resource_type]:
            group_id = self._group_cache[owner][resource_type][name]

        return group_id

    @property
    def group_len(self):
        """The current length of the indicator list

        Returns:
            (integer): The lenght of the indicator list
        """
        return len(self._groups)

    def indicator(self, indicator):
        """Add indicator data to TcEx job.

        This method will add indicator data to the indicator list.  No
        validation of the data will be performed and duplicates will only
        be handle when a dict is provided.

        Example Structure::

            {
                'summary': '1.1.1.1',
                'type': 'Address',
                'rating': '3',
                'confidence': 5,
                'attribute': attributes,
                'tag': tags
            }

        Args:
            indicator (dict | list): Dictionary or List containing indicator
                data
        """
        if isinstance(indicator, list):
            self._indicators.extend(indicator)
        elif isinstance(indicator, dict):
            # verifiy indicator is not a duplicate before adding
            if indicator['summary'] not in self._indicators:
                self._indicators.append(indicator)

    @property
    def indicator_data(self):
        """Return the indicator list

        Returns:
            (list): The indicator list
        """
        return self._indicators

    @property
    def indicator_len(self):
        """The current length of the indicator list

        Returns:
            (integer): The length of the indicator list
        """
        return len(self._indicators)


    def _chunk_indicators(self):
        """Split indicator list into smaller more manageable numbers.

        """
        for i in xrange(0, len(self._indicators), self._tcex._args.batch_chunk):
            yield self._indicators[i:i+self._tcex._args.batch_chunk]

    def _process_file_occurrences(self, owner):
        """Process file occurrences and write to TC API

        Args:
            owner (string):  The owner name for the indicator to be written
        """
        resource = getattr(Resources, 'File')(self._tcex)
        resource.http_method = 'POST'
        resource.owner = owner
        resource.url = self._tcex._args.tc_api_path

        for occurrence in self._file_occurrences:

            resource.body = json.dumps({'fileName': occurrence['file_name']})
            # bcs - research and update this
            # supported format -> 2014-11-03T00:00:00-05:00
            # body['date'] = occurrence['file_date']
            # body['path'] = occurrence['path']
            resouce.occurrence(occurrence['indicator'])
            results = resource.request()

    def _process_group_association(self, owner):
        """Process groups and write to TC API

        Args:
            owner (string):  The owner name for the indicator to be written
        """
        for ga in self._group_associations:
            self._tcex.log.info(u'creating association: group {} indicator {}'.format(
                    ga['group_name'], ga['indicator']))

            group_id = self.group_id(ga['group_name'], owner, ga['group_type'])
            if group_id is None:
                continue

            resource = getattr(Resources, ga['indicator_type'])(self._tcex)
            resource.http_method = 'POST'
            resource.indicator(ga['indicator'])
            resource.owner = owner
            resource.url = self._tcex._args.tc_api_path

            association_resource = getattr(Resources, ga['group_type'])(self._tcex)
            resource.set_association(association_resource.api_uri, group_id)
            resource.request()

    def _process_groups(self, owner, duplicates=False):
        """Process groups and write to TC API

        Args:
            owner (string):  The owner name for the indicator to be written
        """
        for group in self._groups:
            cache = self.group_cache(owner, group['type'])

            if duplicates:
                # bcs - support duplicate groups
                pass
            elif group['name'] not in cache.keys():
                group_id = self.group_add(group['type'], group['name'], owner, group)
                if group_id is not None:
                    self._group_cache[owner][group['type']][group['name']] = group_id
                self._tcex.log.info(u'creating group {} [{}]'.format(
                    group['name'], group_id))

    def _process_indicators(self, owner):
        """Process batch indicators and write to TC API

        Args:
            owner (string):  The owner name for the indicator to be written
        """

        resource = getattr(Resources, 'Batch')(self._tcex)
        resource.http_method = 'POST'
        resource.url = self._tcex._args.tc_api_path

        batch_job_body = {
            'action': self._tcex._args.batch_action,
            'attributeWriteType': self._tcex._args.batch_write_type,
            'haltOnError': self._tcex._args.batch_halt_on_error,
            'owner': owner
        }

        for chunk in self._chunk_indicators():
            resource.content_type = 'application/json'
            resource.body = json.dumps(batch_job_body)
            results = resource.request()

            if results['status'] == 'Success':
                batch_id = results['data']

                resource.content_type = 'application/octet-stream'
                resource.batch_id(batch_id)
                resource.body = json.dumps(chunk)
                results = resource.request()

                # bcs - add a small delay before first status check then normal delay in loop
                time.sleep(3)

                poll_time = 0
                while True:
                    self._tcex.log.debug('poll_time: {0}'.format(poll_time))
                    if poll_time >= self._tcex._args.batch_poll_interval_max:
                        msg = 'Status check exceeded max poll time.'
                        self._tcex.log.error(msg)
                        self._tcex.message_tc(msg)
                        self._tcex.exit(1)

                    if self.batch_status(batch_id):
                        break

                    time.sleep(self._tcex._args.batch_poll_interval)

                    poll_time += self._tcex._args.batch_poll_interval

    def process(self, owner):
        """Process data and write to TC API

        Process each of the supported data types for this job.

        Args:
            owner (string): The owner name for the data to be written
        """
        if len(self._groups) > 0:
            self._tcex.log.info('Processing Groups')
            self._process_groups(owner)

        if len(self._indicators) > 0:
            self._tcex.log.info('Processing Indicators')
            self._process_indicators(owner)

        if len(self._file_occurrences) > 0:
            self._tcex.log.info('Processing File Occurrences')
            self._process_file_occurrences(owner)

        if len(self._group_associations) > 0:
            self._tcex.log.info('Processing Group Associations')
            self._process_group_association(owner)