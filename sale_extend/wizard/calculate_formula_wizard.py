from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ClaculateFormulaWizard(models.TransientModel):
    _name = 'calculate.formula.wizard'

    type_calcule = fields.Selection(string="Calcul", selection=[('formula', 'Formule')], default='formula')
    base = fields.Selection(string="Basée sur", selection=[('cost', 'Coût'), ('supplier_price', 'Prix fournisseur')], default='supplier_price')
    taux_change = fields.Float(string="Taux de change", digits=(12, 3))
    droits_douanes = fields.Float(string="Droits de douanes", digits=(12, 3))
    transportation_costs = fields.Float(string="Frais de transport", digits=(12, 3))
    marge = fields.Float(string="Marge (%)")

    order_id = fields.Many2one(comodel_name="sale.order")
    partner_id = fields.Many2one(comodel_name="res.partner", string='Fournisseur')
    partner_ids = fields.Many2many(comodel_name="res.partner", string="fournisseurs")

    


    def calculate_formula(self):
        # Prix fournisseur ou coût * Taux de change * Droits de douanes * Frais de transport
        # self.order_id.taux_change = self.taux_change
        # self.order_id.droits_douanes = self.droits_douanes
        # self.order_id.transportation_costs = self.transportation_costs
        #
        # for line in self.order_id.order_line:
        #     po_line = self.env['purchase.order.line'].search([('sale_line_id', '=', line.id)])
        #     line.formula = (self.taux_change if self.taux_change else 1) * (self.droits_douanes if self.droits_douanes else 1) * (self.transportation_costs if self.transportation_costs else 1)
        #
        #     if self.base == 'supplier_price':
        #         line.price_unit = po_line.price_unit * line.formula
        #
        #     elif self.base == 'cost':
        #         line.price_unit = line.product_id.standard_price * line.formula

        if self.order_id and len(self.order_id._get_purchase_orders()):
            formule = self.order_id.formule_ids.filtered(lambda f: f.partner_id.id == self.partner_id.id)
            if len(formule):
                # update values if formule exist
                formule.taux_change = self.taux_change
                formule.droits_douanes = self.droits_douanes
                formule.transportation_costs = self.transportation_costs
                formule.marge = self.marge
                formule.base = self.base
            else:
                # create new formules
                formule = self.env['sale.order.formule'].create({
                    'name': self.order_id.id,
                    'partner_id': self.partner_id.id,
                    'taux_change': self.taux_change,
                    'droits_douanes': self.droits_douanes,
                    'transportation_costs': self.transportation_costs,
                    'marge': self.marge,
                    'base': self.base,
                })

            po = self.order_id._get_purchase_orders().filtered(lambda po: po.partner_id.id == self.partner_id.id)
            for p in po:
                for line in p.order_line:
                    line.sale_line_id.formula = ((self.taux_change if self.taux_change else 1) *
                                                 (self.droits_douanes if self.droits_douanes else 1) *
                                                 (self.transportation_costs if self.transportation_costs else 1)) / (1 - self.marge/100)

                    if self.base == 'supplier_price':
                        line.sale_line_id.price_unit = line.price_unit * (line.sale_line_id.formula)
                    elif self.base == 'cost':
                        line.price_unit = line.product_id.standard_price * (line.sale_line_id.formula)

        else:
            raise ValidationError("Il n'y a pas de bon de commande achat")

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        formule = self.order_id.formule_ids.filtered(lambda f: f.partner_id.id == self.partner_id.id)
        if len(formule):
            self.taux_change = formule[0].taux_change
            self.droits_douanes = formule[0].droits_douanes
            self.transportation_costs = formule[0].transportation_costs
            self.marge = formule[0].marge
            self.base = formule[0].base
        
