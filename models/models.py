# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SdHrRelativesMembers(models.Model):
    _name = 'sd_hr_relatives.members'
    _description = 'Relative Members'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'employee_id,birth_date'

    name = fields.Char(required=True, tracking=True)
    image_1920 = fields.Image("Image", max_width=1920, max_height=1920)

    employee_id = fields.Many2one('hr.employee', default=lambda self: self.env.context.get('employee_id', False),
                                  string="Employee", index=True,
                                  required=True)
    relative_type = fields.Many2one('sd_hr_relatives.relative_type', required=True, tracking=True,)
    birth_date = fields.Date()
    death_date = fields.Date()
    id_card = fields.Char()
    id_card_validation = fields.Char( store=False, compute='is_valid_iran_national_id')
    id_card_is_valid = fields.Boolean( default=False)
    birth_certificate_no = fields.Char()
    marriage_state = fields.Selection([('single', _('Single')), ('married', _('Married'))], )
    under_sponsorship = fields.Boolean(required=True, default=True)
    mobile_no = fields.Char()
    age = fields.Char(compute='_age_calculation', stare=True)

    @api.depends('birth_date', 'death_date')
    def _age_calculation(self):
        for rec in self:
            age = ''
            end_date = rec.death_date if rec.death_date else  fields.Date.today()
            if rec.birth_date and rec.birth_date > fields.Date.today():
                raise UserError(_('Birth date cannot be grater than today.'))
            elif rec.death_date and (rec.death_date < rec.birth_date or rec.death_date > fields.Date.today()):
                raise UserError(_('Death date is not correct.'))
            elif rec.birth_date:
                age = end_date.year - rec.birth_date.year - ((end_date.month, end_date.day) < (rec.birth_date.month, rec.birth_date.day))
            else:
                age = ''
            rec.age = age


# TODO: constraint on name to prevent duplicate
    @api.depends('id_card')
    @api.onchange('id_card')
    def is_valid_iran_national_id(self, ) -> bool:
        """
        Validates an Iranian national ID (کارت ملی).

        Args:
            national_id (str): The national ID as a string.

        Returns:
            bool: True if valid, False otherwise.
        """
        national_id = self.id_card
        # Ensure it is a 10-digit number
        if not national_id or not national_id.isdigit() or len(national_id) != 10:
            res = False
            # Check if all digits are the same (e.g., 3333333333)
        elif national_id == national_id[0] * 10:
            res = False
        else:
            # Extract the first 9 digits and the checksum digit
            digits = list(map(int, national_id))
            checksum = digits[-1]
            coefficients = range(10, 1, -1)

            # Calculate the weighted sum of the first 9 digits
            weighted_sum = sum(d * c for d, c in zip(digits[:-1], coefficients))

            # Calculate the remainder
            remainder = weighted_sum % 11

            # Validate checksum based on remainder
            if remainder < 2:
                res = checksum == remainder
            else:
                res = checksum == 11 - remainder
        self.id_card_validation = _('Valid') if res else _('Not Valid')
        self.id_card_is_valid = res


class SdHrRelativesTypes(models.Model):
    _name = 'sd_hr_relatives.relative_type'
    _description = 'Relative Type'

    name = fields.Char(required=True, translate=True)
