# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    datev_consultant_number = fields.Char(
        related="company_id.l10n_de_datev_consultant_number",
        readonly=False,
    )

    datev_client_number = fields.Char(
        related="company_id.l10n_de_datev_client_number",
        readonly=False,
    )
