# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

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
    document_ids = fields.One2many('sd_hr_documents.attachments',
                                   'relative_id',
                                   string="Documents")

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

    document_count = fields.Integer(compute='_compute_document_count',
                                    string='documents',
                                    help='Count of documents.')

    def _compute_document_count(self):
        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)]).id
        attachment_model = self.env['sd_hr_documents.attachments']
        for rec in self:
            # domain = [('related_model', '=', model_id), ('related_res_id', '=', rec.id)]
            domain = [('employee_id', '=', rec.employee_id.id),('relative_id', '=', rec.id)]
            rec.document_count = attachment_model.search_count(domain)


    # @api.model
    def open_document_attachments_action(self):
        model_id = self.env['ir.model'].sudo().search([('model', '=', self._name)])

        action = self.env.ref('sd_hr_documents.document_attachments_action').sudo().read()[0]
        if model_id:
            action['domain'] = [('employee_id', '=', self.employee_id.id),
                                # ('related_model', '=', model_id ),
                                # ('related_res_id', '=', self.id),
                                ]
            ctx = action.get('context', '{}')
            ctx_1 = ctx.replace("'", '"')
            ctx = json.loads(ctx_1)
            ctx['default_employee_id'] = self.employee_id.id if len(self.employee_id) else False
            action['context'] = ctx

        return action

    def action_document_view(self):
        self.ensure_one()
        context = dict(self.env.context)
        context['default_employee_id'] = self.employee_id.id
        model_id = self.env['ir.model'].sudo().search([('model', '=', 'sd_hr_relatives.members')]).id

        domain = [('employee_id', '=', self.employee_id.id),
                  # ('related_model', '=', model_id),
                  # ('related_res_id', '=', self.id)
                  ]
        print(f"\n %%%%%%%%%%%%%%%%%%% model_id: {model_id} action_document_view:\n context:{context} ")
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'sd_hr_documents.attachments',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': context
        }


    # @api.model
    # def default_get(self, fields_list):
        # defaults = super(SdHrRelativesMembers, self).default_get(fields_list)
        # context = dict(self.env.context)

        # print(f"\n >>>>>>> \n {fields_list} \n\n {defaults} \n\n {context}\n {super(SdHrRelativesMembers, self)}\n" )

        # if self.env.context.get('copy_from_previous'):
        #     last_record_id = self.env.context.get('last_record_id')
        #     if last_record_id:
        #         last_record = self.browse(last_record_id)
        #         # Copy specific fields
        #         defaults.update({
        #             'name': last_record.name,
        #             'description': last_record.description,
        #         })
        # return defaults


    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        documents = self.create_documents(res.employee_id.id, res.id)
        if not documents:
            logging.error(f"Default documents for new relative failed, res_id: {res.id}")
        return res

    def create_documents(self, employee_id, res_id):
        documents_model = self.env['sd_hr_documents.attachments']
        auto_create = self.env['sd_hr_documents.document_type'].search([('relative_auto_create', '=', True)])
        try:
            for rec in auto_create:
                documents_model.create({
                    'employee_id': employee_id,
                    'relative_id': res_id,
                    'document_type': rec.id,
                    'name': rec.name,
                })
            done = True
        except Exception as e:
            done = False

        return done




class SdHrRelativesTypes(models.Model):
    _name = 'sd_hr_relatives.relative_type'
    _description = 'Relative Type'

    name = fields.Char(required=True, translate=True)
