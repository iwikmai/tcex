#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""TcEx Framework Template Download/Generation Module."""
import os
import re

import colorama as c
import requests
from mako.template import Template

from ..utils import Utils

# autoreset colorama
c.init(autoreset=True, strip=False)


class CustomTemplates:
    """Custom method Template Class"""

    def __init__(self, profile, branch='master'):
        """Initialize class properties."""
        self.url = f'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex/{branch}/app_init'
        self.profile = profile

    @property
    def feature_template(self):
        """Return the feature template file for custom methods"""
        url = f'{self.url}/tests/custom_feature.py.tpl'
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError(f'Could not download template file ({url}).')
        return r.content

    @property
    def parent_template(self):
        """Return the parent template file for custom methods"""
        url = f'{self.url}/tests/custom.py.tpl'
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError(f'Could not download template file ({url}).')
        return r.content

    def render_templates(self):
        """Render the templates and write to disk conditionally."""
        variables = {'runtime_level': self.profile.ij.runtime_level.lower()}

        parent_file = os.path.join(self.profile.test_directory, 'custom.py')
        if not os.path.isfile(parent_file):
            template = Template(self.parent_template)
            rendered_template = template.render(**variables)
            with open(parent_file, 'a') as f:
                f.write(rendered_template)

        feature_file = os.path.join(self.profile.feature_directory, 'custom_feature.py')
        if not os.path.isfile(feature_file):
            template = Template(self.feature_template)
            rendered_template = template.render(**variables)
            with open(feature_file, 'a') as f:
                f.write(rendered_template)


class DownloadTemplates:
    """Template Download Module.

    Args:
        profile (Profile): An instance of Profile.
    """

    def __init__(self, branch, profile=None):
        """Initialize Class properties."""
        self.url = f'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex/{branch}/app_init'
        self.profile = profile

        # properties
        self._download_results = []
        self.utils = Utils()

    def print_download_results(self):
        """Print the download results."""
        if self._download_results:
            # get the max length of url
            destination_length = 0
            destination_max = 50
            url_length = 0
            for r in self._download_results:
                if len(r.get('destination')) > destination_length:
                    destination_length = min(len(r.get('destination')) + 5, destination_max)
                if len(r.get('url')) > url_length:
                    url_length = len(r.get('url')) + 5

            # title row
            print(
                f"{c.Style.BRIGHT}{c.Fore.CYAN}{'Download URL:'!s:<{url_length}}"
                f"{'Destination:'!s:<{destination_length}}"
                f"{'Status:'!s:<10}"
            )
            for r in self._download_results:
                destination = self._short_string(
                    r.get('destination'), length=(destination_length - 5)
                )
                status = r.get('status')
                url = r.get('url')

                # get status color
                status_color = f'{c.Style.BRIGHT}{c.Fore.RED}'
                if status == 'Success':
                    status_color = c.Fore.GREEN
                elif status == 'Skipped':
                    status_color = f'{c.Style.BRIGHT}{c.Fore.YELLOW}'

                # data row
                print(
                    f'{url!s:<{url_length}}'
                    f'{destination!s:<{destination_length}}'
                    f'{status_color}{status!s:<10}'
                )

    @staticmethod
    def _short_string(string, length=65, prepend_ellipsis=True):
        """Return a shortened destination."""
        ellipsis = ''
        if prepend_ellipsis and len(string) > length:
            ellipsis = '...'
            length -= len(ellipsis)
        return f'{ellipsis}{string[-length:]}'

    def download_file(self, url, destination, overwrite=False, default_choice='yes'):
        """Download the provided source file to the provided destination.

        Args:
            url (str): The full URL where the file can be downloaded.
            destination (str): The fully qualified path to the destination file.
            overwrite (bool, str): If True the file will be overwritten, if value
                is "prompt" the user will get prompted to choose.
            default_choice (str): The value for the default choice on the download prompt.
        """

        prompted = False
        if (
            not isinstance(overwrite, bool)
            and overwrite.lower() == 'prompt'
            and os.path.isfile(destination)
        ):
            overwrite = self.download_prompt(destination, default_choice)
            prompted = True

        status = 'Failed'
        if not os.path.isfile(destination) or overwrite is True:
            r = requests.get(url, allow_redirects=True)
            if not r.ok:
                raise RuntimeError(f'Could not download template file ({url}).')

            # write destination file
            open(destination, 'wb').write(r.content)
            status = 'Success'
        elif prompted:
            status = 'Skipped'
        else:
            print(f'{c.Fore.RED}Destination file {destination} already exists.')
            status = 'Skipped'

        self._download_results.append({'destination': destination, 'status': status, 'url': url})

    def download_prompt(self, destination, default_choice):
        """Present the download prompt for the user.

        Args:
            destination (str): The fully qualified path to the destination file.
            default_choice (str): The value for the default choice on the download prompt.

        Returns:
            bool: True if the user select yes.
        """
        option_text = self.download_prompt_option_text(default_choice)

        print(f"{c.Style.BRIGHT}{'File:'!s:<15}{c.Fore.CYAN}{self._short_string(destination)}")
        message = (
            f'{c.Fore.MAGENTA}Replace '
            f'{c.Style.BRIGHT}{c.Fore.WHITE}({option_text}):{c.Fore.RESET} '
        )
        response = input(message).strip()
        if not response:
            response = default_choice
        return self.utils.to_bool(response)

    @staticmethod
    def download_prompt_option_text(default_choice):
        """Return the default value and option text.

        Args:
            default_choice (str, optional): The default choice for the prompt.

        Returns:
            str: The options text string.
        """
        valid_values = ['yes', 'no']

        options = []
        for v in valid_values:
            # o = f'{c.Fore.YELLOW}{v}{c.Fore.RESET}'
            o = v
            if v.lower() == default_choice.lower():
                # o = f'{c.Fore.GREEN}[{v}]{c.Fore.RESET}'
                o = f'[{v}]'
            options.append(o)
        return f"{'/'.join(options)}"

    def init_common_files(self, template):
        """Download common files."""
        self.download_file(
            f'{self.url}/.pre-commit-config.yaml',
            destination='.pre-commit-config.yaml',
            overwrite=True,
        )
        self.download_file(
            url=f'{self.url}/coveragerc',
            destination='.coveragerc',
            overwrite='prompt',
            default_choice='yes',
        )
        self.download_file(
            url=f'{self.url}/gitignore',
            destination='.gitignore',
            overwrite='prompt',
            default_choice='yes',
        )
        self.download_file(
            url=f'{self.url}/pyproject.toml', destination='pyproject.toml', overwrite=True
        )
        self.download_file(
            url=f'{self.url}/README.md',
            destination='README.md',
            overwrite='prompt',
            default_choice='no',
        )
        self.download_file(
            url=f'{self.url}/requirements.txt',
            destination='requirements.txt',
            overwrite='prompt',
            default_choice='no',
        )
        self.download_file(url=f'{self.url}/setup.cfg', destination='setup.cfg', overwrite=True)
        self.download_file(
            f'{self.url}/{template}/app.py',
            destination='app.py',
            overwrite='prompt',
            default_choice='no',
        )
        if not template.startswith('external'):
            self.download_file(f'{self.url}/app_lib.py', destination='app_lib.py', overwrite=True)
            self.download_file(
                f'{self.url}/{template}/args.py',
                destination='args.py',
                overwrite='prompt',
                default_choice='no',
            )
            self.download_file(
                f'{self.url}/{template}/install.json',
                destination='install.json',
                overwrite='prompt',
                default_choice='no',
            )
            self.download_file(
                f'{self.url}/{template}/tcex.json',
                destination='tcex.json',
                overwrite='prompt',
                default_choice='no',
            )

    def init_external(self, template):
        """Download external App files."""
        self.download_file(
            f'{self.url}/external/external_app.py', destination='external_app.py', overwrite=True,
        )
        self.download_file(f'{self.url}/external/run.py', destination='run.py', overwrite=True)
        self.download_file(
            f'{self.url}/{template}/app_config.json',
            destination='app_config.json',
            overwrite=False,
        )

    def init_job(self):
        """Download job App files."""
        self.download_file(f'{self.url}/__main__.py', destination='__main__.py', overwrite=True)
        self.download_file(f'{self.url}/job/job_app.py', destination='job_app.py', overwrite=True)
        self.download_file(f'{self.url}/job/run.py', destination='run.py', overwrite=True)

    def init_playbook(self):
        """Download playbook App files."""
        self.download_file(f'{self.url}/__main__.py', destination='__main__.py', overwrite=True)
        self.download_file(
            f'{self.url}/playbook/playbook_app.py', destination='playbook_app.py', overwrite=True,
        )
        self.download_file(f'{self.url}/playbook/run.py', destination='run.py', overwrite=True)

    def init_service(self, template):
        """Download service App files."""
        self.download_file(
            f'{self.url}/service/service_app.py', destination='service_app.py', overwrite=True
        )
        self.download_file(f'{self.url}/service/run.py', destination='run.py', overwrite=True)
        self.download_file(f'{self.url}/{template}/run.py', destination='run.py', overwrite=True)

    def test_conftest_py(self):
        """Download the configtest.py file."""
        if not self.profile:
            raise RuntimeError('Download of "conftest.py" requires a Profile object.')
        url = f'{self.url}/tests/conftest.py'
        destination = os.path.join(self.profile.test_directory, 'conftest.py')
        self.download_file(url, destination, overwrite=True)

    def test_profiles_py(self):
        """Download the profiles.py file."""
        if not self.profile:
            raise RuntimeError('Download of "profiles.py" requires a Profile object.')
        url = f'{self.url}/tests/profiles.py'
        destination = os.path.join(self.profile.test_directory, 'profiles.py')
        self.download_file(url, destination, overwrite=True)


class TestProfileTemplates:
    """TestProfile Template Class"""

    def __init__(self, profile, branch='master'):
        """Initialize class properties."""
        self.url = f'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex/{branch}/app_init'
        self.profile = profile

    @property
    def app_class(self):
        """Return the proper App class based on runtime level."""
        app_type_to_class = {
            'organization': 'TestCaseJob',
            'playbook': 'TestCasePlaybook',
            'triggerservice': 'TestCaseTriggerService',
            'webhooktriggerservice': 'TestCaseWebhookTriggerService',
        }
        return app_type_to_class.get(self.profile.ij.runtime_level.lower())

    def render_template(self):
        """Render the templates and write to disk conditionally."""
        variables = {
            'class_name': self.app_class,
            'runtime_level': self.profile.ij.runtime_level.lower(),
        }

        test_profiles_file = os.path.join(self.profile.feature_directory, 'test_profiles.py')
        template = Template(self.test_profiles_template)
        rendered_template = template.render(**variables)
        with open(test_profiles_file, 'w') as f:
            f.write(rendered_template)

    @property
    def test_profiles_template(self):
        """Return template file"""
        url = f'{self.url}/tests/test_profiles.py.tpl'
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError(f'Could not download template file ({url}).')
        return r.content


class ValidationTemplates:
    """Validation Template Class

    Args:
        profile (Profile): An instance of the Profile object.
        branch (str, optional): The tcex git branch. Defaults to 'master'.

    Raises:
        NotImplementedError: The delete method is not currently implemented.
    """

    def __init__(self, profile, branch='master'):
        """Initialize class properties."""
        self.url = f'https://raw.githubusercontent.com/ThreatConnect-Inc/tcex/{branch}/app_init'
        self.profile = profile
        self._variable_match = re.compile(fr'^{self._variable_pattern}$')
        self._variable_parse = re.compile(self._variable_pattern)

    def _method_name(self, variable):
        """Convert variable name to a valid method name.

        Args:
            variable (string): The variable name to convert.

        Returns:
            (str): Method name
        """
        method_name = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self._variable_match, variable):
                var = re.search(self._variable_parse, variable)
                variable_name = var.group(3).replace('.', '_').lower()
                variable_type = var.group(4).lower()
                method_name = f'{variable_name}_{variable_type}'
        return method_name

    @property
    def _variable_pattern(self):
        """Regex pattern to match and parse a playbook variable."""
        variable_pattern = r'#([A-Za-z]+)'  # match literal (#App) at beginning of String
        variable_pattern += r':([\d]+)'  # app id (:7979)
        variable_pattern += r':([A-Za-z0-9_\.\-\[\]]+)'  # variable name (:variable_name)
        variable_pattern += r'!(StringArray|BinaryArray|KeyValueArray'  # variable type (array)
        variable_pattern += r'|TCEntityArray|TCEnhancedEntityArray'  # variable type (array)
        variable_pattern += r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'  # variable type
        variable_pattern += r'|(?:(?!String)(?!Binary)(?!KeyValue)'  # non matching for custom
        variable_pattern += r'(?!TCEntity)(?!TCEnhancedEntity)'  # non matching for custom
        variable_pattern += r'[A-Za-z0-9_-]+))'  # variable type (custom)
        return variable_pattern

    @property
    def custom_template(self):
        """Return template file"""
        url = f'{self.url}/tests/validate_custom.py.tpl'
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError(f'Could not download template file ({url}).')
        return r.content

    @property
    def feature_template(self):
        """Return template file"""
        url = f'{self.url}/tests/validate_feature.py.tpl'
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError(f'Could not download template file ({url}).')
        return r.content

    def output_data(self, output_variables):
        """Return formatted output data.

        variable format: #App:9876:http.content!Binary
        """
        output_data = []
        for ov in output_variables:
            output_data.append({'method': self._method_name(ov), 'variable': ov})
        return sorted(output_data, key=lambda i: i['method'])

    @property
    def parent_template(self):
        """Return template file"""
        url = f'{self.url}/tests/validate.py.tpl'
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise RuntimeError(f'Could not download template file ({url}).')
        return r.content

    def render_templates(self, overwrite=False):
        """Render the templates and write to disk conditionally."""
        variables = {
            'feature': self.profile.feature,
            'output_data': self.output_data(self.profile.ij.output_variable_array),
        }

        # render the parent "validate.py" template
        parent_file = os.path.join(self.profile.test_directory, 'validate.py')
        template = Template(self.parent_template)
        rendered_template = template.render(**variables)
        with open(parent_file, 'w') as f:
            f.write(rendered_template)

        # render the custom "validate_custom.py" template
        custom_file = os.path.join(self.profile.test_directory, 'validate_custom.py')
        if not os.path.isfile(custom_file) or overwrite:
            template = Template(self.custom_template)
            rendered_template = template.render(**variables)
            with open(custom_file, 'w') as f:
                f.write(rendered_template)

        # render the feature "validate_feature.py" template
        feature_file = os.path.join(self.profile.feature_directory, 'validate_feature.py')
        if not os.path.isfile(feature_file) or overwrite:
            template = Template(self.feature_template)
            rendered_template = template.render(**variables)
            with open(feature_file, 'w') as f:
                f.write(rendered_template)
