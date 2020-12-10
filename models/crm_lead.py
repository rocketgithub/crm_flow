from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.tools.safe_eval import safe_eval
from . import crm_stage
import logging

class Lead(models.Model):
    _inherit = 'crm.lead'

    tipo_interes_id = fields.Many2one('product.template', string='Tipo de interés')

    def eval_dominio(self, dominio):
        domain = safe_eval(dominio)
        return domain

    @api.model
    def create(self, vals):
        rec = super(Lead, self).create(vals)
        rec._onchange_stage_crm_id()
        return rec

    @api.onchange('stage_id')
    def _onchange_stage_crm_id(self):
        for rec in self:
            logging.warn('entra a onchange')
            oportunidad = self.env['crm.lead'].browse(rec._origin.id)
            activity = self.env['mail.activity']
            model_id = self.env['ir.model'].search([('model','=','crm.lead')])
            fecha_limite = False
            fecha_sugerida = False
            hora = 0
            base = fields.Date.context_today(rec)
            base_fecha_sugerida =  fields.Date.context_today(rec)
            hoy = fields.Datetime.context_timestamp(rec, timestamp=datetime.now())
            date_deadline = False

            datos = activity._obtener_fechas(rec.stage_id.actividad_inicial)

            activity_ins = activity.create(
            {
            'res_id': oportunidad.id,
            'res_model_id': model_id.id,
            'res_model':model_id.name,
            'activity_type_id':rec.stage_id.actividad_inicial.id,
            'date_deadline':  datos['date_deadline'],
            'hora': datos['hora'],
            'fecha_sugerida': datos['fecha_sugerida'],
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
                    if len(estado_ids) > 0 and oportunidad_id.stage_id.is_won == False:
                        logging.warn(posicion_estado_actual)
                        oportunidad_id.write({'stage_id': estado_ids[posicion_estado_actual+1]})
                        oportunidad_id._onchange_stage_crm_id()


    def agendar_cita(self):
        for oportunidad in self:
            accion = {}
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            empleado_id = self.env['hr.employee'].search([('user_id','=', oportunidad.user_id.id)])
            if empleado_id and oportunidad.team_id.tipo_cita_id.employee_ids:
                website_url = False
                for empleado in oportunidad.team_id.tipo_cita_id.employee_ids:
                    if empleado.id == empleado_id.id:
                        website_url = oportunidad.team_id.tipo_cita_id.website_url
                        accion = {
                            "type": "ir.actions.act_url",
                            "url": str(base_url)+str(website_url)+'?employee_id='+str(empleado.id),
                            "target": "new",
                        }
            return accion
