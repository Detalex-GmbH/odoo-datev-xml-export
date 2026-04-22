# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

import logging
import re

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def datev_price_information(self):
        self.ensure_one()
        price = self.price_unit * (1 - (self.discount / 100.0))
        currency = self.currency_id or self.move_id.currency_id or self.company_currency_id
        if not currency:
            raise ValueError(
                "Rechnung '%s', Zeile '%s': Keine Währung hinterlegt. "
                "Bitte prüfen Sie die Währung auf der Rechnung und der Rechnungszeile."
                % (self.move_id.name, self.name or self.id)
            )
        result = self.tax_ids.compute_all(
            price,
            currency,
            self.quantity,
            product=self.product_id,
            partner=self.move_id.partner_id,
        )
        if not result or not isinstance(result, dict):
            _logger.warning(
                "Rechnung '%s', Zeile '%s': Steuerberechnung lieferte kein gültiges Ergebnis. "
                "Bitte prüfen Sie die Steuerkonfiguration dieser Rechnungszeile.",
                self.move_id.name, self.name or self.id,
            )
            return {
                "total_included": price * self.quantity,
                "total_excluded": price * self.quantity,
                "taxes": [],
            }
        return result

    def datev_booking_text(self):
        self.ensure_one()
        return self.datev_name()

    def datev_name(self):
        self.ensure_one()
        name = self.name or ""
        if not name and self.product_id:
            name = self.product_id.name or ""
        return name[:60]

    def datev_cost_category_id(self):
        self.ensure_one()
        analytic = None
        source = "NONE"

        # Log: Track welche Analytics-Felder vorhanden sind
        has_analytic_dist = hasattr(self, "analytic_distribution") and self.analytic_distribution
        has_analytic_account = hasattr(self, "analytic_account_id") and self.analytic_account_id
        has_analytic_lines = bool(self.analytic_line_ids)

        _logger.info(
            "[KOSTENSTELLE-TRACK] move: %s | line_id: %s | "
            "analytic_distribution: %s | analytic_account_id: %s | analytic_line_ids: %s",
            self.move_id.name, self.id,
            "JA" if has_analytic_dist else "NEIN",
            "JA" if has_analytic_account else "NEIN",
            "JA" if has_analytic_lines else "NEIN"
        )

        # Odoo 16+ Standard: analytic_distribution (dict mit account_id als key)
        if hasattr(self, "analytic_distribution") and self.analytic_distribution:
            source = "analytic_distribution"
            account_ids = list(self.analytic_distribution.keys())
            if account_ids:
                # Convert to int if it's a string
                account_id = int(account_ids[0]) if isinstance(account_ids[0], str) else account_ids[0]
                analytic = self.env["account.analytic.account"].browse(account_id)
                _logger.debug(
                    "[KOSTENSTELLE-TRACK] Source: %s | account_id: %s | code: %s",
                    source, account_id, analytic.code if analytic else "N/A"
                )

        # Fallback: klassisches Feld analytic_account_id
        elif hasattr(self, "analytic_account_id") and self.analytic_account_id:
            source = "analytic_account_id"
            analytic = self.analytic_account_id
            _logger.debug(
                "[KOSTENSTELLE-TRACK] Source: %s | account_id: %s | code: %s",
                source, analytic.id, analytic.code
            )

        # Fallback: analytic_line_ids
        elif self.analytic_line_ids and hasattr(self.analytic_line_ids[0], "account_id"):
            source = "analytic_line_ids"
            analytic = self.analytic_line_ids[0].account_id
            _logger.debug(
                "[KOSTENSTELLE-TRACK] Source: %s | account_id: %s | code: %s",
                source, analytic.id, analytic.code
            )

        # Ensure analytic is a singleton before accessing code
        if analytic and hasattr(analytic, "code"):
            analytic.ensure_one()  # Make sure it's a single record
            if analytic.code:
                result = analytic.code[:36]
                _logger.info(
                    "[KOSTENSTELLE-RESULT] move: %s | source: %s | code: %s",
                    self.move_id.name, source, result
                )
                return result

        _logger.warning(
            "[KOSTENSTELLE-EMPTY] move: %s | line_id: %s | KEINE Kostenstelle gefunden!",
            self.move_id.name, self.id
        )
        return ""


class AccountMove(models.Model):
    _inherit = "account.move"

    datev_exported = fields.Boolean(
        string="Datev XML exported",
        default=False,
        copy=False,
        store=True,
        compute="_compute_datev_exported",
        help="When finishing a datev XML exports the processed invoices are marked as exported to datev.\n",
    )

    datev_export_ids = fields.Many2many(
        "datev.export.xml",
        string="Datev XML Exports",
        copy=False,
        help="The Datev XML Exports this invoice belongs to",
    )

    datev_exports_count = fields.Integer(
        string="Datev XML Exports Count", compute="_compute_datev_exports_count"
    )

    datev_validation = fields.Text(
        string="DATEV Validation Error",
        help="Contains DATEV XML validation errors"
    )

    def datev_format_total(self, value, prec=2):
        self.ensure_one()
        if value is None or value is False:
            _logger.warning(
                "Rechnung '%s': Betrag ist leer (None/False). "
                "Bitte prüfen Sie die Beträge auf der Rechnung.",
                self.name,
            )
            value = 0.0
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Rechnung '%s': Ungültiger Betrag '%s'. "
                "Bitte prüfen Sie die Beträge auf der Rechnung."
                % (self.name, value)
            )
        return (
            f"{-value:.{prec}f}"
            if self.move_type.endswith("_refund")
            else f"{value:.{prec}f}"
        )

    def datev_sanitize(self, value, length=36):
        # Handle None, False, or empty values
        if not value:
            return ""
        # Ensure value is a string
        if not isinstance(value, str):
            value = str(value)
        return re.sub(r"[^a-zA-Z0-9$%&\*\+\-/]", "-", value)[:length]

    def datev_filename(self, extension=".pdf"):
        self.ensure_one()
        return self.name.replace("/", "-") + extension

    def datev_drawee_no(self):
        self.ensure_one()
        # Return sanitized reversed entry name or False
        # reversed_entry_id points to the original invoice for credit notes/refunds
        # Return False (not empty string) so QWeb doesn't create empty attribute
        if self.reversed_entry_id:
            # Ensure it's a recordset and has a name
            return self.datev_sanitize(self.reversed_entry_id.name or "")
        return False

    def datev_delivery_date(self):
        """Return the most recent delivery date from done stock pickings.

        Lookup path depends on invoice type:
        - Customer invoice → sale order → outgoing pickings
        - Vendor bill      → purchase order → incoming pickings

        Falls back to invoice_date when no picking is found.
        Must never raise — called from QWeb template during XML generation.
        """
        self.ensure_one()
        try:
            if "stock.picking" not in self.env:
                return self.invoice_date

            pickings = self.env["stock.picking"]
            if self.move_type == "out_invoice" and "sale_line_ids" in self.env["account.move.line"]._fields:
                pickings = self.mapped("invoice_line_ids.sale_line_ids.order_id.picking_ids")
            elif self.move_type == "in_invoice" and "purchase_order_id" in self.env["account.move.line"]._fields:
                pickings = self.mapped("invoice_line_ids.purchase_order_id.picking_ids")

            done_pickings = pickings.filtered(lambda p: p.state == "done" and p.date_done)
            if done_pickings:
                return done_pickings.sorted("date_done", reverse=True)[0].date_done.date()

            # No done pickings — try scheduled_date from any non-cancelled picking
            scheduled = pickings.filtered(lambda p: p.state != "cancel" and p.scheduled_date)
            if scheduled:
                return scheduled.sorted("scheduled_date", reverse=True)[0].scheduled_date.date()

        except Exception:
            _logger.warning("Error computing delivery date for %s", self.name, exc_info=True)

        return self.invoice_date

    def datev_invoice_type(self):
        self.ensure_one()
        if self.move_type in ["out_invoice", "in_invoice"]:
            return "Rechnung"
        return "Gutschrift/Rechnungskorrektur"

    def datev_invoice_id(self):
        self.ensure_one()
        return self.datev_sanitize(self.name or "")

    def datev_order_id(self):
        self.ensure_one()
        origin = self.invoice_origin or ""
        if self.move_type not in (
            "in_invoice",
            "in_refund",
            "out_invoice",
            "out_refund",
        ):
            return self.datev_sanitize(origin)

        # Use the correct setting
        if self.move_type.startswith("in_"):
            ref_field = self.sudo().company_id.datev_vendor_order_ref
        else:
            ref_field = self.sudo().company_id.datev_customer_order_ref

        # Show the original move because ref is a combined value for refund
        if ref_field == "partner" and self.move_type.endswith("_refund"):
            return self.datev_sanitize(self.reversed_entry_id.name or origin)

        # Show the partner reference from the orders stored in ref
        if ref_field == "partner":
            return self.datev_sanitize(self.ref or origin)

        # Show the payment reference
        if ref_field == "payment":
            return self.datev_sanitize(self.payment_reference or origin)

        return self.datev_sanitize(origin)

    def datev_export(self):

        invoice_ids = []
        for move in self:
            if move.datev_exported:
                continue
            invoice_ids.append(move.id)

        if not invoice_ids:
            return False

        self.env["datev.export.xml"].create(
            {
                "company_id": self.env.user.company_id.id,
                "invoice_ids": [(6, 0, invoice_ids)],
            }
        )

        return True

    @api.depends("datev_export_ids")
    def _compute_datev_exports_count(self):
        for record in self:
            record.datev_exports_count = len(record.datev_export_ids)

    def action_show_related_datev_exports_view(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "list,kanban,form",
            "res_model": "datev.export.xml",
            "target": "current",
            "name": _("Datev XML Exports"),
            "domain": [("id", "in", self.datev_export_ids.ids)],
        }

    @api.depends("datev_export_ids")
    def _compute_datev_exported(self):
        for record in self:
            record.datev_exported = bool(record.datev_export_ids)
