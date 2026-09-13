from odoo import api, fields, models


class MbsTenderStatement(models.Model):
    _name = "mbs.tender.statement"
    _description = "Situation / Decompte de marche"
    _order = "statement_date desc, id desc"

    name = fields.Char(string="Reference situation", required=True)
    contract_id = fields.Many2one("mbs.tender.contract", string="Marche", required=True, ondelete="cascade")
    authority_id = fields.Many2one(related="contract_id.authority_id", store=True, readonly=True)
    statement_date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    period_from = fields.Date(string="Periode du")
    period_to = fields.Date(string="Au")
    currency_id = fields.Many2one(related="contract_id.currency_id", store=True, readonly=True)
    line_ids = fields.One2many("mbs.tender.statement.line", "statement_id", string="Attachements / Lignes")
    gross_amount = fields.Monetary(compute="_compute_amounts", store=True, string="Montant brut HT")
    retention_amount = fields.Monetary(compute="_compute_amounts", store=True, string="Retenue de garantie")
    advance_recovery = fields.Monetary(string="Recuperation avance")
    penalties = fields.Monetary(string="Penalites")
    net_amount = fields.Monetary(compute="_compute_amounts", store=True, string="Net HT avant TVA")
    invoice_id = fields.Many2one("account.move", string="Facture liee", domain="[(\"move_type\", \"=\", \"out_invoice\")]")
    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("validated", "Validee"),
            ("invoiced", "Facturee"),
            ("paid", "Payee"),
            ("cancelled", "Annulee"),
        ],
        default="draft",
        required=True,
        string="Statut",
    )
    notes = fields.Html(string="Notes")

    @api.depends(
        "line_ids.quantity_period",
        "line_ids.price_unit",
        "contract_id.retention_rate",
        "advance_recovery",
        "penalties",
    )
    def _compute_amounts(self):
        for statement in self:
            gross = sum(statement.line_ids.mapped("subtotal"))
            retention = gross * (statement.contract_id.retention_rate or 0.0) / 100.0
            statement.gross_amount = gross
            statement.retention_amount = retention
            statement.net_amount = gross - retention - statement.advance_recovery - statement.penalties

    def action_validate(self):
        self.write({"state": "validated"})

    def action_mark_invoiced(self):
        self.write({"state": "invoiced"})

    def action_mark_paid(self):
        self.write({"state": "paid"})


class MbsTenderStatementLine(models.Model):
    _name = "mbs.tender.statement.line"
    _description = "Ligne situation / Attachement"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    statement_id = fields.Many2one("mbs.tender.statement", required=True, ondelete="cascade")
    contract_line_id = fields.Many2one("mbs.tender.contract.line", string="Poste marche", required=True)
    name = fields.Char(related="contract_line_id.name", store=True, readonly=True)
    quantity_period = fields.Float(string="Quantite de la periode", default=0.0, required=True)
    quantity_contract = fields.Float(related="contract_line_id.quantity", readonly=True)
    price_unit = fields.Monetary(related="contract_line_id.price_unit", store=True, readonly=True)
    currency_id = fields.Many2one(related="statement_id.currency_id", store=True, readonly=True)
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True, string="Montant HT")

    @api.depends("quantity_period", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity_period * line.price_unit
