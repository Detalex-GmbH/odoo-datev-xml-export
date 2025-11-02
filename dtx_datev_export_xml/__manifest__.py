# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

# Part of Detalex. See LICENSE file for full copyright and licensing details.
{
    'name': 'DATEV XML Export',
    'version': '18.0.1.0',
    'category': 'Accounting/Localizations',
    'summary': 'Advanced DATEV XML export for invoices and bills with digitized receipts',
    'description': """
        DATEV XML Export

        This addon provides advanced functionality for exporting invoices and bills to the German DATEV system
        using the modern XML interface format with digitized receipt support.

        Features:
        1. Complete DATEV XML export for invoices and bills
        2. Digitized receipt attachment handling
        3. Time-based and individual export capabilities
        4. Magic buttons for exported invoice navigation
        5. DATEV validation with error handling
        6. Automatic PDF merging for multiple attachments
        7. Comprehensive export tracking and monitoring
        8. Integration with DATEV Unternehmen Online

        DATEV XML interface provides structured accounting data transfer and is the modern
        replacement for ASCII-based exports, offering better validation and receipt handling.

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

        History:
        - 18.0.1.0: Unified version with magic button validation features, comprehensive documentation
        - 18.0.0.13: Magic Button for DATEV validation errors with animation and group restrictions
        - 18.0.0.12: Refactoring of datev_cost_category, improved test coverage
        - 18.0.0.11: Removed datev_export_state field and related references
        - 18.0.0.10: Cleaned up posting text and short description of invoice lines
        - 18.0.0.9: Bug fixes in tests and translations
        - 18.0.0.8: Adjustments to datev_exported field and pluralization
        - 18.0.0.7: Bug fix in tests with new PDF merging logic
        - 18.0.0.6: Multiple PDF attachments merged, renamed customer/vendor exports
        - 18.0.0.5: Added XML validation before export
        - 18.0.0.4: Added DATEV XML export menu to accountant menu
        - 18.0.0.3: Moved DATEV XML export menu to Apps menu
        - 18.0.0.2: Bug fix in invoices Smart Button
        - 18.0.0.1: Added DATEV XML export menu to main menu
        - 18.0.0.0: Migration to Odoo 17

    """,
    'author': 'Detalex GmbH, Dietmar Hamm (hamm@detalex.de)',
    'website': 'https://detalex.de',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'dtx_datev_export',
        'account',
        'stock',
        'l10n_de',
        'contacts',
    ],
    'data': [
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
    'images': [
        'static/description/cover.png',
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
