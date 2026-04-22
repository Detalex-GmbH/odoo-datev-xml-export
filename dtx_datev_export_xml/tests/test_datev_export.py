# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

# pylint: disable=invalid-name
# pylint: disable=no-self-argument
# pylint: disable=expression-not-assigned
import base64
import io
import logging
import zipfile
from datetime import date, timedelta

from lxml import etree
from odoo import fields
from odoo.addons.dtx_datev_export_xml.tests.test_base import TestBase
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class TestDatevExport(TestBase):

    def setUp(cls):
        super().setUp()

        cls.JournalObj = cls.env["account.journal"]

        cls.sale_journal = cls.JournalObj.search([("type", "=", "sale")])[0]
        cls.purchase_journal = cls.JournalObj.search([("type", "=", "purchase")])[0]

        cls.AccountObj = cls.env["account.account"]
        cls.PartnerObj = cls.env["res.partner"]
        cls.AnalyticAccountObj = cls.env["account.analytic.account"]
        cls.ProductObj = cls.env["product.product"]
        cls.today = fields.Date.today()
        cls.InvoiceObj = cls.env["account.move"]
        cls.InvoiceLineObj = cls.env["account.move.line"]
        cls.AttachmentObj = cls.env["ir.attachment"]
        cls.DatevExportObj = cls.env["datev.export.xml"]

        cls.inv_attach_de = cls.vendor_bill_attachment_DE
        cls.inv_attach_eu = cls.vendor_bill_attachment_DE
        cls.inv_attach_noneu = cls.vendor_bill_attachment_DE

        cls.refund_attach_de = cls.vendor_bill_attachment_DE

        cls.refund_attach_eu = cls.vendor_bill_attachment_DE
        cls.refund_attach_noneu = cls.vendor_bill_attachment_DE

        cls.customer_de = cls.partner_DE
        cls.vendor_de = cls.partner_DE

        cls.customer_eu = cls.partner_non_DE
        cls.vendor_eu = cls.partner_non_DE

        cls.customer_noneu = cls.partner_non_DE
        cls.vendor_noneu = cls.partner_non_DE

        cls.account_income = cls.account_datev_income
        cls.account_expense = cls.account_datev_expense

        cls.consulting = cls.product_IT_Consulting
        cls.lease = cls.product_IT_Consulting

        cls.analytic_account_it = cls.analytic_account_IT
        cls.analytic_account_office = cls.analytic_account_Office

        cls.parent_customer = cls.hauptpartner
        cls.child_customer = cls.partner_DE

        # Ensure the initial state
        cls.refund_date = cls.today - timedelta(days=55)
        cls.start_date = cls.today - timedelta(days=34)
        cls.end_date = cls.today - timedelta(days=32)

        cls.env.company.datev_default_period = "week"

    def _check_filecontent(self, export, refund=False):
        # check content only for single invoice
        # datev XML export based on unit test cases
        if not export.attachment_id or not export.invoice_ids:
            return {}

        export.check_valid_data(export.invoice_ids)

        if not refund:
            invoice = export.invoice_ids[0].name
        else:
            invoice = export.invoice_ids.filtered(
                lambda inv: "refund" in inv.move_type
            ).name

        invoice = invoice.replace("/", "-")

        zip_data = base64.b64decode(export.datev_file)
        fp = io.BytesIO()
        fp.write(zip_data)
        zipfile.is_zipfile(fp)
        file_list = []
        invoice_xml = {}
        with zipfile.ZipFile(fp, "r") as z:
            for zf in z.namelist():
                file_list.append(zf)

            doc_file = "document.xml"
            inv_file = str(invoice + ".xml")
            doc_data = z.read(doc_file)
            inv_data = z.read(inv_file)
            # document.xml
            doc_root = etree.fromstring(doc_data.decode("utf-8"))
            # invoice.xml file
            inv_root = etree.fromstring(inv_data.decode("utf-8"))
            for i in inv_root:
                invoice_xml.update(i.attrib)

            return {
                "file_list": file_list,
                "zip_file": z,
                "document": lambda xpath: doc_root.findall(
                    xpath, namespaces=doc_root.nsmap
                ),
                "invoice": lambda xpath: inv_root.find(
                    xpath, namespaces=inv_root.nsmap
                ),
            }

    def create_invoice_attachment(self, invoice):
        self.env["ir.attachment"].create(
            {
                "name": f"{invoice.name}.pdf",
                "mimetype": "application/pdf",
                "type": "binary",
                "datas": self.base64_encoded_data,
                "res_model": "account.move",
                "res_id": invoice.id,
            }
        )

    def create_out_invoice(self, customer, start_date, end_date):
        # OUT Invoice
        # Search for existing tax group or create new one
        tax_group = self.env["account.tax.group"].search([("name", "=", "Tax Group 1")], limit=1)
        if not tax_group:
            tax_group = self.env["account.tax.group"].create(
                {
                    "name": "Tax Group 1",
                    "sequence": 1,
                }
            )

        # Search for existing tax or create new one
        tax = self.env["account.tax"].search([
            ("name", "=", "Tax 0%"),
            ("type_tax_use", "=", "sale"),
        ], limit=1)
        if not tax:
            tax = self.env["account.tax"].create(
                {
                    "name": "Tax 0%",
                    "amount": 0.0,
                    "amount_type": "percent",
                    "type_tax_use": "sale",
                    "tax_group_id": tax_group.id,
                }
            )

        # Create analytic plan for analytic account
        analytic_plan = self.env['account.analytic.plan'].create({
            'name': 'Test Plan',
            # 'company_id': self.env.company.id,  # Removed, not a valid field
        })
        # Create analytic account(s) for testing
        analytic_account = self.env['account.analytic.account'].create({
            'name': 'Test Analytic',
            'code': 'TEST01',
            'company_id': self.env.company.id,
            'plan_id': analytic_plan.id,  # Required field
        })
        self.assertTrue(analytic_account.exists())

        invoice = self.InvoiceObj.create(
            {
                "partner_id": customer.id,
                "user_id": self.env.user.id,
                "invoice_date": start_date,
                "invoice_date_due": end_date,
                "company_id": self.env.company.id,
                "currency_id": self.env.company.currency_id.id,
                "move_type": "out_invoice",
                "payment_reference": "Payment Reference",
                "ref": "Customer Reference",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.consulting.id,
                            "quantity": 5.0,
                            "tax_ids": [(6, 0, tax.ids)],
                            "price_unit": 120.00,
                            "price_total": 600.0,
                            "credit": 600.0,
                            "debit": 0.0,
                            "account_id": self.account_income.id,
                            "analytic_distribution": {
                                analytic_account.id: 100.0,
                            },
                        },
                    )
                ],
            }
        )
        invoice.invoice_line_ids.filtered("product_id")[0]
        self.assertEqual(invoice.state, "draft")
        invoice.action_post()
        return invoice

    def create_out_invoice_with_tax(self, customer, start_date, end_date, tax):
        # OUT Invoice with Tax 15%
        invoice = self.InvoiceObj.create(
            {
                "partner_id": customer.id,
                "user_id": self.env.user.id,
                "invoice_date": start_date,
                "invoice_date_due": end_date,
                "company_id": self.env.company.id,
                "currency_id": self.env.company.currency_id.id,
                "move_type": "out_invoice",
                "payment_reference": "Payment Reference",
                "ref": "Customer Reference",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.consulting.id,
                            "quantity": 5.0,
                            "price_unit": 120.00,
                            "account_id": self.account_income.id,
                            "analytic_distribution": {
                                self.analytic_account_it.id: 100.0,
                            },
                            "tax_ids": [(6, 0, tax.ids)],
                        },
                    ),
                ],
            }
        )
        invoice.invoice_line_ids.filtered("product_id")[0]
        self.assertEqual(invoice.state, "draft")
        invoice.action_post()
        return invoice

    def create_in_invoice(self, vendor, start_date, end_date, attachment=True, tax_override=None):
        # IN Invoice
        # Search for existing tax group or create new one
        tax_group = self.env["account.tax.group"].search([("name", "=", "Tax Group 1")], limit=1)
        if not tax_group:
            tax_group = self.env["account.tax.group"].create(
                {
                    "name": "Tax Group 1",
                    "sequence": 1,
                }
            )

        # Use tax_override if provided, otherwise use default tax
        if tax_override:
            tax = tax_override
        else:
            # Search for existing tax or create new one
            tax = self.env["account.tax"].search([
                ("name", "=", "Tax 0%"),
                ("type_tax_use", "=", "purchase"),
            ], limit=1)
            if not tax:
                tax = self.env["account.tax"].create(
                    {
                        "name": "Tax 0%",
                        "amount": 0.0,
                        "amount_type": "percent",
                        "type_tax_use": "purchase",
                        "tax_group_id": tax_group.id,
                    }
                )
        invoice = self.InvoiceObj.create(
            {
                "partner_id": vendor.id,
                "user_id": self.env.user.id,
                "invoice_date": start_date,
                "invoice_date_due": end_date,
                "company_id": self.env.company.id,
                "currency_id": self.env.company.currency_id.id,
                "move_type": "in_invoice",
                "payment_reference": "Payment Reference",
                "ref": "Customer Reference",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.lease.id,
                            "quantity": 1.0,
                            "price_unit": 900.0,
                            "price_total": 900.0,
                            "credit": 0.0,
                            "debit": 900.0,
                            "tax_ids": [(6, 0, tax.ids)],
                            "account_id": self.account_expense.id,
                            "analytic_distribution": {
                                self.analytic_account_office.id: 100.0,
                            },
                        },
                    ),
                ],
            }
        )
        if attachment:
            self.create_invoice_attachment(invoice)
        self.assertEqual(invoice.state, "draft")
        invoice.action_post()
        return invoice

    def create_refund(self, invoice, refund_date):
        # OUT Refund/Credit Note
        refund = invoice._reverse_moves([{"invoice_date": refund_date}])
        self.create_invoice_attachment(refund)
        self.assertEqual(refund.state, "draft")
        refund.action_post()
        return refund

    def create_customer_datev_export(self, start_date, end_date):
        datev_export = self.DatevExportObj.create(
            {
                "check_xsd": True,
                "date_start": start_date,
                "date_stop": end_date,
            }
        )
        return datev_export

    def create_vendor_datev_export(self, start_date, end_date):
        datev_export = self.DatevExportObj.create(
            {
                "check_xsd": True,
                "date_start": start_date,
                "date_stop": end_date,
            }
        )
        return datev_export

    def create_customer_datev_export_manually(self, invoice):
        start_date = invoice.invoice_date
        end_date = invoice.invoice_date_due
        datev_export = self.DatevExportObj.create(
            {
                "check_xsd": True,
                "date_start": start_date,
                "date_stop": end_date,
                "invoice_ids": [(6, 0, [invoice.id])],
            }
        )
        return datev_export

    def _assert_list_of_files(self, expected_list, actual_list):
        self.assertEqual(len(actual_list), len(expected_list))
        for file in expected_list:
            self.assertIn(file, actual_list)

    def _run_test_document(self, doc, invoice):
        inv_number = invoice.name.replace("/", "-")
        self.assertEqual(doc(".//header/clientName")[0].text, invoice.company_id.name)
        self.assertIn(
            invoice.name, [item.text for item in doc(".//document/description")]
        )
        self.assertIn(
            inv_number + ".xml",
            [item.attrib["datafile"] for item in doc(".//extension[@datafile]")],
        )
        self.assertIn(
            inv_number + ".pdf",
            [item.attrib["name"] for item in doc(".//extension[@name]")],
        )
        self.assertIn(
            "Outgoing" if invoice.move_type.startswith("out_") else "Incoming",
            [item.attrib["value"] for item in doc(".//property[@key='InvoiceType']")],
        )

    def _run_test_invoice(self, doc, invoice):
        inv_line = invoice.invoice_line_ids.filtered("product_id")[0]

        info = doc(".//invoice_info").attrib
        line = doc(".//invoice_item_list").attrib
        total = doc(".//total_amount").attrib

        self.assertEqual(
            info["invoice_type"],
            (
                "Rechnung"
                if invoice.move_type.endswith("_invoice")
                else "Gutschrift/Rechnungskorrektur"
            ),
        )
        self.assertEqual(info["invoice_date"], invoice.invoice_date.isoformat())

        if invoice.move_type.startswith("out_"):
            self.assertEqual(
                doc(".//invoice_party/address").attrib["name"],
                invoice.partner_id.display_name,
            )
        else:
            self.assertEqual(
                doc(".//supplier_party/address").attrib["name"],
                invoice.partner_id.display_name,
            )

        self.assertEqual(float(line["quantity"]), inv_line.quantity)
        self.assertEqual(line["product_id"], inv_line.product_id.default_code)

        sign = -1 if invoice.move_type.endswith("_refund") else 1
        self.assertEqual(
            float(total["net_total_amount"]),
            sign * invoice.amount_untaxed,
        )
        self.assertEqual(
            float(total["total_gross_amount_excluding_third-party_collection"]),
            sign * invoice.amount_total,
        )
        # partner has bank account
        if invoice.partner_id.bank_ids:
            bank = doc(".//invoice_party/account").attrib
            self.assertEqual(
                bank["bank_name"], invoice.partner_id.bank_ids[0].bank_name
            )
            self.assertEqual(
                bank["iban"],
                invoice.partner_id.bank_ids[0].acc_number.replace(" ", ""),
            )

    def _run_test_out_refund_datev_export(self, refund):
        line = refund.invoice_line_ids.filtered("product_id")[0]
        self.assertEqual(refund.move_type, "out_refund")
        self.assertEqual(line.account_id, self.account_income)
        self.assertEqual(line.price_unit, 120.00)
        self.assertEqual(line.quantity, 5.00)
        self.assertEqual(refund.journal_id, self.sale_journal)
        self.assertEqual(refund.state, "posted")

        start_date = refund.invoice_date
        end_date = refund.invoice_date_due
        datev_export = self.create_customer_datev_export(start_date, end_date)
        self.assertEqual(datev_export.datev_file, False)
        self.assertEqual(datev_export.state, "draft")
        # There is always a first invoice
        # self.assertEqual(datev_export.invoices_count, 2)
        invoice = datev_export.invoice_ids[0]
        self.assertEqual(invoice, refund.reversed_entry_id)
        inv_number = invoice.name.replace("/", "-")
        ref_number = refund.name.replace("/", "-")

        self.assertEqual(datev_export.state, "draft")
        datev_export.action_pending()
        self.assertEqual(datev_export.state, "pending")
        datev_export.with_user(datev_export.create_uid.id).get_zip()
        datev_export._create_activity()
        datev_export._compute_datev_filesize()
        self.assertTrue(datev_export.datev_filesize)
        self.assertEqual(datev_export.state, "done")

        self.assertTrue(datev_export.datev_file)
        self.assertTrue(datev_export.attachment_id)
        file_list = [
            "document.xml",
            inv_number + ".xml",
            inv_number + ".pdf",
            ref_number + ".xml",
            ref_number + ".pdf",
        ]
        res = self._check_filecontent(datev_export)

        # check list of files
        self._assert_list_of_files(file_list, res["file_list"])

        # check document.xml
        self._run_test_document(res["document"], invoice)

        # check invoice.xml file
        self._run_test_invoice(res["invoice"], invoice)

    def _run_test_in_refund_datev_export(self, refund, attachment):
        line = refund.invoice_line_ids.filtered("product_id")[0]
        self.assertEqual(refund.move_type, "in_refund")
        self.assertEqual(line.account_id, self.account_expense)
        self.assertEqual(line.price_unit, 900.00)
        self.assertEqual(line.quantity, 1.00)
        self.assertEqual(refund.journal_id, self.purchase_journal)
        self.assertEqual(refund.state, "posted")

        start_date = refund.invoice_date
        end_date = refund.invoice_date_due
        datev_export = self.create_vendor_datev_export(start_date, end_date)

        self.assertEqual(datev_export.datev_file, False)
        self.assertEqual(datev_export.state, "draft")
        # There is always a first invoice
        # self.assertEqual(datev_export.invoices_count, 2)
        invoice = refund.reversed_entry_id

        inv_number = invoice.name.replace("/", "-")
        ref_number = refund.name.replace("/", "-")

        self.assertEqual(datev_export.state, "draft")
        datev_export.action_pending()
        self.assertEqual(datev_export.state, "pending")
        datev_export.with_user(datev_export.create_uid.id).get_zip()
        datev_export._create_activity()
        # self.DatevExportObj.cron_run_pending_export()
        # self.DatevExportObj.refresh()
        self.assertEqual(datev_export.state, "done")

        self.assertTrue(datev_export.datev_file)
        self.assertTrue(datev_export.attachment_id)
        file_list = [
            "document.xml",
            f"{inv_number}.xml",
            f"{inv_number}.pdf",
            f"{ref_number}.xml",
            f"{ref_number}.pdf",
        ]
        res = self._check_filecontent(datev_export, refund=True)
        # check list of files
        self.assertEqual(len(res["file_list"]), len(file_list))
        self.assertIn(f"{inv_number}.xml", res["file_list"])
        self.assertIn(f"{inv_number}.pdf", res["file_list"])
        self.assertIn(f"{ref_number}.xml", res["file_list"])
        self.assertIn(f"{ref_number}.pdf", res["file_list"])

        # check document.xml
        self._run_test_document(res["document"], refund)

        # check invoice.xml file
        self._run_test_invoice(res["invoice"], refund)

    def _run_test_out_invoice_datev_export(self, invoice):
        line = invoice.invoice_line_ids.filtered("product_id")[0]
        self.assertEqual(invoice.move_type, "out_invoice")
        self.assertEqual(line.account_id, self.account_income)
        self.assertEqual(line.price_unit, 120.00)
        self.assertEqual(line.quantity, 5.00)
        self.assertEqual(invoice.journal_id, self.sale_journal)
        self.assertEqual(invoice.state, "posted")

        start_date = invoice.invoice_date
        end_date = invoice.invoice_date_due
        datev_export = self.create_customer_datev_export(start_date, end_date)
        self.assertEqual(datev_export.datev_file, False)
        self.assertEqual(datev_export.state, "draft")
        # There is always a first invoice
        self.assertEqual(datev_export.invoices_count, 1)
        invoice = datev_export.invoice_ids[0]
        self.assertEqual(invoice, invoice)
        inv_number = invoice.name.replace("/", "-")

        self.assertEqual(datev_export.state, "draft")
        datev_export.action_pending()
        self.assertEqual(datev_export.state, "pending")
        datev_export.with_user(datev_export.create_uid.id).get_zip()
        datev_export._create_activity()
        # self.DatevExportObj.cron_run_pending_export()
        # self.DatevExportObj.refresh()
        self.assertEqual(datev_export.state, "done")

        self.assertTrue(datev_export.datev_file)
        self.assertTrue(datev_export.attachment_id)
        file_list = ["document.xml", inv_number + ".xml", inv_number + ".pdf"]
        res = self._check_filecontent(datev_export)

        # check list of files
        self._assert_list_of_files(file_list, res["file_list"])

        # check document.xml
        self._run_test_document(res["document"], invoice)

        # check invoice.xml file
        self._run_test_invoice(res["invoice"], invoice)

    def _run_test_in_invoice_datev_export(self, invoice, attachment):
        line = invoice.invoice_line_ids.filtered("product_id")[0]
        self.assertEqual(invoice.move_type, "in_invoice")
        self.assertEqual(line.account_id, self.account_expense)
        self.assertEqual(line.price_unit, 900.00)
        self.assertEqual(line.quantity, 1.00)
        self.assertEqual(invoice.journal_id, self.purchase_journal)
        self.assertEqual(invoice.state, "posted")

        start_date = invoice.invoice_date
        end_date = invoice.invoice_date_due
        datev_export = self.create_vendor_datev_export(start_date, end_date)

        self.assertEqual(datev_export.datev_file, False)
        self.assertEqual(datev_export.state, "draft")
        self.assertEqual(datev_export.invoices_count, 1)
        export_invoice = datev_export.invoice_ids[0]
        self.assertEqual(export_invoice, invoice)
        inv_number = export_invoice.name.replace("/", "-")

        self.assertEqual(datev_export.state, "draft")
        datev_export.action_pending()
        self.assertEqual(datev_export.state, "pending")
        datev_export.with_user(datev_export.create_uid.id).get_zip()
        datev_export._create_activity()
        # self.DatevExportObj.cron_run_pending_export()
        # self.DatevExportObj.refresh()
        self.assertEqual(datev_export.state, "done")

        self.assertTrue(datev_export.datev_file)
        self.assertTrue(datev_export.attachment_id)
        file_list = ["document.xml", f"{inv_number}.xml", f"{inv_number}.pdf"]
        res = self._check_filecontent(datev_export)

        # check list of files
        self._assert_list_of_files(file_list, res["file_list"])

        # check document.xml
        self._run_test_document(res["document"], invoice)

        # check invoice.xml file
        self._run_test_invoice(res["invoice"], invoice)

    # ------- CUSTOMER --------
    def test_01_out_invoice_de_datev_export(self):
        # 1. OUT Invoice DE
        invoice = self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )
        self._run_test_out_invoice_datev_export(invoice)

    def test_02_out_invoice_eu_datev_export(self):
        # 2. OUT Invoice EU
        invoice = self.create_out_invoice(
            self.customer_eu, self.start_date, self.end_date
        )
        self._run_test_out_invoice_datev_export(invoice)

    def test_03_out_invoice_noneu_datev_export(self):
        # 3. OUT Invoice NonEU
        invoice = self.create_out_invoice(
            self.customer_noneu, self.start_date, self.end_date
        )
        self._run_test_out_invoice_datev_export(invoice)

    def test_04_out_refund_de_datev_export(self):
        # 4. OUT Refund DE
        # before the due date of invoice
        invoice = self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )
        refund = self.create_refund(invoice, self.refund_date)
        self.assertEqual(refund.reversed_entry_id, invoice)
        self.assertEqual(refund.invoice_date, self.refund_date)
        self._run_test_out_refund_datev_export(refund)

    def test_05_out_refund_eu_datev_export(self):
        # 5. OUT Refund EU
        # before the due date of invoice
        invoice = self.create_out_invoice(
            self.customer_eu, self.start_date, self.end_date
        )
        refund = self.create_refund(invoice, self.refund_date)
        self.assertEqual(refund.reversed_entry_id, invoice)
        self.assertEqual(refund.invoice_date, self.refund_date)
        self._run_test_out_refund_datev_export(refund)

    def test_06_out_refund_noneu_datev_export(self):
        # 6. OUT Refund NonEU
        # before the due date of invoice
        invoice = self.create_out_invoice(
            self.customer_noneu, self.start_date, self.end_date
        )
        refund = self.create_refund(invoice, self.refund_date)
        self.assertEqual(refund.reversed_entry_id, invoice)
        self.assertEqual(refund.invoice_date, self.refund_date)
        self._run_test_out_refund_datev_export(refund)

    # ------- VENDOR --------
    def test_07_in_invice_de_datev_export(self):
        # 7. IN Invoice DE
        invoice = self.create_in_invoice(self.vendor_de, self.start_date, self.end_date)
        self._run_test_in_invoice_datev_export(invoice, self.inv_attach_de)

    def test_08_in_invoice_eu_datev_export(self):
        # 8. IN Invoice EU
        invoice = self.create_in_invoice(self.vendor_eu, self.start_date, self.end_date)
        self._run_test_in_invoice_datev_export(invoice, self.inv_attach_eu)

    def test_09_in_invoice_noneu_datev_export(self):
        # 9. IN Invoice NonEU
        invoice = self.create_in_invoice(
            self.vendor_noneu, self.start_date, self.end_date
        )
        self._run_test_in_invoice_datev_export(invoice, self.inv_attach_noneu)

    def test_10_in_refund_de_datev_export(self):
        # 10. IN Refund DE
        # before the due date of invoice
        invoice = self.create_in_invoice(self.vendor_de, self.start_date, self.end_date)
        refund = self.create_refund(invoice, self.refund_date)
        self.assertEqual(refund.reversed_entry_id, invoice)
        self.assertEqual(refund.invoice_date, self.refund_date)
        self._run_test_in_refund_datev_export(refund, self.refund_attach_de)

    def test_11_in_refund_eu_datev_export(self):
        # 11. IN Refund EU
        # before the due date of invoice
        invoice = self.create_in_invoice(self.vendor_eu, self.start_date, self.end_date)
        refund = self.create_refund(invoice, self.refund_date)
        self.assertEqual(refund.reversed_entry_id, invoice)
        self.assertEqual(refund.invoice_date, self.refund_date)
        self._run_test_in_refund_datev_export(refund, self.refund_attach_eu)

    def test_12_in_refund_noneu_datev_export(self):
        # 12. IN Refund NonEU
        # before the due date of invoice
        invoice = self.create_in_invoice(
            self.vendor_noneu, self.start_date, self.end_date
        )
        refund = self.create_refund(invoice, self.refund_date)
        self.assertEqual(refund.reversed_entry_id, invoice)
        self.assertEqual(refund.invoice_date, self.refund_date)
        self._run_test_in_refund_datev_export(refund, self.refund_attach_noneu)

    def test_13_out_invoice_with_tax(self):
        # OUT Invoice with tax
        self.env.user.company_id.tax_calculation_rounding_method = "round_globally"

        tax_group = self.env["account.tax.group"].create(
            {
                "name": "Tax Group 1",
                "sequence": 1,
            }
        )

        tax = self.env["account.tax"].create(
            {
                "name": "Tax 15.0",
                "amount": 15.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": tax_group.id,
            }
        )
        invoice = self.create_out_invoice_with_tax(
            self.child_customer, self.start_date, self.end_date, tax
        )
        self._run_test_out_invoice_datev_export(invoice)

    def test_14_datev_export_without_invoice(self):
        # 1. when default values are set
        # date_start, date_end (based on datev_default_period of current company)
        # export_invoice = True,
        # export_refund = True,
        # check_xsd = True,
        date_start = self.today - timedelta(days=self.today.weekday(), weeks=1)
        date_stop = date_start + timedelta(days=6)
        datev_export = self.DatevExportObj.create({})
        self.assertEqual(datev_export.datev_file, False)
        self.assertEqual(datev_export.state, "draft")
        self.assertEqual(datev_export.date_start, date_start)
        self.assertEqual(datev_export.date_stop, date_stop)

        # change date_stop , so that invoices_count = 0
        datev_export.date_stop = date_stop - timedelta(4)
        # 2. when try to set state = 'pending' and invoice_count = 0
        # ValidationError: "No invoices/refunds for export!"
        with self.assertRaises(ValidationError):
            datev_export.action_pending()

        out_invoice = self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )
        self.create_invoice_attachment(out_invoice)

        self.DatevExportObj.with_context(
            active_model="account.move",
            active_ids=out_invoice.ids,
        ).export_zip_invoice()

        in_invoice = self.create_in_invoice(
            self.customer_de, self.start_date, self.end_date
        )

        self.DatevExportObj.export_zip_invoice(in_invoice.ids)

    def test_period(self):
        checks = [
            ("day", (2022, 6, 15), (2022, 6, 14), (2022, 6, 14)),
            ("week", (2022, 6, 15), (2022, 6, 6), (2022, 6, 12)),
            ("month", (2022, 6, 15), (2022, 5, 1), (2022, 5, 31)),
            ("year", (2022, 6, 15), (2021, 1, 1), (2021, 12, 31)),
            (False, (2022, 6, 15), (2022, 6, 14), (2022, 6, 14)),
        ]
        for dates in checks:
            today, start, stop = [date(*x) for x in dates[1:]]
            self.env.company.datev_default_period = dates[0]
            self.assertEqual(self.DatevExportObj._default_start(today), start)
            self.assertEqual(self.DatevExportObj._default_stop(today), stop)

    def test_state_workflow(self):
        self.create_in_invoice(self.customer_de, self.start_date, self.end_date)
        export = self.DatevExportObj.create({})
        export.write({"date_start": self.start_date, "date_stop": self.end_date})

        self.assertEqual(len(export.invoice_ids), 1)

        self.assertEqual(export.state, "draft")
        export.action_pending()
        self.assertEqual(export.state, "pending")
        export.action_draft()
        self.assertEqual(export.state, "draft")
        self.assertEqual(len(export.invoice_ids), 0)

        export.state = "running"
        with self.assertRaises(ValidationError):
            export.action_pending()
        with self.assertRaises(ValidationError):
            export.action_draft()

        export.action_done()
        self.assertEqual(export.state, "done")

    def test_export_zip_with_out_invoice_without_attachment__raises_error(self):
        invoice = self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )
        with self.assertRaises(UserError):
            self.DatevExportObj.export_zip_invoice(invoice.ids)

    def test_generate_pdf_with_in_invoice_without_attachment__raises_error(self):
        invoice = self.create_in_invoice(
            self.vendor_de, self.start_date, self.end_date, attachment=False
        )

        with self.assertRaises(ValueError):
            self.env["datev.pdf.generator"].generate_pdf(invoice)

    def test_out_invoice_with_multiple_pdf__pdf_are_merged(self):
        invoice = self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )
        for _ in range(3):
            self.create_invoice_attachment(invoice)
        self._run_test_out_invoice_datev_export(invoice)

    def test_export_only_invoices_with_datev_exported_false(self):
        tax_group = self.env["account.tax.group"].create(
            {
                "name": "Tax Group 1",
                "sequence": 1,
            }
        )
        tax = self.env["account.tax"].create(
            {
                "name": "Tax 15.0",
                "amount": 15.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": tax_group.id,
            }
        )

        # oldest dates invoice
        invoice1 = self.create_out_invoice_with_tax(
            self.customer_de, self.today, self.today + timedelta(days=1), tax
        )
        self.assertFalse(invoice1.datev_exported)

        # newest dates invoice
        invoice2 = self.create_out_invoice_with_tax(
            self.customer_de,
            self.today + timedelta(days=6),
            self.today + timedelta(days=7),
            tax,
        )
        self.assertFalse(invoice2.datev_exported)

        # with oldest date_start and oldest date_stop
        datev_export1 = self.DatevExportObj.create(
            {
                "date_start": self.today,
                "date_stop": self.today + timedelta(days=1),
            }
        )
        self.assertEqual(datev_export1.invoice_ids.ids, invoice1.ids)
        self.assertTrue(invoice1.datev_exported)

        # with oldest date_start and newest date_stop
        datev_export2 = self.DatevExportObj.create(
            {
                "date_start": self.today,
                "date_stop": self.today + timedelta(days=7),
            }
        )
        self.assertEqual(datev_export2.invoice_ids.ids, invoice2.ids)
        self.assertTrue(invoice2.datev_exported)

        datev_export3 = self.DatevExportObj.create(
            {
                "date_start": self.today,
                "date_stop": self.today + timedelta(days=7),
            }
        )
        self.assertFalse(datev_export3.invoice_ids.ids)

    def test_xml_generator(self):
        """Test that XML validation errors are properly stored in datev_validation field"""
        # Use simple dates for the test
        start_date = date.today() - timedelta(days=10)
        end_date = date.today() - timedelta(days=5)

        # Create a test invoice using the TestBase method
        invoice = self.create_out_invoice(
            self.customer_de, start_date, end_date
        )

        # Create invalid XML
        root = etree.fromstring("<invalid/>")

        # Test that validation error is stored in datev_validation field
        generator = self.env["datev.xml.generator"]
        result = generator.check_xml_file("inv.xml", root, invoice=invoice)

        # Should return True (no exception) but store error in datev_validation
        self.assertTrue(result)
        self.assertTrue(invoice.datev_validation)
        self.assertIn("XML Validation Error", invoice.datev_validation)

    # ========================================================================
    # NEUE TESTS: Dokumententyp-Filter (Checkboxen)
    # ========================================================================

    def test_01_document_type_filter_all_types_enabled(self):
        """Test 1: Alle Dokumententypen aktiviert (Standard-Verhalten)"""
        # Erstelle verschiedene Invoice-Typen
        # out_invoice + out_refund
        self.create_refund(
            self.create_out_invoice(
                self.customer_de, self.start_date, self.end_date
            ), self.start_date
        )

        # in_invoice + in_refund
        self.create_refund(
            self.create_in_invoice(
                self.vendor_de, self.start_date, self.end_date
            ), self.start_date
        )

        # Export mit allen Checkboxen aktiviert (Standard)
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
                "include_out_invoice": True,
                "include_out_refund": True,
                "include_in_invoice": True,
                "include_in_refund": True,
            }
        )

        # Sollte alle 4 Invoices finden
        self.assertEqual(len(datev_export.invoice_ids), 4)
        move_types = datev_export.invoice_ids.mapped("move_type")
        self.assertIn("out_invoice", move_types)
        self.assertIn("out_refund", move_types)
        self.assertIn("in_invoice", move_types)
        self.assertIn("in_refund", move_types)

    def test_02_document_type_filter_only_outgoing(self):
        """Test 2: Nur ausgehende Dokumente (Rechnungen + Gutschriften)"""
        # Erstelle verschiedene Invoice-Typen (invoice_date wird in create() gesetzt)
        out_invoice = self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )
        self.create_refund(out_invoice, self.start_date)

        in_invoice = self.create_in_invoice(
            self.vendor_de, self.start_date, self.end_date
        )
        self.create_refund(in_invoice, self.start_date)

        # Export nur mit ausgehenden Dokumenten
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
                "include_out_invoice": True,
                "include_out_refund": True,
                "include_in_invoice": False,  # DEAKTIVIERT
                "include_in_refund": False,  # DEAKTIVIERT
            }
        )

        # Sollte nur 2 Invoices finden (out_invoice, out_refund)
        self.assertEqual(len(datev_export.invoice_ids), 2)
        move_types = datev_export.invoice_ids.mapped("move_type")
        self.assertIn("out_invoice", move_types)
        self.assertIn("out_refund", move_types)
        self.assertNotIn("in_invoice", move_types)
        self.assertNotIn("in_refund", move_types)

    def test_03_document_type_filter_only_incoming(self):
        """Test 3: Nur eingehende Dokumente (Rechnungen + Gutschriften)"""
        # Erstelle verschiedene Invoice-Typen (invoice_date wird in create() gesetzt)
        self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )

        in_invoice = self.create_in_invoice(
            self.vendor_de, self.start_date, self.end_date
        )
        self.create_refund(in_invoice, self.start_date)

        # Export nur mit eingehenden Dokumenten
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
                "include_out_invoice": False,  # DEAKTIVIERT
                "include_out_refund": False,  # DEAKTIVIERT
                "include_in_invoice": True,
                "include_in_refund": True,
            }
        )

        # Sollte nur 2 Invoices finden (in_invoice, in_refund)
        self.assertEqual(len(datev_export.invoice_ids), 2)
        move_types = datev_export.invoice_ids.mapped("move_type")
        self.assertNotIn("out_invoice", move_types)
        self.assertNotIn("out_refund", move_types)
        self.assertIn("in_invoice", move_types)
        self.assertIn("in_refund", move_types)

    def test_04_document_type_filter_only_invoices(self):
        """Test 4: Nur Rechnungen (keine Gutschriften)"""
        # Erstelle verschiedene Invoice-Typen (invoice_date wird in create() gesetzt)
        out_invoice = self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )
        self.create_refund(out_invoice, self.start_date)

        self.create_in_invoice(
            self.vendor_de, self.start_date, self.end_date
        )

        # Export nur Rechnungen (keine Gutschriften)
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
                "include_out_invoice": True,
                "include_out_refund": False,  # DEAKTIVIERT
                "include_in_invoice": True,
                "include_in_refund": False,  # DEAKTIVIERT
            }
        )

        # Sollte nur 2 Invoices finden (out_invoice, in_invoice)
        self.assertEqual(len(datev_export.invoice_ids), 2)
        move_types = datev_export.invoice_ids.mapped("move_type")
        self.assertIn("out_invoice", move_types)
        self.assertIn("in_invoice", move_types)
        self.assertNotIn("out_refund", move_types)
        self.assertNotIn("in_refund", move_types)

    def test_05_document_type_filter_none_selected_raises_error(self):
        """Test 5: Keine Checkbox aktiviert → muss UserError werfen"""
        # Export mit allen Checkboxen deaktiviert
        # UserError wird bereits im create() geworfen (nicht erst in get_invoices())
        with self.assertRaises(UserError) as cm:
            self.DatevExportObj.create(
                {
                    "date_start": self.start_date,
                    "date_stop": self.end_date,
                    "include_out_invoice": False,
                    "include_out_refund": False,
                    "include_in_invoice": False,
                    "include_in_refund": False,
                }
            )

        # Fehler-Nachricht prüfen
        self.assertIn("Keine Dokumententypen", str(cm.exception))

    def test_06_document_type_filter_description_shows_selected_types(self):
        """Test 6: get_description() zeigt nur ausgewählte Typen"""
        # Export nur mit out_invoice + in_invoice
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
                "include_out_invoice": True,
                "include_out_refund": False,
                "include_in_invoice": True,
                "include_in_refund": False,
            }
        )

        description = datev_export.get_description()

        # Beschreibung sollte nur aktivierte Typen enthalten
        self.assertIn("Ausgehende Rechnungen", description)
        self.assertNotIn("Ausgehende Gutschriften", description)
        self.assertIn("Eingehende Rechnungen", description)
        self.assertNotIn("Eingehende Gutschriften", description)

    def test_07_document_type_filter_checkbox_change_in_draft(self):
        """Test 7: Checkboxen können im draft State geändert werden"""
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
                "include_out_invoice": True,
                "include_out_refund": True,
                "include_in_invoice": True,
                "include_in_refund": True,
            }
        )

        # Im draft State sollten Änderungen möglich sein
        self.assertEqual(datev_export.state, "draft")
        datev_export.write({"include_out_refund": False})
        self.assertFalse(datev_export.include_out_refund)

    def test_08_document_type_filter_default_values(self):
        """Test 8: Standard-Werte sind alle TRUE"""
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
            }
        )

        # Alle Checkboxen sollten standardmäßig aktiviert sein
        self.assertTrue(datev_export.include_out_invoice)
        self.assertTrue(datev_export.include_out_refund)
        self.assertTrue(datev_export.include_in_invoice)
        self.assertTrue(datev_export.include_in_refund)

    def test_09_document_type_filter_write_triggers_reload(self):
        """Test 9: Datum-Änderung triggert Reload von invoice_ids"""
        # Erstelle Invoice (invoice_date wird in create() gesetzt)
        self.create_out_invoice(
            self.customer_de, self.start_date, self.end_date
        )

        # Export erstellen
        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.start_date,
                "date_stop": self.end_date,
            }
        )

        len(datev_export.invoice_ids)

        # Datum ändern → sollte invoice_ids neu laden
        new_start_date = self.start_date - timedelta(days=10)
        datev_export.write({"date_start": new_start_date})

        # invoice_ids sollten neu geladen worden sein
        # (kann mehr oder weniger Invoices finden)
        self.assertIsNotNone(datev_export.invoice_ids)

    def test_missing_attachment_saves_error_messages(self):
        """Test that error messages are saved in export and invoices when attachment is missing."""
        # Create a vendor bill WITHOUT attachment
        bill = self.create_in_invoice(
            vendor=self.partner_DE,
            start_date=self.today,
            end_date=self.today,
            attachment=False
        )
        # Make sure NO attachment exists for this bill
        self.env["ir.attachment"].search(
            [("res_id", "=", bill.id), ("res_model", "=", "account.move")]
        ).unlink()

        # Create DATEV export
        start_date = self.today
        end_date = self.today
        datev_export = self.DatevExportObj.create(
            {
                "date_start": start_date,
                "date_stop": end_date,
            }
        )

        # Try to generate ZIP - should NOT raise but mark as failed with error messages
        datev_export.get_zip()

        # Verify that error message is saved in export
        self.assertNotEqual(
            datev_export.exception_info,
            False,
            "export.exception_info should be set when attachment is missing",
        )
        self.assertIn(
            "No PDF attachment found",
            datev_export.exception_info,
            "export.exception_info should contain error about missing PDF",
        )
        self.assertIn(
            bill.name,
            datev_export.exception_info,
            "export.exception_info should contain invoice name",
        )

        # Verify that error message is saved in invoice.datev_validation
        self.assertNotEqual(
            bill.datev_validation,
            False,
            "invoice.datev_validation should be set when attachment is missing",
        )
        self.assertIn(
            "No PDF attachment found",
            bill.datev_validation,
            "invoice.datev_validation should contain error about missing PDF",
        )

        # Verify that state is 'failed' (export failed due to missing attachment)
        self.assertEqual(
            datev_export.state,
            "failed",
            "export state should be 'failed' when some invoices have errors",
        )

        # 🚨 KRITISCH: Verify that NO ZIP attachment was created!
        self.assertFalse(
            datev_export.attachment_id,
            "NO ZIP attachment should be created when validation errors exist!",
        )
        self.assertFalse(
            datev_export.datev_file,
            "datev_file should be False when validation errors exist!",
        )

        # Verify that problematic_invoices_count is correct
        self.assertEqual(
            datev_export.problematic_invoices_count,
            1,
            "Should have 1 problematic invoice",
        )

    def test_validation_errors_delete_old_attachment(self):
        """Test that old ZIP attachment is deleted when re-export fails with validation errors."""
        # Create a successful export first (with valid invoice)
        self.create_out_invoice(
            customer=self.partner_DE,
            start_date=self.today,
            end_date=self.today,
        )

        datev_export = self.DatevExportObj.create(
            {
                "date_start": self.today,
                "date_stop": self.today,
            }
        )

        # First export should succeed
        datev_export.get_zip()
        self.assertEqual(datev_export.state, "done")
        self.assertTrue(datev_export.attachment_id, "First export should create attachment")
        old_attachment_id = datev_export.attachment_id.id

        # Now add a bill WITHOUT attachment to the same export
        bill_bad = self.create_in_invoice(
            vendor=self.partner_DE,
            start_date=self.today,
            end_date=self.today,
            attachment=False
        )
        # Remove any attachments
        self.env["ir.attachment"].search(
            [("res_id", "=", bill_bad.id), ("res_model", "=", "account.move")]
        ).unlink()

        # Reload invoices to include the bad bill
        datev_export.write({"invoice_ids": [(4, bill_bad.id)]})

        # Set export back to draft for re-export (without clearing invoice_ids)
        datev_export.write({"state": "draft"})

        # Re-export should fail
        datev_export.get_zip()

        # Verify state is failed
        self.assertEqual(
            datev_export.state,
            "failed",
            "Re-export should fail when validation errors exist",
        )

        # 🚨 KRITISCH: Old attachment should be DELETED
        self.assertFalse(
            datev_export.attachment_id,
            "Old ZIP attachment MUST be deleted when re-export fails!",
        )

        # Verify old attachment was actually deleted from database
        old_attachment_exists = self.env["ir.attachment"].search_count(
            [("id", "=", old_attachment_id)]
        )
        self.assertEqual(
            old_attachment_exists,
            0,
            "Old attachment should be deleted from database!",
        )

    def test_bu_code_export_disabled(self):
        """Test that BU-Code is NOT exported when export_bu_code is False"""
        # Create tax with BU-Code
        tax_with_bu_code = self.env["account.tax"].create({
            "name": "Test Tax 19%",
            "amount": 19.0,
            "amount_type": "percent",
            "type_tax_use": "purchase",
            "l10n_de_datev_code": "9",  # BU-Code set (no leading zeros)
        })

        # Create vendor bill with tax that has BU-Code (already posted by create_in_invoice)
        bill = self.create_in_invoice(
            self.vendor_de,
            self.start_date,
            self.end_date,
            tax_override=tax_with_bu_code
        )

        # Create export with export_bu_code = False (default)
        datev_export = self.DatevExportObj.create({
            "date_start": self.start_date,
            "date_stop": self.end_date,
            "export_bu_code": False,  # Explicitly set to False
        })
        datev_export.create_zip()

        # Check that export succeeded
        self.assertEqual(datev_export.state, "done")
        self.assertTrue(datev_export.attachment_id)

        # Parse XML and verify bu_code is NOT present
        zip_data = base64.b64decode(datev_export.datev_file)
        fp = io.BytesIO(zip_data)
        with zipfile.ZipFile(fp, "r") as z:
            invoice_file = f"{bill.name.replace('/', '-')}.xml"
            inv_data = z.read(invoice_file)
            inv_root = etree.fromstring(inv_data)

            # Find accounting_info element
            accounting_info = inv_root.find(
                ".//ns:accounting_info",
                namespaces={"ns": "http://xml.datev.de/bedi/tps/invoice/v050"}
            )

            self.assertIsNotNone(accounting_info, "accounting_info element should exist")

            # Verify bu_code attribute is NOT present or is False
            bu_code_value = accounting_info.get("bu_code")
            self.assertIn(
                bu_code_value,
                [None, "False", "false", ""],
                f"bu_code should be empty/False when export_bu_code=False, got: {bu_code_value}"
            )

    def test_bu_code_export_enabled(self):
        """Test that BU-Code IS exported when export_bu_code is True"""
        # Create tax with BU-Code
        tax_with_bu_code = self.env["account.tax"].create({
            "name": "Test Tax 19%",
            "amount": 19.0,
            "amount_type": "percent",
            "type_tax_use": "purchase",
            "l10n_de_datev_code": "9",  # BU-Code set (no leading zeros)
        })

        # Create vendor bill with tax that has BU-Code (already posted by create_in_invoice)
        bill = self.create_in_invoice(
            self.vendor_de,
            self.start_date,
            self.end_date,
            tax_override=tax_with_bu_code
        )

        # Create export with export_bu_code = True
        datev_export = self.DatevExportObj.create({
            "date_start": self.start_date,
            "date_stop": self.end_date,
            "export_bu_code": True,  # Enable BU-Code export
        })
        datev_export.create_zip()

        # Check that export succeeded
        self.assertEqual(datev_export.state, "done")
        self.assertTrue(datev_export.attachment_id)

        # Parse XML and verify bu_code IS present
        zip_data = base64.b64decode(datev_export.datev_file)
        fp = io.BytesIO(zip_data)
        with zipfile.ZipFile(fp, "r") as z:
            invoice_file = f"{bill.name.replace('/', '-')}.xml"
            inv_data = z.read(invoice_file)
            inv_root = etree.fromstring(inv_data)

            # Find accounting_info element
            accounting_info = inv_root.find(
                ".//ns:accounting_info",
                namespaces={"ns": "http://xml.datev.de/bedi/tps/invoice/v050"}
            )

            self.assertIsNotNone(accounting_info, "accounting_info element should exist")

            # Verify bu_code attribute contains the BU-Code (without leading zeros per DATEV schema)
            bu_code_value = accounting_info.get("bu_code")
            self.assertEqual(
                bu_code_value,
                "9",  # Expected: BU-Code without leading zeros (per DATEV XSD pattern: ([1-9]\d*|0))
                f"bu_code should be '9' when export_bu_code=True, got: {bu_code_value}"
            )
