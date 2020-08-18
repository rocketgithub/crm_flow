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

from odoo.tools.safe_eval import safe_eval
from . import crm_stage

 
class Lead(models.Model):
    _inherit = 'crm.lead'

    tipo_interes_id = fields.Many2one('product.template', string='Tipo de interés')
    sede_id = fields.Char(string='Sede')
    
    def eval_dominio(self, dominio):
        domain = safe_eval(dominio)
        return domain
    
    @api.model
    def create(self, vals):
        rec = super().create(vals)
        rec._onchange_stage_id()
        return rec
    
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for rec in self:
            oportunidad = self.env['crm.lead'].browse(rec._origin.id)
            activity = self.env['mail.activity']
            model_id = self.env['ir.model'].search([('model','=','crm.lead')])
            
            base = fields.Date.context_today(rec)
            date_deadline = base + relativedelta(**{rec.stage_id.actividad_inicial.delay_unit: rec.stage_id.actividad_inicial.delay_count})
            activity_ins = activity.create(
            {
            'res_id': oportunidad.id,
            'res_model_id': model_id.id,
            'res_model':model_id.name,
            'activity_type_id':rec.stage_id.actividad_inicial.id,
            'date_deadline':  date_deadline,
            'user_id': rec.user_id.id
            })
    
    