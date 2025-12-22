import logging
from sys import exc_info

from odoo import fields, models, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TrainingRequest(models.Model):
    _name = 'training.request'
    _description = 'Training Request creation for employees'

    name = fields.Char(string='Program Name', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', string='Status')
    rejection_reason = fields.Text(string='Rejection Reason')
    actives = fields.Boolean(string='Active', default=False)

    @api.constrains('state', 'rejection_reason')
    def _rejection_reason_checker(self):
        for record in self:
            if record.state == 'rejected' and not record.rejection_reason:
                raise ValidationError('Rejection Reason is required.')

    def action_submit(self):
        for record in self:
            record.write({
                'state': 'submitted',
                'actives': True,
            })
            _logger.info(f"Training Request for {record.name} has been submitted by {record.employee_id.name}")

    def action_approve(self):
        for record in self:
            record.write({
                'state': 'approved',
            })
            _logger.info(f"Training Request for {record.name} has been Approved", exc_info)

    def action_reject(self):
        for record in self:
            record.write({
                'state': 'rejected',

            })
            _logger.info(f"Training Request for {record.name} has been Rejected")

    def action_draft(self):
        for record in self:
            record.write({
                'state': 'draft',
                'actives': False,
                'rejection_reason': False,

            })
