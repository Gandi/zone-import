#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gandi.net zone import script

Imports RFC1035 zone files into your account.

You will need to provide your Gandi API key

Zones will be named after the text file they come from

Be warned that there is currently no duplicate check, so using this script
multiple times will result in the same zone names being created

"""
from __future__ import unicode_literals, print_function

import sys
import argparse

from xmlrpclib import ServerProxy, Fault


USAGE = 'Imports RFC1035 zone files into your Gandi.net account, ' \
        'using your API KEY'

REMOTE = None  # ServerProxy
RPC = {
    'production': 'https://rpc.gandi.net/xmlrpc/',
    'ote': 'https://rpc.ote.gandi.net/xmlrpc/',
}


def main():
    global REMOTE

    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument('-k', '--key',
        help='Your API key. Will be asked for if not provided.')
    parser.add_argument('--ote', action='store_true',
        help='Use OT&E environment, for testing')
    parser.add_argument('files', type=argparse.FileType('r'),
        nargs='+', help='Zones files you wish to import')
    args = parser.parse_args()

    target = 'ote' if args.ote else 'production'
    if not args.key:
        args.key = raw_input('Enter API Key (%s): ' % target)

    REMOTE = ServerProxy(RPC[target])

    check_apikey(args.key)

    for file_ in args.files:
        try:
            import_zone(args.key, file_)
        finally:
            file_.close()


def check_apikey(apikey):
    """
    Checks that API key is valid using a dummy call

    """
    try:
        REMOTE.domain.zone.count(apikey, {'name': '-dummy-'})
    except Fault as fault:
        # Invalid format / non-existant key
        if fault.faultCode in (501237, 510150):
            print('Your API key seems invalid', file=sys.stderr)
            sys.exit(1)
        raise


# Lazy colors
def green(string):
    return '\x1b[0;32m%s\x1b[0;m' % string


def red(string):
    return '\x1b[0;31m%s\x1b[0;m' % string


def import_zone(apikey, file_):
    """
    Import a zone file to current REMOTE server

    """

    zone_name = file_.name
    contents = file_.read()

    sys.stdout.write('* %s (%d line(s)) ' % (zone_name, contents.count('\n')))
    sys.stdout.flush()

    zone = None
    try:
        zone = REMOTE.domain.zone.create(apikey, {'name': zone_name})
        version = REMOTE.domain.zone.version.new(apikey, zone['id'], 1)

        records = REMOTE.domain.zone.record.set(apikey, zone['id'],
                                                version, contents)

        # Set current version & remove useless one
        REMOTE.domain.zone.version.set(apikey, zone['id'], version)
        REMOTE.domain.zone.version.delete(apikey, zone['id'], 1)

        print(green('OK'), '(id=%d, %d records)' % (zone['id'], len(records)))
    except Fault as fault:
        print(red('FAILED'), fault.faultString)

        # Try to not pollute zones
        if zone and zone['id']:
            REMOTE.domain.zone.delete(apikey, zone['id'])

if __name__ == '__main__':
    main()
