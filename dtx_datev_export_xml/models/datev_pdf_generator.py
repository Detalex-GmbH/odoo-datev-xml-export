# -*- coding: utf-8 -*-
# Copyright (c) 2025-2026 Detalex GmbH <https://detalex.de>
# License Other proprietary

import base64
import logging
from collections import namedtuple

from odoo import api, models
from odoo.tools import pdf

_logger = logging.getLogger(__name__)


class DatevPdfGenerator(models.AbstractModel):
    _name = "datev.pdf.generator"
    _description = "DATEV PDF Generator"

    @api.model
    def report_name(self):
        return "account.report_invoice"

    @api.model
    def find_existing_attachments(self, account_move):
        self.env.cr.execute(
            """
            SELECT id
            FROM ir_attachment
            WHERE res_id = ANY(%s)
              AND res_model = %s
              AND mimetype = %s
            ORDER BY create_date ASC
        """,
            (account_move.ids, "account.move", "application/pdf"),
        )
        attachment_ids = self.env.cr.fetchall()
        return self.env["ir.attachment"].browse(
            [attachment[0] for attachment in attachment_ids]
        )

    @api.model
    def generate_pdf(self, move):

        def merge_pdfs_to_base64(attachments):
            pdf_datas = [
                base64.decodebytes(attachment.datas) for attachment in attachments
            ]
            report = namedtuple("Report", ["content", "filetype"])
            report_make = report._make((pdf.merge_pdf(pdf_datas), "pdf"))
            return report_make.content

        is_bill = move.move_type in ["in_invoice", "in_refund"]

        # Look for the last attached PDF file assuming this is the most recent
        # and valid one
        attachments = self.find_existing_attachments(move)

        if not attachments:
            if is_bill:
                # If no attachment found, raise an error if the move is a bill
                error_msg = "No PDF attachment found for bill %s (%s)" % (move.name, move.id)
                _logger.error(
                    "No PDF attachment found for bill %s (%s)", move.name, move.id
                )
                raise ValueError(error_msg)
            # else move is a invoice, so we can generate a document
            report = self.env["ir.actions.report"].search(
                [
                    ("model", "=", "account.move"),
                    ("report_name", "=", self.report_name()),
                ],
                limit=1,
            )
            if not report:
                _logger.error("No report found for model account.move")
                raise ValueError("No report found for model account.move")

            new_invoice = report._render(
                res_ids=move.ids, report_ref=self.report_name()
            )[0]
            # Create a new attachment
            attachment = self.env["ir.attachment"].create(
                {
                    "name": "%s.pdf" % move.name,
                    "type": "binary",
                    "res_model": "account.move",
                    "res_id": move.id,
                    "mimetype": "application/pdf",
                    "datas": base64.b64encode(new_invoice),
                }
            )
            # Attach the PDF to the move
            move.message_post(
                body="PDF generated while exporting to DATEV",
                attachments=[
                    ("%s.pdf" % move.name, base64.b64decode(attachment["datas"]))
                ],
            )
            # Return the PDF content as a base64 encoded string
            return base64.b64decode(attachment["datas"])

        if len(attachments) > 1:
            # If there are multiple attachments, merge them
            merged_pdf = merge_pdfs_to_base64(attachments)
            return merged_pdf

        attachment = attachments[0]
        # Return the PDF content as a base64 encoded string
        return base64.b64decode(attachment["datas"])
