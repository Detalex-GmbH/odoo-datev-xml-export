# -*- coding: utf-8 -*-
# Copyright (c) 2025 Detalex GmbH <https://detalex.de>
# License Other proprietary

# pylint: disable=invalid-name
import base64
import io
import logging
import zipfile

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DatevZipGenerator(models.AbstractModel):
    _name = "datev.zip.generator"
    _description = "DATEV ZIP Generator"
    _inherit = ["datev.pdf.generator", "datev.xml.generator"]

    @api.model
    def check_valid_data(self, invoices):
        if not invoices:
            raise UserError(_("No Invoices Selected!"))

        for invoice in invoices:
            if not invoice.partner_id.name and not invoice.partner_id.parent_name:
                raise UserError(
                    _(
                        "Data Insufficient!\nYou have to fill the address for "
                        "partner of invoice {}. The partner address has to have "
                        "official company name!"
                    ).format(invoice.name)
                )

    @api.model
    def generate_zip(self, invoices, check_xsd, export):
        self.check_valid_data(invoices)
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
                        "Error while generating zip file for invoice %s: %s",
                        invoice.name,
                        error_msg,
                    )
                    invoice.datev_validation = error_msg

            if errors:
                export._compute_problematic_invoices_count()

                # Append errors to export.exception_info
                existing = export.exception_info or ""
                new_errors = "\n".join(errors)
                if existing:
                    export.exception_info = f"{existing}\n{new_errors}"
                else:
                    export.exception_info = new_errors

                # Markiere Export als failed
                export.state = "failed"

                _logger.warning(
                    "DATEV Export completed with errors:\n%s",
                    new_errors,
                )
            zip_file.close()
            return base64.b64encode(s.getvalue())
