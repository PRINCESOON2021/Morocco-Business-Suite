from odoo import api, fields, models


class MbsBusinessDashboard(models.TransientModel):
    _name = "mbs.business.dashboard"
    _description = "Situation de mon entreprise"

    company_id = fields.Many2one(
        "res.company",
        string="Societe",
        required=True,
        default=lambda self: self.env.company,
    )
    date_from = fields.Date(
        string="Du",
        default=lambda self: fields.Date.context_today(self).replace(month=1, day=1),
    )
    date_to = fields.Date(string="Au", default=fields.Date.context_today)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)

    invoiced_revenue = fields.Monetary(string="CA facture HT", compute="_compute_metrics")
    open_receivables = fields.Monetary(string="Creances ouvertes", compute="_compute_metrics")
    open_payables = fields.Monetary(string="Dettes fournisseurs", compute="_compute_metrics")
    invoice_warning_count = fields.Integer(string="Factures a verifier", compute="_compute_metrics")
    sale_warning_count = fields.Integer(string="Ventes a verifier", compute="_compute_metrics")
    purchase_warning_count = fields.Integer(string="Achats a verifier", compute="_compute_metrics")
    overdue_customer_count = fields.Integer(string="Factures clients en retard", compute="_compute_metrics")

    @api.depends("company_id", "date_from", "date_to")
    def _compute_metrics(self):
        AccountMove = self.env["account.move"]
        AccountMoveLine = self.env["account.move.line"]
        SaleOrder = self.env["sale.order"]
        PurchaseOrder = self.env["purchase.order"]
        today = fields.Date.context_today(self)

        for dashboard in self:
            company = dashboard.company_id
            invoice_domain = [
                ("company_id", "=", company.id),
                ("state", "=", "posted"),
                ("move_type", "in", ("out_invoice", "out_refund")),
            ]
            if dashboard.date_from:
                invoice_domain.append(("invoice_date", ">=", dashboard.date_from))
            if dashboard.date_to:
                invoice_domain.append(("invoice_date", "<=", dashboard.date_to))

            invoices = AccountMove.search(invoice_domain)
            dashboard.invoiced_revenue = sum(invoices.mapped("amount_untaxed_signed"))

            receivable_lines = AccountMoveLine.search([
                ("company_id", "=", company.id),
                ("parent_state", "=", "posted"),
                ("account_id.account_type", "=", "asset_receivable"),
                ("reconciled", "=", False),
            ])
            payable_lines = AccountMoveLine.search([
                ("company_id", "=", company.id),
                ("parent_state", "=", "posted"),
                ("account_id.account_type", "=", "liability_payable"),
                ("reconciled", "=", False),
            ])
            dashboard.open_receivables = sum(receivable_lines.mapped("amount_residual"))
            dashboard.open_payables = abs(sum(payable_lines.mapped("amount_residual")))

            dashboard.invoice_warning_count = AccountMove.search_count([
                ("company_id", "=", company.id),
                ("move_type", "in", ("out_invoice", "out_refund", "in_invoice", "in_refund")),
                ("mbs_control_state", "=", "warning"),
            ])
            dashboard.sale_warning_count = SaleOrder.search_count([
                ("company_id", "=", company.id),
                ("mbs_control_state", "=", "warning"),
            ])
            dashboard.purchase_warning_count = PurchaseOrder.search_count([
                ("company_id", "=", company.id),
                ("mbs_control_state", "=", "warning"),
            ])
            dashboard.overdue_customer_count = AccountMove.search_count([
                ("company_id", "=", company.id),
                ("state", "=", "posted"),
                ("move_type", "=", "out_invoice"),
                ("payment_state", "not in", ("paid", "reversed")),
                ("invoice_date_due", "<", today),
            ])

    def action_refresh(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Situation de mon entreprise",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_overdue_customers(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Factures clients en retard",
            "res_model": "account.move",
            "view_mode": "list,form,pivot,graph",
            "domain": [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "posted"),
                ("move_type", "=", "out_invoice"),
                ("payment_state", "not in", ("paid", "reversed")),
                ("invoice_date_due", "<", fields.Date.context_today(self)),
            ],
        }
