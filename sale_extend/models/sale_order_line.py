from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    initial_request = fields.Text(string='Demande initiale')
    ref_product = fields.Char(string="Ref article")
    brand = fields.Char(string='Catalogue/marque')
    availablity = fields.Char(string="Disponibilité")
    formula = fields.Float(string="Formule", digits=(12, 4), required=False, )
    is_pack = fields.Boolean(related="product_id.product_tmpl_id.is_pack")
    product_pack_ids = fields.One2many(comodel_name="sale.line.pack.products", inverse_name="sale_line_id", string="Pack")
    type_show_in_report = fields.Selection(string="Affichage imprimer", selection=[('1', 'Modèle à prix article'), ('2', 'Modèle à prix composants'), ])

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.ref_product = self.product_id.default_code
        self.brand = self.product_id.brand_id.name

    @api.onchange('free_qty_today', 'product_uom_qty')
    def _onchange_free_qty_today(self):
        if self.free_qty_today < self.product_uom_qty:
            self.availablity = 'Pas disponible'
        else:
            self.availablity = 'Disponible'

    def open_wizard_pack_product(self):
        return {
            'name': 'Article composants',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'views': [(self.env.ref('sale_extend.view_pack_sale_line_form').id, 'form')],
        }

    def calcul_price_pack(self):
        total_price = 0
        for rec in self:
            for pack in rec.product_pack_ids:
                total_price = total_price + pack.total_price
        self.price_unit = total_price
        
    @api.onchange('formula')
    def _onchange_formula(self):
        po_line = self.env['purchase.order.line'].search([('sale_line_id', '=', self.id)])
        if len(self.purchase_line_ids):
            formule = self.order_id.formule_ids.filtered(lambda f: f.partner_id.id == self.purchase_line_ids[0].order_id.partner_id.id)
            if len(formule):
                if formule[0].base == 'cost':
                    self.price_unit = self.formula * self.product_id.standard_price
                else:
                    self.price_unit = self.formula * self.purchase_line_ids[0].price_unit

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        pass

    def get_qty_report(self):
        if self.product_uom_qty % 1 == 0:
            return int(self.product_uom_qty)
        else:
            return self.product_uom_qty


class SaleOrderLinePackProduct(models.Model):
    _name = 'sale.line.pack.products'
    _rec_name = 'sale_line_id'
    _description = 'ligne de vente produit pack'

    sale_line_id = fields.Many2one(comodel_name="sale.order.line", string="ligne de vente")

    product_id = fields.Many2one('product.product', string='Product')
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    quantity = fields.Integer('Qté')
    price = fields.Float('Prix')
    formula = fields.Float(string="Formule", digits=(12, 4), required=False, )
    total_price = fields.Float('Prix Total', compute='compute_total_price')

    @api.depends('price', 'quantity')
    def compute_total_price(self):
        for rec in self:
            rec.total_price = rec.price * rec.quantity
            rec.sale_line_id.calcul_price_pack()


