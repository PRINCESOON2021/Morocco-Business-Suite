from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    mbs_control_state = fields.Selection(
        [("ok", "Conforme"), ("warning", "A verifier")],
        compute="_compute_mbs_controls",
        store=True,
        index=True,
        string="Controle MBS",
    )
    mbs_control_message = fields.Text(
        compute="_compute_mbs_controls",
        store=True,
        string="Anomalies detectees",
    )

    @api.depends(
        "partner_id",
        "partner_id.mbs_ice",
        "partner_ref",
        "order_line.product_id",
        "order_line.product_qty",
        "order_line.price_unit",
        "state",
        "invoice_status",
    )
    def _compute_mbs_controls(self):
        for order in self:
            warnings = []
            if not order.partner_id:
                warnings.append("Fournisseur absent.")
            elif order.partner_id.is_company and not order.partner_id.mbs_ice:
                warnings.append("ICE fournisseur non renseigne.")

            commercial_lines = order.order_line.filtered(lambda line: not line.display_type)
            if not commercial_lines:
                warnings.append("Aucune ligne d'achat.")
            if any(line.product_qty <= 0 for line in commercial_lines):
                warnings.append("Une ligne contient une quantite nulle ou negative.")
            if any(line.price_unit < 0 for line in commercial_lines):
                warnings.append("Une ligne contient un prix unitaire negatif.")

            if order.state in ("purchase", "done") and order.invoice_status == "to invoice":
                warnings.append("Commande fournisseur restant a facturer.")

            order.mbs_control_state = "warning" if warnings else "ok"
            order.mbs_control_message = "\n".join(warnings) if warnings else "Aucune anomalie detectee."
