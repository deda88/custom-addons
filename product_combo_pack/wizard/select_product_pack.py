# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Afras Habis (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SelectPack(models.TransientModel):
    _name = 'select.product.pack'
    _rec_name = 'product_id'
    _description = 'Add product pack to sale order'

    product_id = fields.Many2one('product.product', string = 'Select Pack', domain = [('is_pack', '=', True)],
                                 required = True)
    quantity = fields.Integer('Quantity', default = 1, required = True)

    def add_pack_order(self):
        active_id = self._context.get('active_id')
        if active_id:
            sale_id = self.env['sale.order'].browse(active_id)
            name = self.product_id.display_name
            if self.product_id.description_sale:
                name += '\n' + self.product_id.description_sale
            sale_order_line = self.env['sale.order.line'].create({
                'product_id': self.product_id.id,
                'price_unit': self.product_id.lst_price,
                'product_uom': self.product_id.uom_id.id,
                'product_uom_qty': self.quantity,
                'order_id': sale_id.id,
                'name': name,
                'type_show_in_report': '1',
                'tax_id' : self.product_id.taxes_id.ids
            })
            sale_order_line._onchange_product_id()
            sale_order_line.name = self.product_id.get_product_multiline_description_sale()
            so_line_price = 0
            for composant in self.product_id.product_tmpl_id.pack_products_ids:
                so_line_price = so_line_price + (composant.price * composant.quantity)
                self.env['sale.line.pack.products'].create({
                    'product_id': composant.product_id.id,
                    'product_tmpl_id': composant.product_tmpl_id.id,
                    'quantity': composant.quantity * self.quantity,
                    'price': composant.price,
                    'sale_line_id': sale_order_line.id,
                })
            sale_order_line.price_unit = so_line_price

    @api.constrains('quantity')
    def _check_positive_qty(self):
        if any([ml.quantity < 0 for ml in self]):
            raise ValidationError(_('You can not enter negative quantities.'))
