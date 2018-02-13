#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import os.path
import sys
import json

from sentry.runner import configure, call_command
from sentry.models import (
    Team, Project, ProjectKey, User, Organization, OrganizationMember,
    OrganizationMemberTeam
)
from django.core.management import load_command_class
from django.utils.encoding import force_text
from django.core.exceptions import ObjectDoesNotExist


def _configure():
    # Add the project to the python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
    # Disable backend validation
    # os.environ['SENTRY_SKIP_BACKEND_VALIDATION'] = 1
    configure()


def _dj_call_command(command_name, *args, **options):
    try:
        command = load_command_class('django.core', command_name)
    except ImportError:
        return None
    parser = command.create_parser('', command_name)
    # Use the `dest` option name from the parser option

    if hasattr(parser, '_actions'):
        opt_mapping = {
            min(s_opt.option_strings).lstrip('-').replace('-', '_'): s_opt.dest
            for s_opt in parser._actions if s_opt.option_strings
        }
    else:
        opt_mapping = {}

    arg_options = {opt_mapping.get(key, key): value for key, value in options.items()}
    defaults = parser.parse_args(args=[force_text(a) for a in args])
    if hasattr(defaults, '_get_kwargs'):
        defaults = dict(defaults._get_kwargs(), **arg_options)
    else:
        defaults = dict(**arg_options)
    # Move positional args out of options to mimic legacy optparse
    args = defaults.pop('args', ())
    if 'skip_checks' not in options:
        defaults['skip_checks'] = True

    return command.execute(*args, **defaults)


def upgrade():
    """
    Run migrations
    """
    _configure()
    _dj_call_command(
        'syncdb',
        database='default',
        interactive=False,
        traceback=True,
        verbosity=1,
    )
    _dj_call_command(
        'migrate',
        merge=True,
        ignore_ghost_migrations=True,
        interactive=False,
        traceback=True,
        verbosity=1,
    )


def loaddata():
    with open('initial_data.json') as data_file:
        structure = json.load(data_file)
    organization = Organization.objects.get(pk=1)
    for record in structure:
        try:
            team = Team.objects.get(name=record['team'],
                                    organization=organization)
        except ObjectDoesNotExist:
            team = Team()
            team.name = record['team']
            team.organization = organization
            team.save()
        try:
            project = Project.objects.get(name=record['project'], team=team,
                                          organization=organization)
        except ObjectDoesNotExist:
            project = Project()
            project.team = team
            project.name = record['project']
            project.organization = organization
            project.save()
        key = ProjectKey.objects.filter(project=project)[0]
        if 'key' in record:
            parts = record['key'].split(':')
            key.public_key = parts[0]
            if len(parts) > 1:
                key.secret_key = parts[1]
            key.save()
        print 'PROJECT_NAME = "%s"' % (project.name,)
        print 'SENTRY_DSN = "%s"' % (key.get_dsn(),)
        print ''
