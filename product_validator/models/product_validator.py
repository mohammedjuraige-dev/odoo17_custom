from odoo import models, fields, api


class ProductValidator(models.Model):
    _name = 'product.validator'
    _description = 'Product Validator'




    name = fields.Char(
        string='Product Name',
        required=False,
        help='Enter the product name'
    )

    quantity = fields.Float(
        string='Quantity',
        default=0,
        help='Enter the product quantity'
    )





    is_valid = fields.Boolean(
        string='Is Valid',
        compute='_compute_is_valid',
        store=True,
        readonly=True,
        help='Automatically checked when both name and quantity are valid'
    )

    @api.depends('name', 'quantity')
    def _compute_is_valid(self):
        """Compute is_valid based on name and quantity conditions"""
        for record in self:
            # Check if name is not empty/None and quantity > 0
            record.is_valid = bool(
                record.name and
                record.quantity > 0
            )

    @api.onchange('quantity')
    def _negative_checker(self):
        for record in self:
            if record.quantity < 0:
                record.quantity = abs(record.quantity)