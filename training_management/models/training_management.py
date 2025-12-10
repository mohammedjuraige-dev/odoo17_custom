import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TrainingManagement(models.Model):
    _name = 'training.course'
    _description = 'Training management module used for managing Trainees'



    name=fields.Char(string="Course Name",required=True)
    instructor_id=fields.Many2one('res.partner',string="Instructor")
    trainee_ids=fields.Many2many('res.partner',string="Trainees")
    description=fields.Text("Training management module is used for managing trainees that enroll "
                            "on courses.")
    trainee_count=fields.Integer(string="Trainee count",store=True,compute='_count_trainee',default=1)



    @api.depends('trainee_ids')
    def _count_trainee(self):
        for record in self:
            record.trainee_count = len(record.trainee_ids)
            # Safe logging - check single record only
            if record.trainee_count > 10 and record.id:
                _logger.warning("'%s' (ID:%s) has %d trainees",
                                record.name, record.id, record.trainee_count)






    def action_view_trainees(self):  # ← Called on button click
        return {
            'name': 'Trainees',
            'type': 'ir.actions.act_window',  # Opens window
            'res_model': 'res.partner',
            'view_mode': 'tree,form',  # List + Form
            'domain': [('id', 'in', self.trainee_ids.ids)],
            'target': 'current',  # Opens in dialog
        }

    @api.constrains('name')
    def unique_name(self):
        for record in self:

           duplicate=self.env['training.course'].search(
               [
                   ('name','=',record.name),
                   ('id','=',record.id)
               ]
           )
           _logger.warning(f"{duplicate}")

           if duplicate:
                raise ValidationError("Name Already exists")