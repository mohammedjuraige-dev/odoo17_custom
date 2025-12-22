from odoo import models, fields

class ProductValidator(models.Model):
    _inherit = 'product.validator'

    order_id = fields.Many2one('custom.order.taker', string="Order", ondelete='cascade')
