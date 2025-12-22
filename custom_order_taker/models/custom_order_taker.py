from odoo import models, fields, api

class OrderTaker(models.Model):
    _name = 'custom.order.taker'
    _description = 'Custom Order Taker'
    _inherit = ['mail.thread','mail.activity.mixin']

    customer_name = fields.Char(string="Customer name",required=True)
    date = fields.Date(string="Order date",required=True)
    product = fields.Many2one('product.validator', string="Product",store=True,tracking=True)
    product_quantity = fields.Float(string="Available Quantity", tracking=True, compute='quantity_taker', store=True)
    total_items = fields.Integer(string="Total Items", compute='record_delete_count')
    order_line_id = fields.One2many(
        "product.validator",
        "order_id",

    )

    @api.depends('product')
    def quantity_taker(self):
        for record in self:
            if record.product:
                record.product_quantity = record.product.quantity
            else:
                record.product_quantity = 0.0

    @api.depends('order_line_id')
    def record_delete_count(self):
        for record in self:
            record.total_items = len(record.order_line_id)

































