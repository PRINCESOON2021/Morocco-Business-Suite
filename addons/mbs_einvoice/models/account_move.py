import json

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    mbs_einvoice_state = fields.Selection(
        [
            ("not_applicable", "Non applicable"),
            ("draft", "Brouillon"),
            ("ready", "Pret a envoyer"),
            ("sent", "Envoye"),
            ("accepted", "Accepte"),
            ("rejected", "Rejete"),
        ],
        string="Etat e-facture",
        default="draft",
        copy=False,
        index=True,
    )
    mbs_einvoice_schema_version = fields.Char(string="Version schema", default="pending-official-spec", copy=False)
    mbs_einvoice_external_id = fields.Char(string="Identifiant externe", copy=False, index=True)
    mbs_einvoice_sent_at = fields.Datetime(string="Envoyee le", copy=False)
    mbs_einvoice_response = fields.Text(string="Reponse plateforme", copy=False)
    mbs_einvoice_payload = fields.Text(string="Payload structure", copy=False, readonly=True)

    def _mbs_build_einvoice_payload(self):
        self.ensure_one()
        lines = []
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            lines.append(
                {
                    "description": line.name,
                    "quantity": line.quantity,
                    "unit_price": line.price_unit,
                    "discount": line.discount,
                    "subtotal": line.price_subtotal,
                    "taxes": line.tax_ids.mapped("name"),
                }
            )
        return {
            "schema_version": self.mbs_einvoice_schema_version,
            "invoice_number": self.name,
            "invoice_date": str(self.invoice_date or ""),
            "move_type": self.move_type,
            "currency": self.currency_id.name,
            "seller": {
                "name": self.company_id.name,
                "ice": self.company_id.mbs_ice,
                "if": self.company_id.mbs_if,
                "rc": self.company_id.mbs_rc,
            },
            "buyer": {
                "name": self.partner_id.name,
                "ice": self.partner_id.mbs_ice,
                "if": self.partner_id.mbs_if,
                "rc": self.partner_id.mbs_rc,
            },
            "amounts": {
                "untaxed": self.amount_untaxed,
                "tax": self.amount_tax,
                "total": self.amount_total,
            },
            "lines": lines,
        }

    def action_mbs_prepare_einvoice(self):
        for move in self:
            payload = move._mbs_build_einvoice_payload()
            move.write(
                {
                    "mbs_einvoice_payload": json.dumps(payload, ensure_ascii=False, indent=2),
                    "mbs_einvoice_state": "ready",
                }
            )

    def action_mbs_mark_einvoice_sent(self):
        self.write({"mbs_einvoice_state": "sent", "mbs_einvoice_sent_at": fields.Datetime.now()})

    def action_mbs_mark_einvoice_accepted(self):
        self.write({"mbs_einvoice_state": "accepted"})

    def action_mbs_mark_einvoice_rejected(self):
        self.write({"mbs_einvoice_state": "rejected"})
