from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'

    def get_product_multiline_description_sale(self):
        name = self.name
        if self.description_sale:
            name += '\n' + self.description_sale

        return name

    def _compute_has_price_list(self):
        return True if len(self.seller_ids.mapped('name')) > 0 else False

