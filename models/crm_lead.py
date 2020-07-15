import logging
import threading
from psycopg2 import sql
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
from odoo.addons.phone_validation.tools import phone_validation
from collections import OrderedDict, defaultdict

from . import crm_stage

 
class Lead(models.Model):
    _inherit = 'crm.lead'
    
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for rec in self:
            oportunidad = self.env['crm.lead'].browse(rec._origin.id)
            activity = self.env['mail.activity']
            model_id = self.env['ir.model'].search([('model','=','crm.lead')])
            
            base = fields.Date.context_today(rec)
            if rec.activity_type_id.delay_from == 'previous_activity' and 'activity_previous_deadline' in self.env.context:
                base = fields.Date.from_string(self.env.context.get('activity_previous_deadline'))
            rec.date_deadline = base + relativedelta(**{rec.activity_type_id.delay_unit: rec.activity_type_id.delay_count})
            
            logging.getLogger('ACAAAAA---0').warn(rec.date_deadline)
            activity_ins = activity.create(
            {
            'res_id': oportunidad.id,
            'res_model_id': model_id.id,
            'res_model':model_id.name,
            'activity_type_id':rec.stage_id.actividad_inicial.id,
            'date_deadline':  rec.date_deadline,
            'user_id': rec.user_id.id
            })