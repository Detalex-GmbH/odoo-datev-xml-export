# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountAccount(models.Model):
    _inherit = "account.account"

    datev_code = fields.Integer(
        string="DATEV Code",
        compute="_compute_datev_code",
        store=True,
        help="Account code converted to integer for DATEV export. Returns 0 if conversion is not possible."
    )

    @api.depends('code')
    def _compute_datev_code(self):
        """Convert account code to integer for DATEV export.

        Examples:
        - '4000' -> 4000
        - '000234' -> 234
        - '0000' -> 0
        - 'ABC123' -> 0
        - '' -> 0
        """
        for account in self:
            try:
                # Strip whitespace and try to convert code to integer
                if account.code and account.code.strip():
                    # int() automatically handles leading zeros
                    account.datev_code = int(account.code.strip())
                else:
                    account.datev_code = 0
            except (ValueError, TypeError):
                # If conversion fails (e.g., contains letters), set to 0
                account.datev_code = 0
