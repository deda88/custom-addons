from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_show_cataloge = fields.Boolean(string="Afficher catalogue dans l'imprimer", default=True)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for po in self:
            po.name = self.env['ir.sequence'].next_by_code('seq.bc') or po.name
        return res
