import logging
from datetime import time

import pytz

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AttendanceSummary(models.Model):
    _name = 'attendance.summary'
    _inherit = 'mail.thread'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True, tracking=True)
    date_from = fields.Date(string='Date from', required=True, tracking=True)
    date_to = fields.Date(string='Date to', required=True, tracking=True)
    total_attendance_days = fields.Integer(string='Total Attendance Days')
    late_days = fields.Float(string='Total Late days', default=0.0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], default='draft', tracking=True)

    threshold_time = fields.Char(string='scheduled check-in time')

    attendance_ids = fields.Many2many('hr.attendance', store=True)

    def action_confirm(self):
        try:
            self.state = 'confirmed'
            for allocation in self:
                """This is function is used for calculating total 
                attendance days, late days, and late minutes"""
                if not allocation.date_from or not allocation.date_to or not allocation.employee_id:
                    allocation.late_days = 0
                    allocation.threshold_time = ""
                    allocation.total_attendance_days = 0
                    allocation.attendance_ids = [(5, 0, 0)]
                    _logger.warning(f"record skipped: {self}")
                    continue
                """checks date_from,date_to,employee given or not. If any of condition
                 fails late_days,threshold_time,total_attendance_days,
                and the one2many field that is connected to hr.attendance
                 unlinks any record which was previously linked"""

                attendance_domain = [
                    ('check_in', '>=', allocation.date_from),
                    ('check_in', '<=', allocation.date_to),
                    ('employee_id', '=', allocation.employee_id.id),
                ]
                """We make a list of the domain details and that is used to
                 search for the records that satisfy the domain below"""

                attendances = allocation.env['hr.attendance'].search(attendance_domain)
                """we assign the recordset from search on model hr_attendance
                 that satisfy domains to a list called attendance"""
                if not attendances:
                    allocation.message_post(
                        body="Warning: No attendance found for employee",
                        message_type='comment',
                        subtype_xmlid='mail.mt_note',
                    )

                allocation.total_attendance_days = len(attendances)
                """The total attendance days is gathered from the number of records """
                # Link the found attendances to this summary
                allocation.attendance_ids = [(6, 0, attendances.ids)]
                """This function mainly does the a part of that _count_days does but
                it unlinks all existing records and links the new records found to 
                our model using the one2many field.
                The structure of an Odoo command is always a tuple of three values:
                 (command_code, virtual_id, list_of_ids).
                 other Set commands:
                 Command,Action,Description
                "(0, 0, {values})",Create,Creates a new record and links it immediately.
                "(4, id, 0)",Link,Adds one specific existing record to the list (doesn't remove others).
                "(3, id, 0)",Unlink,Removes the link to a specific record (but doesn't delete the record).
                "(5, 0, 0)",Clear,Removes all links (empties the list).
                "(6,0,id)", unlinks existing records,keep same tuple format and link new ids.
                We use many2many field so that multiple records can be with multiple attendance summary.
                """

                morning_attendance = allocation.env['resource.calendar.attendance'].search([
                    ('day_period', '=', 'morning')
                ], limit=1)
                """To find the scheduled check in time we searched the 
                model with domain day_period equal to morning which gives
                us records with day_period as morning time and we set a
                 limit=1 so that we get only a single record form the search.
                 But this is only possible for working schedules that have a
                 fixed working time like a 9am to 5pm for everyday.This method will
                  not be work if the company has multiple different working schedule"""

                if not morning_attendance:
                    allocation.late_days = 0
                    allocation.threshold_time = ""
                    continue
                """The searched list is then checked if empty or not. If empty then late 
                days is given zero and threshold time is also nil ,
                since it is a character"""

                threshold_hour = morning_attendance.hour_from
                """Here we took the value hour_from which is the field that
                 stores the work_from time in the morning so this is the 
                scheduled check in time. But threshold hour is used to store
                 the time now but is now a float hour field and cannot be used
                to compare with time object"""

                threshold_time = time(
                    hour=int(threshold_hour),
                    minute=int((threshold_hour % 1) * 60)
                )
                """We are converting the float hour variable to a time object 
                by using a char variable we defined earlier. hour is the getting the
                time as int before the decimal. eg: 8 from 8.29. Next minute is 
                also part of time function so in order to get the points after 
                decimal the float hour is moduled by 1 then converted to 
                minutes multiplied by 60"""

                allocation.threshold_time = threshold_time.strftime("%H:%M")
                """strftime  is used to format a date and time object
                 into a readable string based on specific format codes."""

                # Define timezones
                utc_tz = pytz.UTC
                """Here we localize the utc time by assigning it to a variable"""
                ist_tz = pytz.timezone('Asia/Kolkata')
                """we store our timezone(india) in another variable"""

                late_count = 0
                """initialize a variable with value zero 
                to be able to catch no of late days during computation"""

                for attendance in attendances:
                    """We are now passing through each record present in the attendance recordset"""
                    if attendance.check_in:
                        """so for each record we are checking if the check_in field is not empty"""
                        check_in_utc = attendance.check_in
                        """we are storing the checkin value to a variable, that is the utc time"""
                        if check_in_utc.tzinfo is None:
                            """we are checking if the variable is timezone aware is or not
                            if it satisy that means variable has no timezone set."""
                            check_in_utc = utc_tz.localize(check_in_utc)
                            """so we have made the variable timezone aware that is it now 
                            shows that it is a UTC time."""

                        check_in_ist = check_in_utc.astimezone(ist_tz)
                        """now that it is utc time that odoo uses we can now
                        convert it into india timezone using the astimezone function.
                        It is used to translate one timezone to another"""

                        check_in_time_ist = check_in_ist.time()
                        """now we have the india time stored into a variable but it
                        still is time aware that it will have a +5:30 or something like that
                        to show which timezone it is , so we convert it into normal time and
                        we remove the date as well as checkin is a datetime field"""

                        # Compare with threshold time object
                        if check_in_time_ist > threshold_time:
                            late_count += 1
                            """Now we compare the checkin time in indian time zone
                            with the morning work schedule time . If checkin time is
                            bigger that is the employee arrived late then the count
                            variable is incremented by one. so everytime the condition satisfy
                            the count is incremented and we get the late_days field value"""

                            check_in_minutes = check_in_time_ist.hour * 60 + check_in_time_ist.minute + check_in_time_ist.second / 60
                            """we are assigning a variable by converting the checkin time 
                            to minutes for this attendance record.Now this is a float variable"""
                            threshold_minutes = threshold_time.hour * 60 + threshold_time.minute
                            """we are assigning a variable by converting the threshold time or
                            scheduled morning checkin time into minutes.Now this is float variable"""
                            late_minutes_for_this_record = check_in_minutes - threshold_minutes
                            """These above line is used to calculate by how many minutes the 
                            employee was late in each checkin for a record."""

                            if hasattr(attendance, 'late_minutes'):
                                attendance.late_minutes = late_minutes_for_this_record / 60.0

                allocation.late_days = late_count
                """we are not assigning the late count value to our late_days variable present in our model"""
        except Exception as e:
            _logger.error("An error occurred %s", e)
            """we have given an exception for the initial loop in case of any error occur so we can identify it"""

    def action_draft(self):
        self.state = 'draft'
        for allocation in self:
            allocation.attendance_ids = [(5, 0, 0)]
            """This function is used to unlink the records attached to the model"""
