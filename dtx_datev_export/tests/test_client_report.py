# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

import ast
from unittest.mock import patch, MagicMock

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'datev_client_report')
class TestDtxClientReport(TransactionCase):
    """Unit-Tests für dtx.client.report (send_system_data)."""

    def _get_model(self):
        return self.env['dtx.client.report'].sudo()

    # ------------------------------------------------------------------
    # send_system_data – success
    # ------------------------------------------------------------------

    def test_send_success(self):
        """send_system_data gibt True zurück bei Erfolg."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{'messages': []}"
        mock_response.raise_for_status = MagicMock()

        with patch('odoo.addons.dtx_datev_export.models.dtx_client_report.requests.post',
                   return_value=mock_response):
            result = self._get_model().send_system_data(cron_mode=True)
        self.assertTrue(result)

    # ------------------------------------------------------------------
    # send_system_data – failure in cron_mode
    # ------------------------------------------------------------------

    def test_send_failure_cron_mode_returns_false(self):
        """Bei Fehler im cron_mode wird False zurückgegeben, kein Exception."""
        with patch('odoo.addons.dtx_datev_export.models.dtx_client_report.requests.post',
                   side_effect=ConnectionError('no network')):
            result = self._get_model().send_system_data(cron_mode=True)
        self.assertFalse(result)

    # ------------------------------------------------------------------
    # send_system_data – failure raises in non-cron mode
    # ------------------------------------------------------------------

    def test_send_failure_non_cron_raises(self):
        """Ohne cron_mode wird bei Fehler eine UserError geworfen."""
        with patch('odoo.addons.dtx_datev_export.models.dtx_client_report.requests.post',
                   side_effect=ConnectionError('no network')):
            with self.assertRaises(UserError):
                self._get_model().send_system_data(cron_mode=False)

    # ------------------------------------------------------------------
    # send_system_data – calls _get_message
    # ------------------------------------------------------------------

    def test_send_calls_get_message(self):
        """send_system_data ruft publisher_warranty.contract._get_message auf."""
        mock_response = MagicMock()
        mock_response.text = "{'messages': []}"
        mock_response.raise_for_status = MagicMock()

        with patch('odoo.addons.dtx_datev_export.models.dtx_client_report.requests.post',
                   return_value=mock_response) as mock_post:
            self._get_model().send_system_data(cron_mode=True)
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        self.assertIn('arg0', call_kwargs[1].get(
            'data', call_kwargs[0][1] if len(call_kwargs[0]) > 1 else {}))

    # ------------------------------------------------------------------
    # _post_messages – no mail module
    # ------------------------------------------------------------------

    def test_post_messages_empty_list(self):
        """_post_messages mit leerer Liste tut nichts."""
        self._get_model()._post_messages([])

    def test_post_messages_with_messages_no_crash(self):
        """_post_messages mit Nachrichten crasht nicht."""
        self._get_model()._post_messages(['Test message'])

    # ------------------------------------------------------------------
    # dtx_* addon versions inline in apps list
    # ------------------------------------------------------------------

    def test_annotate_dtx_addon_versions(self):
        """_annotate_dtx_addon_versions hängt Versionen an dtx_* Einträge an."""
        apps = ['base', 'dtx_datev_export']
        result = self._get_model()._annotate_dtx_addon_versions(apps)
        self.assertEqual(result[0], 'base')
        self.assertTrue(result[1].startswith('dtx_datev_export ('))
        self.assertTrue(result[1].endswith(')'))

    def test_annotate_idempotent(self):
        """Zweiter Aufruf mit bereits annotierten Einträgen ändert nichts."""
        apps = ['base', 'dtx_datev_export']
        once = self._get_model()._annotate_dtx_addon_versions(apps)
        twice = self._get_model()._annotate_dtx_addon_versions(once)
        self.assertEqual(once, twice)

    def test_send_apps_list_contains_dtx_versions(self):
        """send_system_data sendet dtx_* Module mit Versionen in apps-Liste."""
        mock_response = MagicMock()
        mock_response.text = "{'messages': []}"
        mock_response.raise_for_status = MagicMock()

        with patch('odoo.addons.dtx_datev_export.models.dtx_client_report.requests.post',
                   return_value=mock_response) as mock_post:
            self._get_model().send_system_data()

        payload = mock_post.call_args[1]['data']
        sent_msg = ast.literal_eval(payload['arg0'])
        self.assertIn('apps', sent_msg)
        dtx_entries = [a for a in sent_msg['apps'] if a.startswith('dtx_')]
        self.assertTrue(dtx_entries)
        for entry in dtx_entries:
            self.assertIn(' (', entry)
            self.assertTrue(entry.endswith(')'))
