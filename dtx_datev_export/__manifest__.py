# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License LGPL-3

# Part of Detalex. See LICENSE file for full copyright and licensing details.

{
    'name': 'DATEV Export',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'author': 'Detalex GmbH',
    'website': 'https://detalex.de',
    'support': 'support@detalex.de',
    'summary': 'German accounting export interface for DATEV system',
    'description': """
DATEV Export

This addon provides the foundation for exporting accounting data to the German DATEV system, which is the leading accounting software in Germany.

Features:
- Base DATEV export infrastructure
- CSV export format support
- Configuration management for DATEV export
- Invoice and bill export functionality
- Integration with Odoo accounting modules
- Error handling and validation
- Export history tracking
- GDPR compliant data handling
- GoBD (Grundsätze ordnungsmäßiger Buchführung) ready

The DATEV system is used by over 500,000 accounting firms, tax advisors, and companies in Germany, Austria, and Switzerland for comprehensive accounting and tax services.

Technical Details:
- Extends account.move with DATEV export functionality
- Provides datev.export model for export management
- CSV generation with proper formatting
- Export state tracking and error management
- Configurable export settings per company

Limitations:
- Does not support pure G/L account postings
- No master data transfer for business partners

Requirements:
- This module provides base functionality; advanced features require dtx_datev_export_xml
- Appropriate DATEV subscription and account required
- German Chart of Accounts (SKR04/SKR03) recommended
    """,
    'depends': [
        'base',
        'account',
        'web',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/datev_configuration.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/datev_export_views.xml',
        'views/menuitems.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
