from odoo import fields, models


class TrainingTopic(models.Model):
    _name = 'training.topic'
    _description = 'Broadtech training'

    name = fields.Char(string='Name',required=True)
    description = fields.Char(string='Description')
    difficulty = fields.Selection([
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ],string='Difficulty')
    active = fields.Boolean(default=True,string='Active')



