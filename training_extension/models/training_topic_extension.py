from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class TrainingExtension(models.Model):
    _inherit = 'training.topic'
    _description = 'Training Topic Extension'

    estimated_hours = fields.Float(string="Estimated Hours")
    is_advanced = fields.Boolean(string="Is Advanced",store=True, compute="_compute_is_advanced")

    @api.depends('estimated_hours','difficulty')
    def _compute_is_advanced(self):
        for record in self:
            if record.estimated_hours > 10 or record.difficulty == 'hard':
                record.is_advanced = True
            else:
                record.is_advanced = False

    @api.constrains('estimated_hours')
    def _check_estimated_hours(self):
        for record in self:
            if record.estimated_hours < 0:
                raise ValidationError("Estimated Hours cannot be negative!")

    @api.model
    def create(self, vals):
        if vals.get('name'):
            _logger.warning(
                f"Name: {vals.get('name')} ,"
                f"difficulty: {vals.get('difficulty')} ,"
                f"estimated_hours: {vals.get('estimated_hours')}"
            )

        return super(TrainingExtension, self).create(vals)