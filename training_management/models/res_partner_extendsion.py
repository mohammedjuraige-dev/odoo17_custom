from odoo import models,fields

class ResPartnerExtension(models.Model):
    _inherit = 'res.partner'

    course_ids=fields.Many2many('training.course')