from odoo import api, fields, models


class MbsTenderContract(models.Model):
    _name = "mbs.tender.contract"
    _description = "Marche public / Contrat"
    _order = "date_start desc, id desc"

    name = fields.Char(string="Objet du marche", required=True)
    reference = fields.Char(string="Reference marche", required=True, index=True)
    tender_id = fields.Many2one("mbs.tender", string="Appel d'offres", ondelete="set null")
    authority_id = fields.Many2one("res.partner", string="Maitre d'ouvrage", required=True)
    date_start = fields.Date(string="Date de debut")
    date_end = fields.Date(string="Date de fin")
    currency_id = fields.Many2one(
        "res.currency",
        string="Devise",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    line_ids = fields.One2many("mbs.tender.contract.line", "contract_id", string="Bordereau des prix")
    amount_untaxed = fields.Monetary(compute="_compute_amounts", store=True, string="Montant HT")
    retention_rate = fields.Float(string="Retenue de garantie (%)", default=0.0)
    advance_amount = fields.Monetary(string="Avance recue")
    penalty_rate = fields.Float(string="Penalite contractuelle (%)", default=0.0)
    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("running", "En execution"),
            ("provisional_acceptance", "Reception provisoire"),
            ("final_acceptance", "Reception definitive"),
            ("closed", "Cloture"),
            ("cancelled", "Annule"),
        ],
        default="draft",
        required=True,
        string="Statut",
    )
    statement_ids = fields.One2many("mbs.tender.statement", "contract_id", string="Situations")

    @api.depends("line_ids.quantity", "line_ids.price_unit")
    def _compute_amounts(self):
        for contract in self:
            contract.amount_untaxed = sum(contract.line_ids.mapped("subtotal"))


class MbsTenderContractLine(models.Model):
    _name = "mbs.tender.contract.line"
    _description = "Ligne bordereau des prix"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    contract_id = fields.Many2one("mbs.tender.contract", required=True, ondelete="cascade")
    code = fields.Char(string="Code")
    name = fields.Char(string="Designation", required=True)
    product_id = fields.Many2one("product.product", string="Produit / Service")
    quantity = fields.Float(string="Quantite contractuelle", default=1.0, required=True)
    uom_id = fields.Many2one("uom.uom", string="Unite")
    price_unit = fields.Monetary(string="Prix unitaire HT", required=True)
    currency_id = fields.Many2one(related="contract_id.currency_id", store=True, readonly=True)
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True, string="Total HT")

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit
