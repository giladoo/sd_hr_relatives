# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SdHrDocumentsRelatives(models.Model):
    _inherit = 'sd_hr_documents.attachments'

    relative_id = fields.Many2one('sd_hr_relatives.members',
                                  default=lambda self: self.env.context.get('relative_id', False))


    def employee_action_document_view(self):
        context = dict(self.env.context)
        context['relative_id'] = self.relative_id.id
        print(f"\n %%%%%%%%%%%>>>>>>>>>>\n context: {context}\n")
        return super().employee_action_document_view()


class SdHrDocumentsRelativesDocumentTypes(models.Model):
    _inherit = 'sd_hr_documents.document_type'

    relative_auto_create = fields.Boolean(default=False)
