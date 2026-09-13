from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    mbs_control_state = fields.Selection(
        [
            ("ok", "Conforme"),
            ("warning", "A verifier"),
        ],
        string="Controle MBS",
        compute="_compute_mbs_controls",
        store=False,
    )
    mbs_control_message = fields.Text(
        string="Anomalies detectees",
        compute="_compute_mbs_controls",
        store=False,
    )

    @api.depends(
        "move_type",
        "partner_id",
        "partner_id.mbs_ice",
        "invoice_date",
        "invoice_date_due",
        "invoice_line_ids.tax_ids",
        "invoice_line_ids.price_subtotal",
    )
    def _compute_mbs_controls(self):
        for move in self:
            warnings = []

            if move.move_type in ("out_invoice", "out_refund", "in_invoice", "in_refund"):
                if not move.partner_id:
                    warnings.append("Client/fournisseur absent.")
                elif move.partner_id.is_company and not move.partner_id.mbs_ice:
                    warnings.append("ICE du tiers non renseigne.")

                if not move.invoice_date:
                    warnings.append("Date de facture absente.")

                taxable_lines = move.invoice_line_ids.filtered(
                    lambda line: not line.display_type and line.price_subtotal
                )
                if taxable_lines and not any(taxable_lines.mapped("tax_ids")):
                    warnings.append("Aucune taxe detectee sur les lignes facturables.")

            move.mbs_control_state = "warning" if warnings else "ok"
            move.mbs_control_message = "\n".join(warnings) if warnings else "Aucune anomalie detectee."
