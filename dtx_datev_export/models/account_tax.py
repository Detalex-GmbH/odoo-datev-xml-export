# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    # Note: The field l10n_de_datev_code is defined in l10n_de module.
    # We only modify its attributes through the view in account_tax_views.xml
    # to provide better labels and help text for German users.
