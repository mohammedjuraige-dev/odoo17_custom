from odoo import models, fields, api
from odoo.fields import Many2many, Many2one, One2many
import logging

_logger=logging.getLogger(__name__)
class TrainingSessionLine(models.Model):
    _name = 'training.session.line'
    _description = "Track session Attendees"

    session_id= fields.Many2one('training.session',string="Session")
    attendee_id= Many2one('res.partner',string="Attendee name")
    attended = fields.Boolean(default=False,string="Attended session?")
    notes = fields.Text("Notes")



