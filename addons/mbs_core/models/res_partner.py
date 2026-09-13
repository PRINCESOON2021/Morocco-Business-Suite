from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    mbs_ice = fields.Char(string="ICE", index=True)
    mbs_if = fields.Char(string="Identifiant fiscal", index=True)
    mbs_rc = fields.Char(string="Registre de commerce")
    mbs_cnss = fields.Char(string="N° CNSS")
