# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary
# pylint: disable=invalid-name
# pylint: disable=no-self-argument
# pylint: disable=expression-not-assigned

from datetime import timedelta

from odoo import fields
from odoo.addons.dtx_datev_export_xml.tests.test_base import TestBase
from odoo.tests import tagged


@tagged('post_install', '-at_install', 'dtx_datev_export_xml')
class TestDatevExport(TestBase):

    def setUp(cls):
        super().setUp()

        cls.InvoiceObj = cls.env["account.move"]
        cls.DatevExportObj = cls.env["datev.export.xml"]
        cls.customer_de = cls.partner_DE
        cls.today = fields.Date.today()
        cls.start_date = cls.today - timedelta(days=34)
        cls.end_date = cls.today - timedelta(days=32)

    def create_invoice(self, datev_export_ids=False):
        return self.InvoiceObj.create(
            {
                "partner_id": self.customer_de.id,
                "user_id": self.env.user.id,
                "invoice_date": self.start_date,
                "invoice_date_due": self.end_date,
                "company_id": self.env.company.id,
                "currency_id": self.env.company.currency_id.id,
                "move_type": "out_invoice",
                "payment_reference": "Payment Reference",
                "ref": "Customer Reference",
                "datev_export_ids": (
                    [(6, 0, datev_export_ids)] if datev_export_ids else False
                ),
            }
        )

    def test_create_invoice_and_link_datev_export_xml__record_linked(self):
        datev_export = self.DatevExportObj.create({})
        invoice = self.create_invoice()
        self.assertFalse(invoice.datev_export_ids)
        invoice.write(
            {
                "datev_export_ids": [(6, 0, datev_export.ids)],
            }
        )
        self.assertEqual(invoice.datev_export_ids.ids, datev_export.ids)

    def test_create_invoice_with_datev_export_xml_and_unlink__record_unlinked(self):
        datev_export = self.DatevExportObj.create({})
        invoice = self.create_invoice(datev_export_ids=datev_export.ids)
        invoice.datev_export_ids = False
        self.assertFalse(invoice.datev_export_ids)

    def test_compute_invoice_datev_exported_with_no_export__datev_exported_false(self):
        invoice = self.create_invoice()
        self.assertFalse(invoice.datev_exported)

    def test_compute_invoice_datev_exported_with_one_export__datev_exported_true(self):
        datev_export = self.DatevExportObj.create({})
        invoice = self.create_invoice(datev_export_ids=datev_export.ids)
        self.assertTrue(invoice.datev_exported)

    def test_compute_invoice_datev_exported_with_many_exports__datev_exported_true(
        self,
    ):
        datev_exports = self.DatevExportObj.create([{}, {}, {}])
        invoice = self.create_invoice(datev_export_ids=datev_exports.ids)
        self.assertTrue(invoice.datev_exported)

    def test_compute_invoice_datev_exported_with_one_export_and_unlink__datev_exported_changed(
        self,
    ):
        datev_export = self.DatevExportObj.create({})
        invoice = self.create_invoice(datev_export_ids=datev_export.ids)
        self.assertTrue(invoice.datev_exported)
        invoice.datev_export_ids = False
        self.assertFalse(invoice.datev_exported)
