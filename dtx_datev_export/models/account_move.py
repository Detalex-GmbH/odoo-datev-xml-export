# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

from odoo import api, fields, models


class AccountAccount(models.Model):
    _inherit = "account.move.line"
    datev_vorsteuer_automatic = fields.Boolean(
        string="DATEV Vorsteuer Automatk",
        default=False,
        compute="_compute_datev_vorsteuer_automatic",
    )

    @api.depends("account_id")
    def _compute_datev_vorsteuer_automatic(self):
        move_is_outbound = self.move_id.move_type in ("out_invoice", "out_refund")
        move_is_inbound = self.move_id.move_type in ("in_invoice", "in_refund")
        for record in self:

            record.datev_vorsteuer_automatic = False

            if move_is_outbound and record.account_id.datev_vorsteuer_automatic:
                record.datev_vorsteuer_automatic = True

            if move_is_inbound and record.account_id.datev_umsatzsteuer_automatic:
                record.datev_vorsteuer_automatic = True
