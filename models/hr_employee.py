# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SdHrRelativesEmployee(models.Model):
    _inherit = 'hr.employee'

    relative_ids = fields.One2many('sd_hr_relatives.members',
                                   'employee_id',
                                   string="Relatives")


    relative_count = fields.Integer(compute='_compute_relative_count',
                                    string='Relatives',
                                    help='Count of relatives.')

    def _compute_relative_count(self):
        for rec in self:
            rec.relative_count = len(rec.relative_ids)


    def action_relative_view(self):
        self.ensure_one()
        # return {}
        return {
            'name': _('Relatives'),
            'domain': [('employee_id', '=', self.id)],
            'res_model': 'sd_hr_relatives.members',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': "{'employee_id': %s}" % self.id
        }
