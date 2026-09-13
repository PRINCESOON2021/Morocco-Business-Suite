from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    mbs_ice = fields.Char(string="ICE", index=True)
    mbs_if = fields.Char(string="Identifiant fiscal", index=True)
    mbs_rc = fields.Char(string="Registre de commerce")
    mbs_cnss = fields.Char(string="N° CNSS")
    mbs_patente = fields.Char(string="Taxe professionnelle / Patente")
    mbs_fiscal_year_label = fields.Char(string="Exercice fiscal", default="2026")
