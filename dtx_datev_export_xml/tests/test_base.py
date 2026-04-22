# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary
# pylint: disable=invalid-name
# pylint: disable=pointless-string-statement

from odoo.tests.common import TransactionCase


class TestBase(TransactionCase):
    """Testklasse zum Laden von Demo-Daten."""

    base64_encoded_data = (
        "JVBERi0xLjQKMSAwIG9iago8PC9UeXBlIC9DYXRhbG9nIC9QYWdlcyAyIDAgUj4+CmVuZG9iagoyIDAgb2Jq"
        "Cjw8L1R5cGUgL1BhZ2VzIC9Db3VudCAxIC9LaWRzIFszIDAgUl0+PgplbmRvYmoKMyAwIG9iago8PC9UeXBl"
        "IC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gL0NvbnRlbnRzIDQgMCBS"
        "Pj4KZW5kb2JqCjQgMCBvYmoKPDwvTGVuZ3RoIDQzPj4Kc3RyZWFtCkJUCi9GMCAyNCBUZgowIDAgVGYKKEhl"
        "bGxvIFBERiBDb250ZW50KSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA1CjAwMDAwMDAwMDAgNjU1"
        "MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAwMDAwNjcgMDAwMDAgbiAKMDAwMDAwMTI2IDAwMDAwIG4g"
        "CjAwMDAwMDE5OCAwMDAwMCBuIAp0cmFpbGVyCjw8L1Jvb3QgMSAwIFIgL1NpemUgNT4+CnN0YXJ0eHJlZgoy"
        "NzYKJSVFT0YK"
    )

    def setUp(self):
        super().setUp()
        self.load_test_data()

    def load_test_data(self):
        """Lädt die Demo-Daten in die Datenbank."""
        self._load_bank_data()
        self._load_company_data()
        self._load_account_data()
        self._load_partner_data()
        self._load_analytic_account_data()
        self._load_product_data()
        self._load_attachment_data()

    def _load_company_data(self):
        """Lädt die Partner-Daten."""
        self.country_DE = self.env.ref("base.de")

        """Lädt die Firmendaten."""
        self.company = self.env.ref("base.main_company")

        self.company.write(
            {
                "l10n_de_datev_consultant_number": "12345",
                "l10n_de_datev_client_number": "12345",
                "datev_vendor_order_ref": "partner",
                "datev_customer_order_ref": "partner",
            }
        )

        # add company address
        self.company_address = self.env["res.partner"].create(
            {
                "name": "Company Address",
                "street": "Street 1",
                "zip": "12345",
                "city": "City",
                "country_id": self.country_DE.id,
                "company_id": self.company.id,
                "property_account_receivable_id": self.env["account.account"]
                .create(
                    {
                        "name": "Company Account Receivable",
                        "code": "10000",
                        "reconcile": True,
                        "account_type": "asset_receivable",  # Forderungen
                    }
                )
                .id,
                "property_account_payable_id": self.env["account.account"]
                .create(
                    {
                        "name": "Company Account Payable",
                        "code": "70000",
                        "reconcile": True,
                        "account_type": "liability_payable",  # Verbindlichkeiten
                    }
                )
                .id,
            }
        )

        self.company.write(
            {
                "partner_id": self.company_address.id,
            }
        )

        # set germany as company country
        self.company.write(
            {
                "country_id": self.country_DE.id,
            }
        )

    def _load_account_data(self):

        tax_group = self.env["account.tax.group"].create(
            {
                "name": "Tax Group Basic",
                "sequence": 1,
            }
        )

        self.tax = self.env["account.tax"].create(
            {
                "name": "Tax 120%",
                "amount": 120.0,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "tax_group_id": tax_group.id,
            }
        )

        # create sale journal
        self.sale_journal = self.env["account.journal"].create(
            {
                "name": "Sales Journal",
                "code": "SAJ",
                "type": "sale",
                "company_id": self.company.id,
            }
        )
        # create purchase journal
        self.purchase_journal = self.env["account.journal"].create(
            {
                "name": "Purchase Journal",
                "code": "PUJ",
                "type": "purchase",
                "company_id": self.company.id,
            }
        )

        """Lädt die Konten-Daten für Odoo 17."""
        # Hauptkonten
        self.account_datev_rec = self.env["account.account"].create(
            {
                "name": "Company Account Receivable",
                "code": "69998",
                "reconcile": True,
                "account_type": "asset_receivable",  # Forderungen
            }
        )
        self.account_datev_pay = self.env["account.account"].create(
            {
                "name": "Company Account Payable",
                "code": "99999",
                "reconcile": True,
                "account_type": "liability_payable",  # Verbindlichkeiten
            }
        )

        # Deutsche Konten
        self.account_datev_rec_DE = self.env["account.account"].create(
            {
                "name": "A-Customer Account DE",
                "code": "10001",
                "reconcile": True,
                "account_type": "asset_receivable",  # Forderungen
            }
        )
        self.account_datev_pay_DE = self.env["account.account"].create(
            {
                "name": "A-Vendor Account DE",
                "code": "70001",
                "reconcile": True,
                "account_type": "liability_payable",  # Verbindlichkeiten
            }
        )

        # nicht deutsche Konten
        self.account_datev_rec_non_DE = self.env["account.account"].create(
            {
                "name": "A-Customer Account Non-DE",
                "code": "10002",
                "reconcile": True,
                "account_type": "asset_receivable",  # Forderungen
            }
        )
        self.account_datev_pay_non_DE = self.env["account.account"].create(
            {
                "name": "A-Vendor Account Non-DE",
                "code": "70002",
                "reconcile": True,
                "account_type": "liability_payable",  # Verbindlichkeiten
            }
        )

        # Einnahmen- und Ausgabenkonten
        self.account_datev_income = self.env["account.account"].create(
            {
                "name": "A-Income",
                "code": "8401",
                "reconcile": False,
                "account_type": "income",  # Erträge
            }
        )
        self.account_datev_expense = self.env["account.account"].create(
            {
                "name": "A-Expense",
                "code": "3401",
                "reconcile": False,
                "account_type": "expense",  # Aufwendungen
            }
        )

    def _load_partner_data(self):

        # Hauptpartner
        self.hauptpartner = self.env["res.partner"].create(
            {
                "name": "A-Customer Parent",
                "street": "Straße 1",
                "zip": "12345",
                "city": "Berlin",
                "country_id": self.country_DE.id,
                "customer_rank": 1,
                "supplier_rank": 0,
                "property_account_receivable_id": self.account_datev_rec_DE.id,
                "property_account_payable_id": self.account_datev_pay_DE.id,
            }
        )

        # Deutsche Partner
        self.partner_DE = self.env["res.partner"].create(
            {
                "name": "A-Customer DE",
                "street": "Straße 1",
                "zip": "12345",
                "city": "City",
                "country_id": self.country_DE.id,
                "customer_rank": 1,
                "supplier_rank": 0,
                "property_account_receivable_id": self.account_datev_rec_DE.id,
                "property_account_payable_id": self.account_datev_pay_DE.id,
            }
        )

        # nicht deutsche Partner
        self.partner_non_DE = self.env["res.partner"].create(
            {
                "name": "A-Customer Non-DE",
                "street": "Street 2",
                "zip": "54321",
                "city": "City",
                "country_id": self.country_CH.id,
                "customer_rank": 1,
                "supplier_rank": 0,
                "property_account_receivable_id": self.account_datev_rec_non_DE.id,
                "property_account_payable_id": self.account_datev_pay_non_DE.id,
            }
        )

    def _load_analytic_account_data(self):
        """Lädt die analytischen Konten."""
        # Erstellen Sie einen Standard-Analytic Plan, falls noch keiner vorhanden ist
        self.analytic_plan = self.env["account.analytic.plan"].search([], limit=1)
        if not self.analytic_plan:
            self.analytic_plan = self.env["account.analytic.plan"].create(
                {
                    "name": "Standard Plan",
                    "company_id": self.env.company.id,
                }
            )

        # Erstellen Sie die analytischen Konten mit dem Analytic Plan
        self.analytic_account_IT = self.env["account.analytic.account"].create(
            {
                "name": "A-IT",
                "code": "990010",
                "plan_id": self.analytic_plan.id,  # Analytic Plan angeben
            }
        )
        self.analytic_account_Office = self.env["account.analytic.account"].create(
            {
                "name": "A-Office",
                "code": "990000",
                "plan_id": self.analytic_plan.id,  # Analytic Plan angeben
            }
        )

        self.analytic_account_long_code = self.env["account.analytic.account"].create(
            {
                "name": "Analytic Account with a very long code",
                "code": "1234567890123456789012345678901234567890",
                "plan_id": self.analytic_plan.id,  # Analytic Plan angeben
            }
        )

    def _load_product_data(self):
        """Lädt die Produkt-Daten."""
        # In Odoo 19.0: product.product_category_all doesn't exist anymore
        # Create or find the root category
        self.product_category = self.env["product.category"].search([], limit=1)
        if not self.product_category:
            self.product_category = self.env["product.category"].create({
                "name": "All Products"
            })

        self.product_IT_Consulting = self.env["product.product"].create(
            {
                "name": "A-IT-Consulting",
                "default_code": "11-001",
                "type": "service",
                "sale_ok": True,
                "categ_id": self.product_category.id,
                "list_price": 120.00,
                "property_account_income_id": self.account_datev_income.id,
            }
        )

    def _load_attachment_data(self):
        """Lädt die Anhangs-Daten."""
        attachment_data = {
            "name": "vendor_bill_attachment_DE.pdf",
            "type": "binary",
            "datas": self.base64_encoded_data,
        }
        self.vendor_bill_attachment_DE = self.env["ir.attachment"].create(
            attachment_data
        )

    def _load_bank_data(self):
        """Lädt die Bank-Daten."""
        self.country_CH = self.env.ref("base.ch")

        self.example_bank = self.env["res.bank"].create(
            {
                "name": "Example Bank",
                "active": True,
                "bic": "ALSWCH21XXX",
                "country": self.country_CH.id,
            }
        )

        self.partner_bank = self.env["res.partner.bank"].create(
            {
                "acc_number": "DE89370400440532013000",
                "partner_id": self.env.ref("base.main_partner").id,
                "acc_type": "bank",
                "bank_id": self.example_bank.id,
            }
        )
