# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

import logging
import re

from lxml import etree
from odoo import _, api, models, tools

_logger = logging.getLogger(__name__)


class DatevXmlGenerator(models.AbstractModel):
    _name = "datev.xml.generator"
    _description = "DATEV XML Generator"

    @api.model
    def check_xml_file(self, doc_name, root, xsd=None, invoice=None, export=None):
        if not xsd:
            xsd = "Document_v050.xsd"

        schema = tools.file_open(f"dtx_datev_export_xml/xsd_files/{xsd}")
        try:
            schema = etree.XMLSchema(etree.parse(schema))
            schema.assertValid(root)

            # Successful validation - clear any previous validation errors
            if invoice:
                invoice.datev_validation = False

        except (etree.DocumentInvalid, etree.XMLSyntaxError) as e:
            _logger.warning(etree.tostring(root))

            error_msg = f"XML Validation Error in {doc_name}: {str(e)}"

            if invoice:
                invoice.datev_validation = error_msg

            if export:
                # Add validation error to export record using exception_info
                current_exception = export.exception_info or ""
                if current_exception:
                    export.exception_info = f"{current_exception}\n{error_msg}"
                else:
                    export.exception_info = error_msg

        return True

    @api.model
    def _check_invoices(self, invoices):
        # Check against double taxes
        problems = invoices.browse()
        for invoice in invoices:
            if any(len(line.tax_ids) > 1 for line in invoice.invoice_line_ids):
                problems |= invoice

        if problems:
            raise ValueError(
                _(
                    "There are multiple taxes in the following invoices: %(invoices)s",
                    invoices=", ".join(problems.mapped("name")),
                )
            )

    @api.model
    def generate_xml_document(self, invoices, export, check_xsd=True):
        self._check_invoices(invoices)

        root = etree.fromstring(
            self.env["ir.qweb"]._render(
                "dtx_datev_export_xml.export_invoice_document",
                {"docs": invoices, "company": self.env.company, "export": export},
            ),
            parser=etree.XMLParser(remove_blank_text=True),
        )

        if check_xsd:
            self.check_xml_file(
                "document.xml",
                root,
                "Document_v050.xsd",
                export=export,
            )

        return "document.xml", etree.tostring(root)

    @api.model
    def generate_xml_invoice(self, invoice, export, check_xsd=True):
        doc_name = re.sub(r"[^a-zA-Z0-9_\-.()]", "", f"{invoice.name}.xml")
        root = etree.fromstring(
            self.env["ir.qweb"]._render(
                "dtx_datev_export_xml.export_invoice",
                {"doc": invoice, "company": self.env.company, "export": export},
            ),
            parser=etree.XMLParser(remove_blank_text=True),
        )

        if check_xsd:
            self.check_xml_file(
                doc_name,
                root,
                "Belegverwaltung_online_invoice_v050.xsd",
                invoice=invoice,
                export=export,
            )

        return doc_name, etree.tostring(root)
