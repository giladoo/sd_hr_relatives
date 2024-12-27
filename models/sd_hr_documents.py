# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SdHrDocumentsRelatives(models.Model):
    _inherit = 'sd_hr_documents.attachments'

    relative_id = fields.Many2one('sd_hr_relatives.members')


