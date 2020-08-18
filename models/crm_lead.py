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
            fecha_limite = False
            fecha_sugerida = False
            hora = 0
            base = fields.Date.context_today(rec)
            base_fecha_sugerida =  fields.Date.context_today(rec)
            hoy = fields.Datetime.context_timestamp(rec, timestamp=datetime.now())

            if rec.stage_id.actividad_inicial.fecha_sugerida_from  == 'previous_activity' and 'activity_previous_deadline' in self.env.context:
                base_fecha_sugerida = fields.Date.from_string(self.env.context.get('activity_previous_deadline'))


            if rec.stage_id.actividad_inicial.fecha_sugerida_unit != 'horas':
                fecha_sugerida = base_fecha_sugerida + relativedelta(**{rec.activity_type_id.fecha_sugerida_unit: rec.activity_type_id.fecha_sugerida_count})
            else:
                hora_fecha_limite = hoy+relativedelta(hours=+rec.activity_type_id.fecha_sugerida_count)
                hora_final = hora_fecha_limite.strftime('%H')
                minuto_final = hora_fecha_limite.strftime('%M')
                # hora_final_limite = int(hora_limite) + int(minuto_limite)/60
                fecha_sugerida = hora_fecha_limite.strftime('%Y-%m-%d')


            if rec.stage_id.actividad_inicial.delay_unit != 'horas':
                date_deadline = base + relativedelta(**{rec.stage_id.actividad_inicial.delay_unit: rec.stage_id.actividad_inicial.delay_count})
            else:
                hora_limite = hoy+relativedelta(hours=+rec.stage_id.actividad_inicial.delay_count)
                hora = hora_limite.strftime('%H')
                minuto = hora_limite.strftime('%M')
                hora_final = int(hora) + int(minuto)/60
                date_deadline = hora_limite.strftime('%Y-%m-%d')
                hora = float(hora_final)


            activity_ins = activity.create(
            {
            'res_id': oportunidad.id,
            'res_model_id': model_id.id,
            'res_model':model_id.name,
            'activity_type_id':rec.stage_id.actividad_inicial.id,
            'date_deadline':  date_deadline,
            'hora': hora,
            'fecha_sugerida': fecha_sugerida,
            'user_id': rec.user_id.id
            })

    def cambiar_estado(self,actividad):
        actividad_id = self.env['mail.activity'].search([('id','in',actividad)])
        if actividad_id and actividad_id.res_model == 'crm.lead' and actividad_id.res_id:
            oportunidad_id = self.env['crm.lead'].search([('id','=', actividad_id.res_id)])
            if oportunidad_id:
                estado_ids = self.env['crm.stage'].search([], order="sequence asc").ids
                logging.warn(estado_ids)
                if estado_ids:
                    posicion_estado_actual = estado_ids.index(oportunidad_id.stage_id.id)
                    logging.warn(posicion_estado_actual)
                    oportunidad_id.write({'stage_id': estado_ids[posicion_estado_actual+1]})
                    oportunidad_id._onchange_stage_id()

