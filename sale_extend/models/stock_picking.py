# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_show_cataloge = fields.Boolean(string="Afficher catalogue dans l'imprimer", default=True)

    @api.model
    def create(self, values):
        res = super(StockPicking, self).create(values)
        if res.picking_type_id and res.picking_type_id.id == self.env.ref('stock.picking_type_out').id:
            res.name = "Brouillon"+str(res.id)
        return res

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.state == "done":
            self.name = self.env['ir.sequence'].next_by_code('seq.bl') or _('New')
        return res