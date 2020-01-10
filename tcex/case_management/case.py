# -*- coding: utf-8 -*-
"""ThreatConnect Case"""
from .assignee import Assignee, User, Users
from .api_endpoints import ApiEndpoints
from .artifact import Artifact, Artifacts
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .note import Note, Notes
from .tag import Tag, Tags
from .task import Task, Tasks
from .tql import TQL


class Cases(CommonCaseManagementCollection):
    """Case Class for Case Management Collection

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties"""
        super().__init__(
            tcex, ApiEndpoints.CASES, initial_response=initial_response, tql_filters=tql_filters
        )

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        """Map a dict to a Artifact.

        Args:
            entity (dict): The Artifact data.

        Returns:
            CaseManagement.Case: A Case Object.
        """
        return Case(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterCase Object."""
        return FilterCase(self.tql)


class Case(CommonCaseManagement):
    """Unique API calls for Artifact Type API Endpoints

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        artifacts (dict, kwargs): The Artifacts for the Case.
        created_by (dict, kwargs): The Created By data for the Case.
        date_added (date, kwargs): The Date Added for the Case.
        description (str, kwargs): The Description for the Case.
        name (str, kwargs): The Name for the Case.
        notes (dict, kwargs): The Notes for the Case.
        resolution (string, kwargs): The Resolution for the Case.
        severity (str, kwargs): The Severity for the Case.
        status (str, kwargs): The Status for the Case.
        tasks (dict, kwargs): The Tasks for the Case.
        tags (dict, kwargs): The Tags for the case.
        xid (str, kwargs): The unique XID (external ID) for the Case.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.CASES, kwargs)
        case_filter = [
            {'keyword': 'caseid', 'operator': TQL.Operator.EQ, 'value': self.id, 'type': 'integer'}
        ]

        self._artifacts = Artifacts(
            self.tcex, kwargs.get('artifacts', None), tql_filters=case_filter
        )
        self._assignee = self.assignee_builder(kwargs.get('assignee'))
        self._created_by = User(**kwargs.get('created_by', {}))
        self._date_added = kwargs.get('date_added', None)
        self._description = kwargs.get('description', None)
        self._name = kwargs.get('name', None)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}), tql_filters=case_filter)
        self._resolution = kwargs.get('resolution', None)
        self._severity = kwargs.get('severity', None)
        self._status = kwargs.get('status', None)
        self._tasks = Tasks(self.tcex, kwargs.get('tasks', {}), tql_filters=case_filter)
        self._tags = Tags(self.tcex, kwargs.get('tags', {}), tql_filters=case_filter)
        self._user_access = Users(kwargs.get('user_access', {}))
        self._xid = kwargs.get('xid', None)

    def add_artifact(self, **kwargs):
        """Add a Artifact to a Case."""
        self._artifacts.add_artifact(Artifact(self.tcex, **kwargs))

    def add_note(self, **kwargs):
        """Add a Note to a Case."""
        self._notes.add_note(Note(self.tcex, **kwargs))

    def add_tag(self, **kwargs):
        """Add a Tag to a Case."""
        self._tags.add_tag(Tag(self.tcex, **kwargs))

    def add_task(self, **kwargs):
        """Add a Task to a Case."""
        self._tasks.add_task(Task(self.tcex, **kwargs))

    @property
    def artifacts(self):
        """Return the Artifacts for the Case."""
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts):
        """Set the Artifacts for the Case."""
        self._artifacts = artifacts

    @property
    def assignee(self):
        """Return the Assignee for the Case."""
        return self._assignee

    @assignee.setter
    def assignee(self, assignee):
        """Set the Assignee for the Case."""
        self._assignee = self.assignee_builder(assignee)

    @staticmethod
    def assignee_builder(assignee):
        """Build the Assignee for the Case.

        Args:
            assignee (Assignee|dict): The Assignee data as dict or object.
        """
        if isinstance(assignee, dict):
            assignee = Assignee(type=assignee.get('type'), **assignee.get('data'))

        return assignee

    @property
    def as_entity(self):
        """Return the entity representation of the Case."""
        return {'type': 'Case', 'id': self.id, 'value': self.name}

    @property
    def available_fields(self):
        """Return the available fields to fetch for an Artifact."""
        return ['artifacts', 'events', 'notes', 'related', 'tags', 'tasks']

    @property
    def created_by(self):
        """Return the Created By for the Case."""
        return self._created_by

    @created_by.setter
    def created_by(self, created_by):
        """Set the Created By for the Case."""
        self._created_by = created_by

    @property
    def description(self):
        """Return the Description for the Case."""
        return self._description

    @description.setter
    def description(self, description):
        """Set the Description for the Case."""
        self._description = description

    @property
    def date_added(self):
        """Return the Date Added for the Case."""
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """Set the Date Added for the Case."""
        self._date_added = date_added

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = Case(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def name(self):
        """Return the Name for the Case."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the Name for the Case."""
        self._name = name

    @property
    def notes(self):
        """Return the Notes for the Case."""
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the Notes for the Case."""
        self._notes = notes

    @property
    def required_properties(self):
        """Return a list of required fields for an Artifact."""
        return ['name', 'severity', 'status']

    @property
    def resolution(self):
        """Return the Resolution for the Case."""
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """Set the Resolution for the Case."""
        self._resolution = resolution

    @property
    def severity(self):
        """Return the Severity for the Case."""
        return self._severity

    @severity.setter
    def severity(self, artifact_severity):
        """Set the Severity for the Case."""
        self._severity = artifact_severity

    @property
    def status(self):
        """Return the Status for the Case."""
        return self._status

    @status.setter
    def status(self, status):
        """Set the Status for the Case."""
        self._status = status

    @property
    def tags(self):
        """Return the Tags for the Case."""
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Set the Tags for the Case."""
        self._tags = tags

    @property
    def tasks(self):
        """Return the Tasks for the Case."""
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        """Set the Tasks for the Case."""
        self._tasks = tasks

    @property
    def user_access(self):
        """Return the User Access for the Case."""
        return self._user_access

    @user_access.setter
    def user_access(self, user_access):
        """Set the User Access for the Case."""
        self._user_access = user_access

    @property
    def xid(self):
        """Return the XID for the Case."""
        return self._xid

    @xid.setter
    def xid(self, xid):
        """Set the XID for the Case."""
        self._xid = xid


class FilterCase:
    """Filter Object for Case

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self._tql = tql

    def created_by(self, operator, created_by):
        """Filter objects based on "create by" field.

        Args:
            operator (enum): The enum for the required operator.
            created_by (int): The filter value.
        """
        self._tql.add_filter('createdby', operator, created_by)

    def created_by_id(self, operator, created_by_id):
        """Filter objects based on "create by id" field.

        Args:
            operator (enum): The enum for the required operator.
            created_by_id (int): The filter value.
        """
        self._tql.add_filter('createdbyid', operator, created_by_id, TQL.Type.INTEGER)

    def description(self, operator, description):
        """Filter objects based on description field.

        Args:
            operator (enum): The enum for the required operator.
            description (str]): The filter value.
        """
        self._tql.add_filter('description', operator, description)

    def hasartifact(self, operator, artifact_id):
        """Filter objects based on "artifact id" field.

        Args:
            operator (enum): The enum for the required operator.
            artifact_id (str): The filter value.
        """
        self._tql.add_filter('hasartifact', operator, artifact_id, TQL.Type.INTEGER)

    def hastag(self, operator, tag):
        """Filter objects based on tag field.

        Args:
            operator (enum): The enum for the required operator.
            tag (str): The filter value.
        """
        self._tql.add_filter('hastag', operator, tag)

    def hastask(self, operator, task):
        """Filter objects based on task field.

        Args:
            operator (enum): The enum for the required operator.
            task (str): The filter value.
        """
        self._tql.add_filter('hastask', operator, task)

    def id(self, operator, case_id):
        """Filter objects based on id field.

        Args:
            operator (enum): The enum for the required operator.
            case_id (int): The filter value.
        """
        self._tql.add_filter('id', operator, case_id, TQL.Type.INTEGER)

    def owner_name(self, operator, owner_name):
        """Filter objects based on "owner name" field.

        Args:
            operator (enum): The enum for the required operator.
            owner_name (str): The filter value.
        """
        self._tql.add_filter('ownername', operator, owner_name)

    def name(self, operator, name):
        """Filter objects based on name field.

        Args:
            operator (enum): The enum for the required operator.
            name (str): The filter value.
        """
        self._tql.add_filter('name', operator, name)

    def resolution(self, operator, resolution):
        """Filter objects based on resolution field.

        Args:
            operator (enum): The enum for the required operator.
            resolution (str): The filter value.
        """
        self._tql.add_filter('resolution', operator, resolution)

    def severity(self, operator, severity):
        """Filter object based on severity field.

        Args:
            operator (enum): The enum for the required operator.
            severity (str): The filter value.
        """
        self._tql.add_filter('severity', operator, severity)

    def status(self, operator, status):
        """Filter objects based on status field.

        Args:
            operator (enum): The enum for the required operator.
            status (str): The filter value.
        """
        self._tql.add_filter('status', operator, status)

    def tag(self, operator, tag):
        """Filter objects based on tag field.

        Args:
            operator (enum): The enum for the required operator.
            tag (str): The filter value.
        """
        self._tql.add_filter('tag', operator, tag)

    def target_id(self, operator, target_id):
        """Filter objects based on "target id" field.

        Args:
            operator (enum): The enum for the required operator.
            target_id (str): The filter value.
        """
        self._tql.add_filter('targetid', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator, target_type):
        """Filter objects based on "target type" field.

        Args:
            operator (enum): The enum for the required operator.
            target_type (str): The filter value.
        """
        self._tql.add_filter('targettype', operator, target_type)

    def xid(self, operator, xid):
        """Filter objects based on xid field.

        Args:
            operator (enum): The enum for the required operator.
            xid (str): The filter value.
        """
        self._tql.add_filter('xid', operator, xid)