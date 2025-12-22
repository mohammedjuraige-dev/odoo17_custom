from odoo import models, fields, api

class TrainingSession(models.Model):
    _name = 'training.session'
    _description = 'Training Session'



    name=fields.Char(string='Session name', required=True)
    trainee_ids = fields.Many2many(
        'res.partner',
        relation='my_trainees',domain=[('is_trainee', '=', True)]
    )

    instructor_ids=fields.Many2many('res.partner',string="Instructors",
         relation='my_instructors',domain=[('is_instructor', '=', True)])

    trainee_count = fields.Integer(compute='_compute_trainee_count',store=True,string='Trainee count')
    session_line_ids = fields.One2many('training.session.line', 'session_id', string="Session Lines")
    attended_count = fields.Integer(store=True, string="Attendee count", compute='attended_counter')


    @api.depends('trainee_ids')
    def _compute_trainee_count(self):
        for record in self:
            record.trainee_count = len(record.trainee_ids)

    @api.depends('session_line_ids.attended')
    def attended_counter(self):
        for record in self:
            record.attended_count = self.env['training.session.line'].search_count([
                ('session_id','=',record.id),
                ('attended','=',True),
            ])





















# @api.depends('session_line_ids')
    # def attended_counter(self):
    #     for record in self:
    #         count = 0
    #         for line in record.session_line_ids:
    #             if line.attended:
    #                 count += 1
    #         record.attended_count = count














"""
    Computes trainee_count for each training course.
    
    CRITICAL: Why the loop can give WRONG results without `record.trainee_ids`
    
    PROBLEM SCENARIO:
    ┌──────────────┬──────────────┬─────────────────────┐
    │ Session      │ Real Count   │ If using self:      │
    ├──────────────┼──────────────┼─────────────────────┤
    │ Python 101   │ 3 trainees   │ 12 (ALL records) ❌ │
    │ Java Master  │ 7 trainees   │ 12 (ALL records) ❌ │
    │ SQL Basics   │ 2 trainees   │ 12 (ALL records) ❌ │
    └──────────────┴──────────────┴─────────────────────┘
    
    EXECUTION FLOW (WRONG CODE):
    1. View loads → self = [ID1,ID2,ID3] (3 records together)
    2. for record in self: starts loop
       Iteration 1: record=ID1,  self.trainee_ids=[ID1+ID2+ID3]=12 → ID1.count=12
       Iteration 2: record=ID2,  self.trainee_ids=STILL 12 → ID2.count=12  
       Iteration 3: record=ID3,  self.trainee_ids=STILL 12 → ID3.count=12
    
    KEY CONCEPT:
    • self     = ALL records being processed (list view = multiple records)
    • record   = CURRENT single record in loop iteration
    
    WRONG: len(self.trainee_ids)  = TOTAL trainees across ALL sessions
    CORRECT: len(record.trainee_ids) = ONLY this session's trainees
    
    SOLUTION:
        record.trainee_count = len(record.trainee_ids)  # ✅ Each gets own count
    """
    