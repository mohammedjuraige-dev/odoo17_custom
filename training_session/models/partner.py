from odoo import fields, models

class MyPartnerExtension(models.Model):

    _inherit = 'res.partner'

    is_instructor = fields.Boolean(string="Is Instructor")
    is_trainee = fields.Boolean(string="Is Trainee")

