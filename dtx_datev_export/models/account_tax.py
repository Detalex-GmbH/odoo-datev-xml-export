# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    l10n_de_datev_code = fields.Char(
        string="DATEV-Buchungsschlüssel (BU-Code)",
        help="""4-stelliger Code für die DATEV Steuerautomatik (z.B. 9 für 19%% Vorsteuer, 3 für 19%% Umsatzsteuer).

WICHTIG: Sprechen Sie mit Ihrer Steuerkanzlei, bevor Sie dieses Feld ausfüllen!

• Leer lassen = DATEV ordnet Steuer automatisch zu (empfohlen für den Start)
• Code eintragen = DATEV nutzt diesen Code für Steuerautomatik

Der BU-Code steuert in DATEV:
- Automatische Kontenfindung
- Automatische Steuerberechnung
- Automatische UStVA-Zuordnung

Ausführliche Dokumentation:
https://github.com/Detalex-GmbH/odoo-datev-xml-export/blob/18.0/dtx_datev_export/README_BU_CODE.md"""
    )
