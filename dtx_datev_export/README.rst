==================
DATEV Export Base
==================

This addon provides the base functionality for exporting accounting data to the German DATEV system.

Features
========

1. DATEV consultant and client number configuration
2. Base models for DATEV export functionality
3. Account move line extensions for DATEV tax handling
4. Automatic VAT detection for in/outbound invoices
5. Company-specific DATEV configuration settings

DATEV is a widely used accounting software in Germany and this module provides
the foundation for various DATEV export functionalities required for German localization.

Technical Details
=================

- Extends res.company with DATEV numbers
- Extends res.config.settings for easy configuration
- Extends account.move.line with DATEV-specific tax automation
- Provides base structure for DATEV export modules

Version History
===============

- 17.0.1.2.0: UI improvements and help text enhancements
- 17.0.1.1: Added BU-Code (Buchungsschlüssel) field and documentation, fixed GitHub links
- 17.0.1.0: Initial Odoo 17 version with base DATEV functionality
