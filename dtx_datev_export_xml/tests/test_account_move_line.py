# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary


from odoo.addons.dtx_datev_export_xml.tests.test_base import TestBase


class TestDatevCostCategoryId(TestBase):
    def setUp(self):
        super().setUp()
        # Create additional analytic accounts for this test
        self.analytic_account_1 = self.env['account.analytic.account'].create({
            'name': 'Test Analytic Account 1',
            'code': 'A123456789012345678901234567890123456',  # 36 chars
            'plan_id': self.analytic_plan.id,
        })
        self.analytic_account_2 = self.env['account.analytic.account'].create({
            'name': 'Test Analytic Account 2',
            'code': 'B987654321',
            'plan_id': self.analytic_plan.id,
        })

        # Create test moves with proper account.move.line structure
        self.move_01 = self.env['account.move'].create({
            'name': 'Test Move 01',
            'journal_id': self.sale_journal.id,
            'date': '2025-01-01',
            'move_type': 'out_invoice',
            'partner_id': self.company_address.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Test Line with Analytics',
                    'account_id': self.account_datev_expense.id,
                    'quantity': 1.0,
                    'price_unit': 100.0,
                    'tax_ids': [(6, 0, [self.tax.id])],
                    'analytic_distribution': {
                        str(self.analytic_account_1.id): 100.0,
                        str(self.analytic_account_2.id): 50.0
                    },
                })
            ]
        })

        self.move_02 = self.env['account.move'].create({
            'name': 'Test Move 02',
            'journal_id': self.sale_journal.id,
            'date': '2025-01-01',
            'move_type': 'out_invoice',
            'partner_id': self.company_address.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Test Line without Analytics',
                    'account_id': self.account_datev_expense.id,
                    'quantity': 1.0,
                    'price_unit': 50.0,
                    'tax_ids': [(6, 0, [self.tax.id])],
                })
            ]
        })

    def test_datev_cost_category_id_max_length(self):
        result = self.move_01.invoice_line_ids[0].datev_cost_category_id()
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 36)
        self.assertEqual(result, self.analytic_account_1.code[:36])

    def test_datev_cost_category_id_empty(self):
        result = self.move_02.invoice_line_ids[0].datev_cost_category_id()
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 0)
        self.assertEqual(result, "")
