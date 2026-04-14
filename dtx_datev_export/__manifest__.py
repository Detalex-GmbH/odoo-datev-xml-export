# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

# Part of Detalex. See LICENSE file for full copyright and licensing details.
{
    'name': 'DATEV Export Base',
    'version': '19.0.1.2.0',
    'category': 'Hidden/Technical',
    'summary': 'Base module for German DATEV accounting system exports',
    'author': 'Detalex GmbH, Dietmar Hamm (hamm@detalex.de)',
    'website': 'https://detalex.de/odoo-datev',
    'license': 'Other proprietary',
    'depends': [
        'base',
        'account',
        'l10n_de',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/account_tax_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': [
        'static/description/cover.gif',
    ],
    'auto_install': True,
}
