.. GoIT Python Web HW 012 documentation master file, created by
   sphinx-quickstart on Sat Feb  8 19:34:52 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GoIT Python Web HW 012 documentation
====================================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.


Rest API Contacts Manager documentation
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Rest API Contacts Manager main
==============================

Main FastAPI Application Entry Point
-----------------------------------

This module serves as the main entry point for the FastAPI application. It sets up the application with necessary middleware and routers, and defines the base application configuration.

Features
--------

* CORS Middleware configuration for handling Cross-Origin Resource Sharing
* Rate limiting implementation using slowapi
* API routers for different endpoints:
    - /api/utils - Utility endpoints
    - /api/contacts - Contact management endpoints
    - /api/auth - Authentication endpoints
    - /api/users - User management endpoints

Endpoints
---------

``GET /``
    Root endpoint that returns a welcome message.

    **Returns:**
        dict: Contains a welcome message

Configuration
-------------

The application is configured with the following settings:

* CORS is enabled for localhost:8000
* Rate limiting is implemented to prevent abuse
* Multiple workers (4) for better performance
* Debug mode enabled with auto-reload

.. automodule:: main
  :members:
  :undoc-members:
  :show-inheritance:

Rest API Contacts Manager API Auth
==================================

Authentication API endpoints for user registration, login, and email confirmation.

This module provides FastAPI routes for handling user authentication operations including:

* User registration with email confirmation
* User login with JWT token generation
* Email confirmation request and verification

Endpoints
---------

``POST /auth/register``
    Register a new user and send confirmation email.

    **Request Body:**
        - email (str): User's email address
        - username (str): Desired username
        - password (str): User's password

    **Returns:**
        User object of the created user

    **Raises:**
        - HTTPException (409): If user with provided email or username already exists

``POST /auth/login``
    Authenticate user and generate access token.

    **Request Body (form):**
        - username (str): User's username
        - password (str): User's password

    **Returns:**
        Token object containing JWT access token

    **Raises:**
        - HTTPException (401): If login credentials are invalid or email is not confirmed

``POST /auth/request_email``
    Request email confirmation to be sent again.

    **Request Body:**
        - email (str): Email address to resend confirmation

    **Returns:**
        Message indicating the status of the request

``GET /auth/confirmed_email/{token}``
    Confirm user's email address using the provided token.

    **Parameters:**
        - token (str): Email confirmation token

    **Returns:**
        Message indicating the confirmation status

    **Raises:**
        - HTTPException (400): If verification fails or token is invalid

Authentication
--------------

All protected endpoints require a valid JWT token in the Authorization header:

.. code-block:: text

    Authorization: Bearer <token>

The token can be obtained by logging in through the ``/auth/login`` endpoint.

.. automodule:: src.api.auth
  :members:
  :undoc-members:
  :show-inheritance:
  
Rest API Contacts Manager API Contacts
======================================
  .. automodule:: src.api.contacts
    :members:
    :undoc-members:
    :show-inheritance:

Rest API Contacts Manager API Utils
===================================
.. automodule:: src.api.utils
  :members:
  :undoc-members:
  :show-inheritance:


Rest API Contacts Manager Database Models
=========================================
.. automodule:: src.database.models
  :members:
  :undoc-members:
  :show-inheritance:


Rest API Contacts Manager repository Contacts
=============================================
.. automodule:: src.repository.contacts
  :members:
  :undoc-members:
  :show-inheritance:

Rest API Contacts Manager repository Users
===========================================
.. automodule:: src.repository.users
  :members:
  :undoc-members:
  :show-inheritance:

Rest API Contacts Manager Services Auth
=======================================
.. automodule:: src.services.auth
  :members:
  :undoc-members:
  :show-inheritance:

Rest API Contacts Manager Services Contacts
===========================================
.. automodule:: src.services.contacts
  :members:
  :undoc-members:
  :show-inheritance:

Rest API Contacts Manager Services Users
========================================
.. automodule:: src.services.users
  :members:
  :undoc-members:
  :show-inheritance:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`