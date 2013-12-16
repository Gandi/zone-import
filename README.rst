============
Zone import
============

Imports a list of RFC1035_ zone files into a Gandi.net account.

You will need your account's API key (see http://wiki.gandi.net/en/xml-api/activate)

Usage
======

::

  python zone-import.py [-k apikey] [--ote] first-zone.txt second-zone.txt […]

Script will ask for your API key if not provided in arguments.

Each zone will be name from its file name.

Limitations
============

There is currently no check on the zone name, so running the script multiple times will currently create "duplicates" in your interface.

Requirements
=============

- python 2.7 standard library


.. _RFC1035: http://tools.ietf.org/html/rfc1035
