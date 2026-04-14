# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    datev_default_period = fields.Selection(
        [
            ("day", "Day"),
            ("week", "Week"),
            ("month", "Month"),
            ("year", "Year"),
        ],
        help="Used to get default values for start and stop date at DATEV XML Export!",
        default="week",
    )

    datev_vendor_order_ref = fields.Selection(
        [
            ("partner", "Partner Reference"),
            ("payment", "Payment Reference"),
        ],
        string="Vendor Order Reference",
        default="partner",
        required=True,
    )

    datev_customer_order_ref = fields.Selection(
        [
            ("partner", "Partner Reference"),
            ("payment", "Payment Reference"),
        ],
        string="Customer Order Reference",
        default="partner",
        required=True,
    )
