from odoo import _, fields, models
from odoo.exceptions import UserError


class MbsAccountingReportWizard(models.TransientModel):
    _name = "mbs.accounting.report.wizard"
    _description = "Assistant rapports comptables MBS"

    report_type = fields.Selection(
        [
            ("trial_balance", "Balance generale"),
            ("general_ledger", "Grand livre"),
            ("customer_ledger", "Balance clients"),
            ("supplier_ledger", "Balance fournisseurs"),
            ("receivables", "Creances clients"),
            ("payables", "Dettes fournisseurs"),
            ("vat", "TVA"),
        ],
        required=True,
        default="trial_balance",
        string="Rapport",
    )
    date_from = fields.Date(string="Du")
    date_to = fields.Date(string="Au", default=fields.Date.context_today)
    journal_ids = fields.Many2many("account.journal", string="Journaux")
    partner_ids = fields.Many2many("res.partner", string="Tiers")
    only_posted = fields.Boolean(string="Ecritures validees uniquement", default=True)

    def _base_domain(self):
        self.ensure_one()
        domain = [("display_type", "=", False)]
        if self.date_from:
            domain.append(("date", ">=", self.date_from))
        if self.date_to:
            domain.append(("date", "<=", self.date_to))
        if self.only_posted:
            domain.append(("parent_state", "=", "posted"))
        if self.journal_ids:
            domain.append(("journal_id", "in", self.journal_ids.ids))
        if self.partner_ids:
            domain.append(("partner_id", "in", self.partner_ids.ids))
        return domain

    def action_open_report(self):
        self.ensure_one()
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_("La date de debut doit etre anterieure a la date de fin."))

        domain = self._base_domain()
        title = dict(self._fields["report_type"].selection).get(self.report_type)

        if self.report_type in ("trial_balance", "general_ledger"):
            domain.append(("account_id.deprecated", "=", False))
        elif self.report_type == "customer_ledger":
            domain.extend([
                ("account_id.account_type", "=", "asset_receivable"),
                ("partner_id", "!=", False),
            ])
        elif self.report_type == "supplier_ledger":
            domain.extend([
                ("account_id.account_type", "=", "liability_payable"),
                ("partner_id", "!=", False),
            ])
        elif self.report_type == "receivables":
            domain.extend([
                ("account_id.account_type", "=", "asset_receivable"),
                ("reconciled", "=", False),
            ])
        elif self.report_type == "payables":
            domain.extend([
                ("account_id.account_type", "=", "liability_payable"),
                ("reconciled", "=", False),
            ])
        elif self.report_type == "vat":
            domain.append(("tax_line_id", "!=", False))

        return {
            "type": "ir.actions.act_window",
            "name": title,
            "res_model": "account.move.line",
            "view_mode": "list,pivot,graph",
            "domain": domain,
            "context": {
                "search_default_group_by_account": 1
                if self.report_type in ("trial_balance", "general_ledger")
                else 0,
                "search_default_group_by_partner": 1
                if self.report_type in ("customer_ledger", "supplier_ledger", "receivables", "payables")
                else 0,
            },
        }
