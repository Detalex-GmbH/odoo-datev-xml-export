# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

from odoo.addons.dtx_datev_export_xml.tests.test_base import TestBase


class TestAccountDatevCode(TestBase):

    def test_datev_code_update_on_code_change(self):
        """Test that datev_code is updated when code changes."""
        # Use existing fixture from test_base
        account = self.account_datev_income

        # Test initial datev_code (code: "8401" -> 8401)
        self.assertEqual(account.datev_code, 8401)

        # Change to non-numeric code
        account.code = 'NEW123'
        self.assertEqual(account.datev_code, 0)

        # Change to code with leading zeros
        account.code = '00567'
        self.assertEqual(account.datev_code, 567)

        # Change back to numeric code
        account.code = '5000'
        self.assertEqual(account.datev_code, 5000)
