from odoo import api, fields, models


class SaleOrderFormule(models.Model):
    _name = 'sale.order.formule'
    _rec_name = 'name'

    name = fields.Many2one(comodel_name="sale.order", string="Vente")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Fournisseur")
    taux_change = fields.Float(string="Taux de change", default=1)
    droits_douanes = fields.Float(string="Droits de douanes", default=1)
    transportation_costs = fields.Float(string="Frais de transport", default=1)
    marge = fields.Float(string="Marge", default=1)
    base = fields.Selection(string="Basée sur", selection=[('cost', 'Coût'), ('supplier_price', 'Prix fournisseur')], default='supplier_price')
