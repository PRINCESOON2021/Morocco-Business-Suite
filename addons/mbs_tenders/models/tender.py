from odoo import fields, models


class MbsTender(models.Model):
    _name = "mbs.tender"
    _description = "Appel d'offres / Consultation"
    _order = "submission_deadline desc, id desc"

    name = fields.Char(string="Intitule", required=True)
    reference = fields.Char(string="Reference AO", required=True, index=True)
    authority_id = fields.Many2one("res.partner", string="Maitre d'ouvrage", required=True)
    publication_date = fields.Date(string="Date de publication")
    submission_deadline = fields.Datetime(string="Date limite")
    source_url = fields.Char(string="Lien source")
    lot_number = fields.Char(string="Lot")
    estimated_amount = fields.Monetary(string="Montant estime")
    currency_id = fields.Many2one(
        "res.currency",
        string="Devise",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("preparing", "Preparation"),
            ("submitted", "Soumis"),
            ("awarded", "Attribue"),
            ("lost", "Non retenu"),
            ("cancelled", "Annule"),
        ],
        string="Statut",
        default="draft",
        required=True,
        index=True,
    )
    notes = fields.Html(string="Notes")
    contract_ids = fields.One2many("mbs.tender.contract", "tender_id", string="Marches")
    contract_count = fields.Integer(compute="_compute_contract_count", string="Nombre de marches")

    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.contract_ids)

    def action_mark_preparing(self):
        self.write({"state": "preparing"})

    def action_mark_submitted(self):
        self.write({"state": "submitted"})

    def action_mark_awarded(self):
        self.write({"state": "awarded"})

    def action_mark_lost(self):
        self.write({"state": "lost"})
