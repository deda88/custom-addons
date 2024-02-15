# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class createpurchaseorder(models.TransientModel):
    _name = 'create.purchaseorder'
    _description = "Create Purchase Order"

    new_order_line_ids = fields.One2many('getsale.orderdata', 'new_order_line_id', string="Order Line")
    partner_id = fields.Many2one('res.partner', string='Vendor')
    date_order = fields.Datetime(string='Order Date', required=True, copy=False, default=fields.Datetime.now)
    order_line_with_supplier = fields.Many2many(comodel_name="sale.order.line")
    num_new_order_line_ids = fields.Integer(compute="cumpute_num_lines")
    num_order_line_with_supplier = fields.Integer(compute="cumpute_num_lines")

    @api.depends('new_order_line_ids', 'order_line_with_supplier')
    def cumpute_num_lines(self):
        self.num_new_order_line_ids = len(self.new_order_line_ids)
        self.num_order_line_with_supplier = len(self.order_line_with_supplier)

    @api.model
    def default_get(self, default_fields):
        res = super(createpurchaseorder, self).default_get(default_fields)
        data = self.env['sale.order'].browse(self._context.get('active_ids', []))
        update = []
        update_with_supplier = []
        for record in data.order_line:
            po_line = record.env['purchase.order.line'].search([('sale_line_id', '=', record.id)])
            if len(po_line) == 0:
                if not record.product_id._compute_has_price_list():
                    update.append((0, 0, {
                        'product_id': record.product_id.id,
                        'product_uom': record.product_uom.id,
                        'order_id': record.order_id.id,
                        'name': record.name,
                        'product_qty': record.product_uom_qty,
                        'price_unit': record.price_unit,
                        'product_subtotal': record.price_subtotal,
                        'sale_line_id': record.id,
                    }))
                else:
                    update_with_supplier.append(record.id)
        if len(update)==0 and len(update_with_supplier)==0:
            raise ValidationError("Vous avez déjà créé des bons de commande d'achat pour les articles de ce devis")
        res.update({'new_order_line_ids': update, 'order_line_with_supplier': [(6, 0, update_with_supplier)]})
        return res

    def action_create_purchase_order(self):
        so = self.env['sale.order'].browse(self._context.get('active_id'))
        po = self.create_po_without_supplier()
        self.create_po_with_supplier()

    def create_po_without_supplier(self):
        self.ensure_one()
        value = []
        purchase_order = self.env['purchase.order']
        so = self.env['sale.order'].browse(self._context.get('active_id'))
        for data in self.new_order_line_ids:
            value.append([0, 0, {
                'product_id': data.product_id.id,
                'name': data.name,
                'product_qty': data.product_qty,
                'sale_line_id': data.sale_line_id.id,
            }])
        if len(self.new_order_line_ids):
            purchase_order = self.env['purchase.order'].create({
                                'partner_id': self.partner_id.id,
                                'date_order': str(self.date_order),
                                'order_line': value,
                                'origin': so.name,
                                'partner_ref': so.name
                            })
        return purchase_order

    def create_po_with_supplier(self):
        so = self.env['sale.order'].browse(self._context.get('active_id'))
        all_po = {}

        for line_with_supplier in self.order_line_with_supplier:
            supplier = line_with_supplier.product_id.seller_ids.mapped('name')[0]
            if supplier not in all_po:
                # Si le bon de commande n'existe pas pour ce fournisseur, créez-en un.
                purchase_order = self.env['purchase.order'].create({
                    'partner_id': supplier.id,
                    'date_order': str(self.date_order),
                    'origin': so.name,
                    'partner_ref': line_with_supplier.order_id.name
                })
                all_po[supplier] = purchase_order
            else:
                purchase_order = all_po[supplier]

            line = {
                'product_id': line_with_supplier.product_id.id,
                'name': line_with_supplier.name,
                'product_qty': line_with_supplier.product_qty,
                'order_id': purchase_order.id,
                'sale_line_id': line_with_supplier.id,
            }
            self.env['purchase.order.line'].create(line)


        
    # def create_po_with_supplier(self, po_without_supplier):
    #     all_po = [po_without_supplier]

    #     for line_with_supplier in self.order_line_with_supplier:
    #         po_exist = False
    #         if len(line_with_supplier.product_id.seller_ids.mapped('name')):
    #             for po in all_po:
    #                 if line_with_supplier.product_id.seller_ids.mapped('name')[0] == po.partner_id:
    #                     po_exist = True
    #                     self.env['sale.order.line'].create({
    #                                                     'product_id': line_with_supplier.product_id.id,
    #                                                     'name': line_with_supplier.name,
    #                                                     'product_qty': line_with_supplier.product_qty,
    #                                                     'order_id': po.id
    #                                                 })

    #             if not po_exist:
    #               new_po = self.env['purchase.order'].create({
    #             'partner_id': line_with_supplier.product_id.seller_ids.mapped('name')[0].id,
    #             'date_order': self.date_order,
    #             'origin': line_with_supplier.order_id.name,
    #             'partner_ref': line_with_supplier.order_id.name
    #         })
    #         all_po.append(new_po)
    #         line = {
    #             'product_id': line_with_supplier.product_id.id,
    #             'name': line_with_supplier.name,
    #             'product_qty': line_with_supplier.product_qty,
    #             'order_id': new_po.id,
    #             'sale_line_id': line_with_supplier.id,
    #         }
    #         self.env['purchase.order.line'].create(line)


class Getsaleorderdata(models.TransientModel):
    _name = 'getsale.orderdata'
    _description = "Get Sale Order Data"

    new_order_line_id = fields.Many2one('create.purchaseorder')

    product_id = fields.Many2one('product.product', string="Product", required=True)
    name = fields.Char(string="Description")
    product_qty = fields.Float(string='Quantity', required=True)
    date_planned = fields.Datetime(string='Scheduled Date', default=datetime.today())
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    product_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
    sale_line_id = fields.Many2one(comodel_name="sale.order.line")

    @api.depends('product_qty', 'price_unit')
    def _compute_total(self):
        for record in self:
            record.product_subtotal = record.product_qty * record.price_unit

