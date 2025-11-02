# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License LGPL-3

# Part of Detalex. See LICENSE file for full copyright and licensing details.

{
    'name': 'DATEV XML Export',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'license': 'LGPL-3',
    'author': 'Detalex GmbH',
    'website': 'https://detalex.de',
    'support': 'support@detalex.de',
    'summary': 'Advanced DATEV XML export for invoices and bills with digitized receipts',
    'description': """
DATEV XML Export

This addon provides advanced functionality for exporting invoices and bills to the German DATEV system using the modern XML interface format with digitized receipt support.

Features:
- Complete DATEV XML export for invoices and bills
- Digitized receipt attachment handling
- Time-based and individual export capabilities
- Magic buttons for exported invoice navigation
- DATEV validation with error handling
- Automatic PDF merging for multiple attachments
- Comprehensive export tracking and monitoring
- Integration with DATEV Unternehmen Online
- GDPR compliant data handling
- GoBD (Grundsätze ordnungsmäßiger Buchführung) ready

DATEV XML interface provides structured accounting data transfer and is the modern replacement for ASCII-based exports, offering better validation and receipt handling.

Technical Details:
- Extends account.move with DATEV XML export functionality
- Provides datev.export.xml model for export management
- XML/ZIP generation with XSD validation
- PDF processing and attachment handling
- Export state tracking and error management
- Magic button integration for UX enhancement

Limitations:
- Does not support pure G/L account postings
- No master data transfer for business partners
- Certain §13b UStG cases require manual handling

Requirements:
- This module requires connection to DATEV Unternehmen Online
- Requires appropriate DATEV subscription and configuration
- German Chart of Accounts (SKR04/SKR03) recommended
    """,
    'depends': [
        'base',
        'account',
        'web',
        'dtx_datev_export',
    ],
    'data': [
        'data/datev_mapping.xml',
        'data/ir_cron_data.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_invoice_view.xml',
        'views/datev_export_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
        'views/dtx_datev_export_xml_menuitems.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dtx_datev_export_xml/static/src/css/datev_magic_button.css',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
