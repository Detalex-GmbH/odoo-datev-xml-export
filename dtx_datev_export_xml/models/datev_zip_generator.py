# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary
# pylint: disable=invalid-name

import base64
import io
import logging
import zipfile

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class DatevZipGenerator(models.AbstractModel):
    _name = "datev.zip.generator"
    _description = "DATEV ZIP Generator"
    _inherit = ["datev.pdf.generator", "datev.xml.generator"]

    @api.model
    def _validate_invoices(self, invoices):
        """Validate all invoices and return a list of error messages.

        Does NOT raise — always checks every invoice so the user sees all
        problems at once.
        """
        errors = []

        if not invoices:
            errors.append(_("Keine Rechnungen ausgewählt! "
                            "Bitte wählen Sie mindestens eine Rechnung für den Export."))
            return errors

        for invoice in invoices:
            if not invoice.partner_id:
                errors.append(
                    _("Rechnung '%s': Kein Partner/Kunde hinterlegt. "
                      "Bitte weisen Sie der Rechnung einen Partner zu.") % invoice.name
                )
                continue
            if not invoice.partner_id.name and not invoice.partner_id.parent_name:
                errors.append(
                    _("Rechnung '%s': Der Partner '%s' hat keinen Firmennamen. "
                      "Bitte tragen Sie den offiziellen Firmennamen in den Partnerstammdaten ein.")
                    % (invoice.name, invoice.partner_id.display_name or invoice.partner_id.id)
                )

        # Check that all invoices have a PDF attachment (or can generate one)
        for invoice in invoices:
            attachments = self.find_existing_attachments(invoice)
            is_bill = invoice.move_type in ("in_invoice", "in_refund")

            if not attachments:
                if is_bill:
                    # Vendor bills cannot generate PDFs — attachment is mandatory
                    errors.append(
                        _("Rechnung '%s': Kein PDF-Anhang gefunden. "
                          "Eingangsrechnungen benötigen ein angehängtes PDF-Dokument. "
                          "Bitte laden Sie das PDF der Rechnung als Anhang hoch.") % invoice.name
                    )
                else:
                    # Outgoing invoices can generate PDFs — check that the report exists
                    report = self.env["ir.actions.report"].search(
                        [
                            ("model", "=", "account.move"),
                            ("report_name", "=", self.report_name()),
                        ],
                        limit=1,
                    )
                    if not report:
                        errors.append(
                            _("Rechnung '%s': Kein PDF-Anhang vorhanden und der Rechnungsbericht '%s' "
                              "wurde nicht gefunden. Bitte laden Sie ein PDF hoch oder installieren Sie "
                              "den Rechnungsbericht.") % (invoice.name, self.report_name())
                        )
            else:
                # Attachments exist — check that they contain data
                empty_atts = [att for att in attachments if not att.datas]
                if empty_atts:
                    empty_names = [att.name or str(att.id) for att in empty_atts]
                    errors.append(
                        _("Rechnung '%s': Folgende PDF-Anhänge enthalten keine Daten: %s. "
                          "Bitte laden Sie die Dokumente erneut hoch.")
                        % (invoice.name, ", ".join(empty_names))
                    )

        return errors

    @api.model
    def generate_zip(self, invoices, check_xsd, export):
        # --- Phase 1: Validate all invoices upfront ---
        validation_errors = self._validate_invoices(invoices)
        if validation_errors:
            error_text = "\n".join(validation_errors)
            for inv in invoices:
                inv_errors = [e for e in validation_errors if inv.name in str(e)]
                if inv_errors:
                    inv.datev_validation = "\n".join(inv_errors)
            export.exception_info = error_text
            export.state = "failed"
            _logger.warning("DATEV Export Validierung fehlgeschlagen:\n%s", error_text)
            return None

        # --- Phase 2: Generate ZIP (all invoices validated) ---
        with io.BytesIO() as s, zipfile.ZipFile(s, mode="w") as zip_file:

            xml_document_data = self.generate_xml_document(invoices, export, check_xsd)
            zip_file.writestr(
                xml_document_data[0],
                xml_document_data[1],
                zipfile.ZIP_DEFLATED,
            )

            errors = []
            for invoice in invoices.with_context(progress_iter=True):
                try:
                    _logger.debug(
                        "[ZIP-TRACK] invoice: %s | lines: %d",
                        invoice.name,
                        len(invoice.invoice_line_ids)
                    )

                    # attach pdf file for vendor bills
                    attachment = self.generate_pdf(invoice)
                    zip_file.writestr(
                        invoice.datev_filename(),
                        attachment,
                        zipfile.ZIP_DEFLATED,
                    )

                    # create xml file for invoice
                    xml_invoice_data = self.generate_xml_invoice(
                        invoice, self, check_xsd
                    )
                    zip_file.writestr(
                        invoice.datev_filename(".xml"),
                        xml_invoice_data[1],
                        zipfile.ZIP_DEFLATED,
                    )
                except Exception as e:
                    error_msg = f"{invoice.name}: {e}"
                    errors.append(error_msg)
                    _logger.error(
                        "Fehler beim DATEV-Export für Rechnung %s: %s",
                        invoice.name,
                        str(e),
                        exc_info=True,
                    )
                    invoice.datev_validation = str(e)

            if errors:
                export._compute_problematic_invoices_count()

                existing = export.exception_info or ""
                new_errors = "\n".join(errors)
                if existing:
                    export.exception_info = f"{existing}\n{new_errors}"
                else:
                    export.exception_info = new_errors

                export.state = "failed"

                _logger.warning(
                    "DATEV Export mit Fehlern abgeschlossen — kein ZIP erstellt:\n%s",
                    new_errors,
                )
                # Return None so that get_zip() does NOT create an attachment
                return None

            zip_file.close()
            return base64.b64encode(s.getvalue())
