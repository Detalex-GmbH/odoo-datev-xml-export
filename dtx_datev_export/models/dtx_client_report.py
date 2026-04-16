# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary
import logging
from ast import literal_eval

import requests

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

DETALEX_URL = 'https://detalex.de/client_data'


class DtxClientReport(models.AbstractModel):
    _name = 'dtx.client.report'
    _description = 'Detalex Client Data Report'

    @api.model
    def _annotate_dtx_addon_versions(self, apps):
        """Return the apps list with versions appended to dtx_* entries.

        Entries that already contain a version (identified by a space+paren)
        are returned unchanged, so the call is idempotent.
        """
        dtx_names = [a for a in apps if a.startswith('dtx_') and ' (' not in a]
        if not dtx_names:
            return apps
        modules = self.env["ir.module.module"].sudo().search([
            ("state", "=", "installed"),
            ("name", "in", dtx_names),
        ])
        versions = {m.name: m.installed_version for m in modules}
        return [
            f"{a} ({versions[a]})" if a in versions else a
            for a in apps
        ]

    @api.model
    def send_system_data(self, cron_mode=True):
        """Send system data to the Detalex server."""
        try:
            msg = self.env['publisher_warranty.contract']._get_message()
            msg['apps'] = self._annotate_dtx_addon_versions(msg.get('apps', []))
            arguments = {'arg0': str(msg), 'action': 'update'}
            response = requests.post(DETALEX_URL, data=arguments, timeout=30)
            response.raise_for_status()
            result = literal_eval(response.text)
            self._post_messages(result.get('messages', []))
        except Exception:  # pylint: disable=broad-except
            if cron_mode:
                _logger.warning(
                    "dtx_datev_export: send_system_data failed (cron_mode)",
                    exc_info=True,
                )
                return False
            raise UserError(
                _("Error communicating with the Detalex server.")
            )
        return True

    def _post_messages(self, messages):
        """Post notification messages to the employee channel (if mail is installed)."""
        if not messages:
            return
        if 'mail.channel' not in self.env:
            _logger.debug("mail module not installed, skipping message posting")
            return
        try:
            poster = self.sudo().env.ref('mail.channel_all_employees')
            for message in messages:
                try:
                    poster.message_post(
                        body=message,
                        subtype_xmlid='mail.mt_comment',
                    )
                except Exception:  # pylint: disable=broad-except
                    _logger.debug(
                        "Could not post notification message", exc_info=True
                    )
        except Exception:  # pylint: disable=broad-except
            _logger.debug("Could not access employee channel", exc_info=True)
