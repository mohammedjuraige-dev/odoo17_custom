from odoo import fields, models


class HrAttendanceExtend(models.Model):
    _inherit = 'hr.attendance'

    employee_attendance_id = fields.Many2one('attendance.summary')
    late_minutes = fields.Float(string='Late Minutes')

