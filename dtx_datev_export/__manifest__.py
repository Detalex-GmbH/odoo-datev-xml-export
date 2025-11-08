# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

# Part of Detalex. See LICENSE file for full copyright and licensing details.
{
    'name': 'DATEV Export Base',
    'version': '17.0.1.2',
    'category': 'Hidden/Technical',
    'summary': 'Base module for German DATEV accounting system exports',
    'description': """
        DATEV Export Base

        This addon provides the base functionality for exporting accounting data to the German DATEV system.

        Features:
        1. DATEV consultant and client number configuration
        2. Base models for DATEV export functionality
        3. Account move line extensions for DATEV tax handling
        4. Automatic VAT detection for in/outbound invoices
        5. Company-specific DATEV configuration settings

        DATEV is a widely used accounting software in Germany and this module provides
        the foundation for various DATEV export functionalities required for German localization.

        Technical Details:
        - Extends res.company with DATEV numbers
        - Extends res.config.settings for easy configuration
        - Extends account.move.line with DATEV-specific tax automation
        - Provides base structure for DATEV export modules

        History:
        - 17.0.1.2: UI improvements and help text enhancements
        - 17.0.1.1: Added BU-Code (Buchungsschlüssel) field and documentation, fixed GitHub links
        - 17.0.1.0: Initial Odoo 17 version

        History:
        - 17.0.1.0: Initial version with base DATEV functionality

    """,
    'author': 'Detalex GmbH, Dietmar Hamm (hamm@detalex.de)',
    'website': 'https://detalex.de',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'account',
        'l10n_de',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
    'application': False,
}
