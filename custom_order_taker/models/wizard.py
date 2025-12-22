from odoo import models, fields, api
from odoo.exceptions import UserError


class OrderTakerWizard(models.TransientModel):
    _name = "custom.order.taker.wizard"
    _description = "Order Taker Wizard"

    customer_name = fields.Char()
    date = fields.Date()
    product_quantity = fields.Float()
    product = fields.Many2one("product.validator")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        active_id = self.env.context.get('active_id')
        if active_id:
            order = self.env['custom.order.taker'].browse(active_id)
            res.update({
                'customer_name': order.customer_name,
                'date': order.date,
                'product_quantity': order.product_quantity,
                'product': order.product.id if order.product else False
            })

        return res

    def confirm(self):
        self.ensure_one()

        active_id = self.env.context.get('active_id')
        if not active_id:
            raise UserError("No order found!")

        order = self.env['custom.order.taker'].browse(active_id)

        if not order.product:
            raise UserError("Please select a product first!")

        # Create order lines based on the quantity
        if self.product_quantity > 0:
            lines_to_create = []

            # Create multiple lines (one for each unit)
            for i in range(int(self.product_quantity)):
                lines_to_create.append({
                    'name': f"{order.product.name} - Unit {i+1}",
                    'order_id': order.id,
                    'quantity': 1.0,
                })

            # Create all lines at once
            if lines_to_create:
                self.env['product.validator'].create(lines_to_create)

            # Reset the product field after confirmation
            order.write({
                'product': False,
            })

        return {'type': 'ir.actions.act_window_close'}