# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

# Part of Detalex. See LICENSE file for full copyright and licensing details.
{
    'name': 'DATEV XML Export',
    'version': '17.0.1.3.0',
    'category': 'Accounting/Localizations',
    'summary': 'Advanced DATEV XML export for invoices and bills with digitized receipts',
    'author': 'Detalex GmbH, Dietmar Hamm (hamm@detalex.de)',
    'website': 'https://detalex.de/odoo-datev',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'dtx_datev_export',
        'account',
        'stock',
        'l10n_de',
        'contacts',
    ],
    'images': [
        'static/description/cover.gif',
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
