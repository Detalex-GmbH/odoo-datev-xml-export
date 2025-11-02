# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    datev_default_period = fields.Selection(
        related="company_id.datev_default_period",
        readonly=False,
    )

    datev_vendor_order_ref = fields.Selection(
        related="company_id.datev_vendor_order_ref",
        readonly=False,
    )

    datev_customer_order_ref = fields.Selection(
        related="company_id.datev_customer_order_ref",
        readonly=False,
    )
