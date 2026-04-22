# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary
# pylint: disable=assigning-non-slot
# pylint: disable=invalid-name
# pylint: disable=no-raise-unlink
# pylint: disable=pointless-statement
# pylint: disable=no-else-return
# pylint: disable=unused-format-string-key

# pylint: disable=redefined-outer-name
# pylint: disable=simplifiable-if-expression
import datetime
import logging
import time
import urllib.parse
import urllib.request

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DatevExport(models.Model):
    _name = "datev.export.xml"
    _inherit = ["mail.thread", "mail.activity.mixin", "datev.zip.generator"]
    _description = "DATEV XML Export"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        timestamp = datetime.datetime.now()
        res["display_name"] = (
            f"DATEV XML Export {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return res

    @api.model
    def _default_start(self, today=None):
        today = today or datetime.date.today()
        default_period = self.env.company.datev_default_period
        if default_period == "week":
            return today - datetime.timedelta(days=today.weekday(), weeks=1)

        if default_period == "month":
            date = datetime.date(day=1, month=today.month, year=today.year)
            date_stop = date - datetime.timedelta(days=1)
            return datetime.date(day=1, month=date_stop.month, year=date_stop.year)

        if default_period == "year":
            return datetime.date(day=1, month=1, year=today.year - 1)

        return today - datetime.timedelta(days=1)

    @api.model
    def _default_stop(self, today=None):
        today = today or datetime.date.today()
        default_period = self.env.company.datev_default_period

        if default_period == "week":
            date_start = today - datetime.timedelta(days=today.weekday(), weeks=1)
            return date_start + datetime.timedelta(days=6)

        if default_period == "month":
            date = datetime.date(day=1, month=today.month, year=today.year)
            return date - datetime.timedelta(days=1)

        if default_period == "year":
            return datetime.date(day=31, month=12, year=today.year - 1)

        return today - datetime.timedelta(days=1)

    def name_get(self):
        # create a name for the record
        return [
            (rec.id, f"DATEV XML Export {rec.date_start} - {rec.date_stop}")
            for rec in self
        ]

    date_start = fields.Date(
        "From Date",
        default=_default_start,
    )
    date_stop = fields.Date(
        "To Date",
        default=_default_stop,
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )
    check_xsd = fields.Boolean(
        "Check DATEV XML Schema",
        default=True,
    )

    export_bu_code = fields.Boolean(
        string="DATEV Buchungscode (BU-Code) exportieren",
        default=False,
        help="""Aktivieren Sie diese Option, um BU-Codes (Buchungsschlüssel) im DATEV XML-Export zu übertragen.

WICHTIG: Sprechen Sie mit Ihrer Steuerkanzlei, bevor Sie diese Option aktivieren!

• Deaktiviert (empfohlen): DATEV ordnet Steuern automatisch zu
• Aktiviert: DATEV nutzt die in Odoo hinterlegten BU-Codes für Steuerautomatik

Voraussetzungen wenn aktiviert:
- BU-Codes müssen in Steuern korrekt gepflegt sein
- Kanzlei muss über die Verwendung informiert sein
- Nur eine Steuer pro Rechnungszeile verwenden

Bei falschen BU-Codes kann es zu Buchungsfehlern in DATEV kommen!

Ausführliche Dokumentation:
https://github.com/Detalex-GmbH/odoo-datev-xml-export/blob/18.0/dtx_datev_export/README_BU_CODE.md"""
    )

    # Document type filters
    include_out_invoice = fields.Boolean(
        "Ausgehende Rechnungen",
        default=True,
        help="Include customer invoices in export"
    )
    include_out_refund = fields.Boolean(
        "Ausgehende Gutschriften",
        default=True,
        help="Include customer credit notes in export"
    )
    include_in_invoice = fields.Boolean(
        "Eingehende Rechnungen",
        default=True,
        help="Include vendor bills in export"
    )
    include_in_refund = fields.Boolean(
        "Eingehende Gutschriften",
        default=True,
        help="Include vendor refunds in export"
    )

    attachment_id = fields.Many2one(
        comodel_name="ir.attachment", string="Attachment", required=False, readonly=True
    )
    datev_file = fields.Binary("ZIP file", readonly=True, related="attachment_id.datas")
    datev_filename = fields.Char(
        "ZIP filename", readonly=True, related="attachment_id.name"
    )
    datev_filesize = fields.Char(
        "Filesize",
        compute="_compute_datev_filesize",
    )

    problematic_invoices_count = fields.Integer(
        compute="_compute_problematic_invoices_count"
    )
    invoice_ids = fields.Many2many(
        comodel_name="account.move",
        string="Invoices",
        ondelete="restrict",
        copy=False,
        readonly=True,
    )
    invoices_count = fields.Integer(
        compute="_compute_invoices_count", store=True, string="Dokumenten"
    )

    exception_info = fields.Text(readonly=True)
    exception_reported = fields.Boolean(
        default=False,
        readonly=True,
        help='True when exception was reported to Detalex support.',
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("running", "Running"),
            ("done", "Done"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )

    def get_description(self):
        """
        Erstellt eine vollständige Beschreibung für den Export basierend auf den gewählten Optionen.
        """
        generating_system = self.generating_system()

        # Build document types list
        doc_types = []
        if self.include_out_invoice:
            doc_types.append("Ausgehende Rechnungen")
        if self.include_out_refund:
            doc_types.append("Ausgehende Gutschriften")
        if self.include_in_invoice:
            doc_types.append("Eingehende Rechnungen")
        if self.include_in_refund:
            doc_types.append("Eingehende Gutschriften")

        doc_types_str = ", ".join(doc_types) if doc_types else "Alle Dokumententypen"

        return (
            "%(count)s Dokumenten exportiert mit %(generating_system)s\n"
            "%(period)s\n"
            "%(doc_types)s\n"
            % {
                "count": len(self.invoice_ids),
                "generating_system": generating_system,
                "period": (
                    "Zeitraum: %s - %s" % (self.date_start, self.date_stop)
                    if self.date_start
                    else ""
                ),
                "doc_types": doc_types_str,
            }
        )

    @api.depends("attachment_id", "attachment_id.datas")
    def _compute_datev_filesize(self):
        for r in self.with_context(bin_size=True):
            r.datev_filesize = r.datev_file

    @api.depends("invoice_ids")
    def _compute_problematic_invoices_count(self):
        for r in self:
            # Nur echte Probleme zählen (non-empty strings)
            # datev_validation kann False, None oder "" sein = kein Problem
            # Nur wenn es einen nicht-leeren String gibt = Problem
            problematic = r.invoice_ids.filtered(
                lambda inv: inv.datev_validation and isinstance(
                    inv.datev_validation, str) and inv.datev_validation.strip()
            )
            r.problematic_invoices_count = len(problematic)

    @api.depends("invoice_ids")
    def _compute_invoices_count(self):
        for r in self:
            r.invoices_count = len(r.invoice_ids)

    def get_invoices(self):
        """Get invoices based on date range and document type filters."""
        # Build move_type filter based on checkboxes
        move_types = []
        if self.include_out_invoice:
            move_types.append('out_invoice')
        if self.include_out_refund:
            move_types.append('out_refund')
        if self.include_in_invoice:
            move_types.append('in_invoice')
        if self.include_in_refund:
            move_types.append('in_refund')

        # Validate that at least one type is selected
        if not move_types:
            raise UserError(
                _("Keine Dokumententypen ausgewählt!\n"
                  "Bitte wählen Sie mindestens einen Dokumententyp aus.")
            )

        search_clause = [
            ("amount_untaxed", "!=", 0),
            ("amount_total", "!=", 0),
            ("state", "in", ("posted", "open")),
            ("company_id", "=", self.company_id.id),
            ("datev_exported", "=", False),
            ("move_type", "in", move_types),  # Filter by selected types
        ]

        if self.date_start:
            search_clause.append(("invoice_date", ">=", self.date_start))
            if self.date_stop:
                search_clause.append(("invoice_date", "<=", self.date_stop))
        else:
            raise UserError(
                _("Data Insufficient!\nPlease select Period or at least Start Date.")
            )
        return self.env["account.move"].search(search_clause)

    def generating_system(self):
        # return Detalex Datex Export mit version der Addon"
        addon_version = (
            self.env["ir.module.module"]
            .search([("name", "=", "dtx_datev_export_xml")])
            .installed_version
        )
        return f"Detalex DATEV XML Export {addon_version}"

    def get_zip(self):
        self = self.with_context(bin_size=False)

        try:
            if self.attachment_id:
                self.attachment_id.unlink()

            self.write({"state": "running"})

            zip_data = self.generate_zip(self.invoice_ids, self.check_xsd, self)

            # Reload self from database to get updated state from generate_zip()
            self = self.browse(self.id)

            if zip_data and self.state != "failed":
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": time.strftime("%Y_%m_%d_%H_%M") + ".zip",
                        "datas": zip_data,
                        "res_model": "datev.export.xml",
                        "res_id": self.id,
                        "res_field": "attachment_id",
                        "description": self.get_description(),
                    }
                )
                self.write({"attachment_id": attachment.id, "state": "done"})
                self.message_post(
                    body=self.get_description(),
                    attachment_ids=[attachment.id],
                )
                # Send success log to Detalex server
                self._report_success_to_detalex()
            else:
                # generate_zip() returned None or state is already "failed"
                # Errors are already in exception_info and invoice.datev_validation
                _logger.warning(
                    "[EXPORT] Export %s fehlgeschlagen — kein ZIP erstellt. Fehler: %s",
                    self.id, self.exception_info,
                )

        except Exception as e:
            _logger.error("[EXPORT] Exception in get_zip(): %s", str(e), exc_info=True)
            msg = e.name if hasattr(e, "name") else str(e)
            existing = self.exception_info or ""
            combined = f"{existing}\n{msg}" if existing else msg
            self.write({"exception_info": combined, "state": "failed"})

        self._compute_problematic_invoices_count()

        # Auto-report errors to Detalex support (must never break the export flow)
        try:
            self_fresh = self.browse(self.id)
            if self_fresh.state == "failed" and self_fresh.exception_info:
                self_fresh._report_exception_to_detalex()
        except Exception:  # pylint: disable=broad-except
            _logger.warning("[EXPORT] Auto-report to Detalex failed", exc_info=True)

    def _report_success_to_detalex(self):
        """Send success info to Detalex client_log endpoint."""
        try:
            dbuuid = self.env['ir.config_parameter'].sudo().get_param(
                'database.uuid', ''
            )
            dbname = self.env.cr.dbname
            company = self.env.company.name or dbname
            invoice_count = len(self.invoice_ids)

            payload = str({
                'dbuuid': dbuuid,
                'type': 'info',
                'subject': f'DATEV Export OK: {company} ({dbname}) – {invoice_count} Belege',
                'body': self.get_description(),
            })

            data = urllib.parse.urlencode({
                'arg0': payload,
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://detalex.de/client_log',
                data=data,
                method='POST',
            )
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, timeout=10):
                pass

        except Exception:  # pylint: disable=broad-except
            _logger.debug("[EXPORT] Could not report success to Detalex", exc_info=True)

    def _report_exception_to_detalex(self):
        """Send consolidated exception_info to Detalex client_log endpoint."""
        try:
            dbuuid = self.env['ir.config_parameter'].sudo().get_param(
                'database.uuid', ''
            )
            dbname = self.env.cr.dbname
            company = self.env.company.name or dbname

            payload = str({
                'dbuuid': dbuuid,
                'type': 'error',
                'subject': f'DATEV Export failed: {company} ({dbname})',
                'body': self.exception_info or '',
            })

            data = urllib.parse.urlencode({
                'arg0': payload,
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://detalex.de/client_log',
                data=data,
                method='POST',
            )
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            with urllib.request.urlopen(req, timeout=10):
                pass

            self.write({'exception_reported': True})
            _logger.info("[EXPORT] Exception reported to Detalex for export %s", self.id)

        except Exception as e:  # pylint: disable=broad-except
            _logger.warning(
                "[EXPORT] Could not report exception to Detalex: %s", e
            )

    def action_report_exception(self):
        """Button action: manually send exception to Detalex support."""
        self.ensure_one()
        if not self.exception_info:
            raise UserError(_("No exception to report."))
        self._report_exception_to_detalex()
        if not self.exception_reported:
            raise UserError(_("Fehler konnte nicht gesendet werden. Bitte prüfen Sie die Netzwerkverbindung."))

    @api.model
    def cron_run_pending_export(self):
        datev_export = self.search(
            [("state", "=", "pending")],
        )
        while datev_export:
            datev_export.with_user(datev_export.create_uid.id).get_zip()
            datev_export._create_activity()

        return True

    def action_create_export(self):
        self.ensure_one()
        self.invoice_ids = [(6, 0, self.get_invoices().ids)]
        return True

    def export_zip(self):
        self.ensure_one()

        if self.env.context.get("wizard"):
            return self._return_wizard_action()
        else:
            self.action_pending()
        return True

    @api.model
    def export_zip_invoice(self, invoice_ids=None):

        def check_invoices_have_attachments(self, invoice_ids):
            """Check if all given invoices have at least one PDF attachment."""
            if not invoice_ids:
                return

            invoices_to_check = self.env["account.move"].browse(invoice_ids)
            # check all invoice have allowed type
            allowed_types = ["out_invoice", "in_invoice", "out_refund", "in_refund"]
            invoices_types = invoices_to_check.mapped("move_type")
            # check all invoice have allowed type
            invalid_types = [t for t in invoices_types if t not in allowed_types]
            if invalid_types:
                raise UserError(
                    _(
                        "Folgende Dokumententypen können nicht exportiert werden: %s\n"
                        "Erlaubte Typen: %s\n"
                        "Bitte wählen Sie nur Rechnungen und Gutschriften aus."
                    )
                    % (", ".join(invalid_types), ", ".join(allowed_types))
                )

            self.env.cr.execute(
                """
                SELECT am.name
                FROM account_move am
                LEFT JOIN ir_attachment ia
                    ON ia.res_model = 'account.move'
                    AND ia.res_id = am.id
                    AND ia.mimetype = 'application/pdf'
                WHERE am.id IN %s
                GROUP BY am.id, am.name
                HAVING COUNT(ia.id) = 0
            """,
                (tuple(invoice_ids),),
            )

            missing_names = [row[0] for row in self.env.cr.fetchall()]

            if missing_names:
                raise UserError(
                    _("Folgende Dokumente haben kein PDF angehängt:\n%s\n\n"
                      "Bitte laden Sie für diese Rechnungen jeweils ein PDF-Dokument als Anhang hoch.")
                    % "\n".join(missing_names)
                )

        if not invoice_ids and self.env.context.get("active_model") == "account.move":
            invoice_ids = self.env.context.get("active_ids")

        invoices = self.env["account.move"].browse(invoice_ids)

        # check all invoice are not draft
        if any(invoice.state == "draft" for invoice in invoices):
            raise UserError(
                _(
                    "You can't export draft invoices!\nPlease set all invoices to posted!"
                )
            )
        # check all invoice have attachment
        check_invoices_have_attachments(self, invoice_ids)

        datev_export = self.create(
            {
                "invoice_ids": [(6, 0, invoice_ids)],
                "date_start": False,
                "date_stop": False,
            }
        )
        datev_export.get_zip()
        datev_export._create_activity()
        return datev_export._return_wizard_action()

    def _return_wizard_action(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "view_id": self.env.ref(
                "dtx_datev_export_xml.view_datev_export_popup_form"
            ).id,
            "res_id": self.id,
            "res_model": self._name,
            "target": "new",
            "context": {"dtx_datev_export_xml": self._name, "wizard": True},
        }

    def _create_activity(self):
        self.ensure_one()
        if self.state == "done":
            note = _("DATEV-XML-Export file is ready to download!")
        elif self.state == "failed":
            note = _("Exception while creating DATEV-XML-Export file!")
        else:
            return
        self.env["mail.activity"].sudo().create(
            {
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "note": note,
                "res_id": self.id,
                "res_model_id": self.env.ref(
                    "dtx_datev_export_xml.model_datev_export_xml"
                ).id,
                "user_id": self.create_uid.id,
            }
        )

    def create_zip(self):
        self.ensure_one()
        # chack context recreate is true
        if self.env.context.get("recreate"):
            self.action_draft()
            self.invoice_ids = [(6, 0, self.get_invoices().ids)]

        # set datev_validation to False and clear exception_info ONLY before getting new zip
        self.invoice_ids.write({"datev_validation": False})
        self.write({"exception_info": False, "exception_reported": False})
        self.get_zip()
        # Only validate if export did NOT fail
        if self.state != "failed":
            self.action_validate()

    def action_validate(self):
        # DO NOT clear exception_info - if there are errors from get_zip(), keep them!
        # Only clear if state is NOT 'failed'
        if self.state != "failed":
            self.write({"exception_info": False, "exception_reported": False})

        generator = self.env["datev.xml.generator"]
        for invoice in self.invoice_ids:
            try:
                generator._check_invoices(invoice)
            except ValueError as e:
                invoice.datev_validation = str(e)
                continue

            try:
                generator.generate_xml_invoice(invoice, self, check_xsd=self.check_xsd)
            except UserError:
                continue

        self._compute_problematic_invoices_count()

        # If validation errors exist after validation, set state to failed
        # This can override "done" state if ZIP was created but validation found errors
        if self.problematic_invoices_count > 0:
            error_msg = _("Export has {} invoice(s) with validation errors").format(
                self.problematic_invoices_count
            )
            self.write({
                "state": "failed",
                "exception_info": error_msg,
            })
            # Remove ZIP attachment if it was created
            if self.attachment_id:
                self.attachment_id.unlink()

    def action_done(self):
        self.filtered(lambda r: r.state in ["running", "failed"]).write(
            {
                "exception_info": _("Manually set to Done by {}!").format(
                    self.env.user
                ),
                "state": "done",
            }
        )

    def action_pending(self):
        for r in self:
            if r.invoices_count == 0:
                raise ValidationError(_("No invoices/refunds for export!"))
            if r.invoices_count > 4999 and r.check_xsd:
                raise ValidationError(
                    _(
                        "The numbers of invoices/refunds is limited to 4999 by DATEV! "
                        "Please decrease the number of documents or deactivate Check XSD."
                    )
                )
            if r.state == "running":
                raise ValidationError(
                    _("It's not allowed to set an already running export to pending!")
                )
            r.write(
                {
                    "state": "pending",
                    "exception_info": False, "exception_reported": False,
                }
            )

    def action_draft(self):
        for r in self:
            if r.state == "running":
                raise ValidationError(
                    _("It's not allowed to set a running export to draft!")
                )

            # set datev_validation to False
            r.invoice_ids.write({"datev_validation": False})

            # remove all linked invoices
            r.invoice_ids = [(6, 0, [])]

            r.attachment_id.unlink()

            # Note: datev_file, datev_filename, datev_filesize are related/computed fields
            # They are automatically cleared when the attachment is deleted above (line 624)

            r.write({"state": "draft", "exception_info": False, "exception_reported": False})

    def action_show_invalid_invoices_view(self):
        """🚨 Magischer Button: Zeigt alle Rechnungen mit Validierungsfehlern"""
        # Finde nur Rechnungen mit datev_validation (nicht False/leer)
        problematic_invoices = self.invoice_ids.filtered(lambda x: x.datev_validation)

        # Logging für debugging
        _logger.info("DATEV: Showing %s problematic invoices", len(problematic_invoices))

        return {
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "account.move",
            "target": "current",
            "name": "🚨 DATEV Validierungsfehler ({} Rechnungen)".format(len(problematic_invoices)),
            "domain": [("id", "in", problematic_invoices.ids)],
            "context": {
                "create": False,
                "edit": False,
            }
        }

    def action_show_related_invoices_view(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "list,kanban,form",
            "res_model": "account.move",
            "target": "current",
            "name": _("Included Invoices"),
            "domain": [("id", "in", self.invoice_ids.ids)],
        }

    def unlink(self):

        if self.filtered(lambda r: r.state != "draft"):
            raise UserError(_("You can only delete drafts!"))
        if self.invoice_ids:
            raise UserError(_("You can't delete an export with linked invoices!"))

        attachments = self.mapped("attachment_id")
        res = super().unlink()
        attachments.exists().unlink()
        return res

    def write(self, vals):
        res = super().write(vals)
        if any(
            changed_value in vals
            for changed_value in [
                "date_start",
                "date_stop",
            ]
        ):
            for record in self:
                super().write({"invoice_ids": [(6, 0, record.get_invoices().ids)]})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if not record.invoice_ids:
                record.invoice_ids = [(6, 0, record.get_invoices().ids)]
        return records
