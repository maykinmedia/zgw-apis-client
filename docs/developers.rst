==========
Developers
==========

.. note:: The developer documentation is aimed at people contributing to this library
    itself, not for users of the library.

Principles
==========

When extending or making changes to the library, please keep the following guidelines in
mind:

* Every aspect of API input or output must be backed by a msgspec struct.
* Use the most appropriate available types in the Python domain.
* Be explicit in the expected input and return types.

Principles and goals
====================

While API documentation in the form of OpenAPI specifications is really nice to work with,
these specifications will and do contain mistakes and cannot be fully trusted. Additionally,
the actual API implementation can contain bugs that lead to unexpected interactions.

For this reason, we use ``msgspec`` to validate all incoming and outgoing data at the
edge - when we encode Python data types to JSON (typically) and send it to the API, or 
when we receive (JSON) data in the API responses. This introduces early (and hard) failure
when something is returned that we didn't expect, rather than passing a lie down the call
stack which results in hard-to-debug errors in places far away from where the actual API
call is made. 

The structure of the library is so that it closely resembles the API 
specification:

* Structs model the resource schemas, and (loosely) translate to the ``components``
  top-level key in OpenAPI.
* Resources model the useful information provided by the endpoints - they tend to follow
  the serializers of API operations, where an operation is the combination of an endpoint
  and an HTTP verb.
* On resources, we expose the client methods like ``list()``, ``retrieve()``,
  ``create()``... They follow the common RESTful actions available on resources.

Status
======

The library is far from feature complete at this point. Only the endpoints and resources
are added that will be actively used in downstream projects. If there's something missing
in the library that exists in the API and you need it, you can of course contribute that
feature. 
