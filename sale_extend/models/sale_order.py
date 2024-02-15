from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ref_request_customer = fields.Char(string="Réf demande client", required=False)
    delivery_locations = fields.Char(string="Lieux de livraison", required=False)
    object = fields.Text(string="Objet")
    other_mentions = fields.Text(string="Autres mentions")
    # taux_change = fields.Float(string="Taux de change", default=1)
    # droits_douanes = fields.Float(string="Droits de douanes", default=1)
    # transportation_costs = fields.Float(string="Frais de transport", default=1)
    is_show_cataloge = fields.Boolean(string="Afficher catalogue dans l'imprimer")
    formule_ids = fields.One2many(comodel_name="sale.order.formule", inverse_name="name", string="Formules")

    def check_availability(self):
        for line in self.order_line:
            if line.free_qty_today < line.product_uom_qty:
                line.availablity = 'Pas disponible'
            else:
                line.availablity = 'Disponible'

    def open_wizard_calculate_formula(self):
        return {
            'name': 'Calcul de formule',
            'type': 'ir.actions.act_window',
            'res_model': 'calculate.formula.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_partner_ids': [(6, 0, self._get_purchase_orders().mapped('partner_id').ids if len(self._get_purchase_orders().mapped('partner_id')) else [])],
                # 'default_taux_change': self.taux_change,
                # 'default_droits_douanes': self.droits_douanes,
                # 'default_transportation_costs': self.transportation_costs
            },
        }

