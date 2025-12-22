from odoo import models, fields, api

class ProductValidator(models.Model):
    _inherit = 'product.validator'

    def action_delete_line(self):
        for record in self:
            record.unlink()
        return {'type': 'ir.actions.client', 'tag': 'reload'}
