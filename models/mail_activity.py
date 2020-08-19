# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import logging

class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    delay_unit = fields.Selection(selection_add=[('horas', 'horas')])
    fecha_sugerida_count = fields.Integer(
        'Fecha de inicio sugerida', default=0)
    fecha_sugerida_unit = fields.Selection([
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('months', 'months'),
        ('horas', 'horas')], string="Delay units", default='days')
    fecha_sugerida_from = fields.Selection([
        ('current_date', 'después de la fecha de validación'),
        ('previous_activity', 'después de la fecha límite de actividad anterior')], string="Delay Type", default='previous_activity')


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    hora = fields.Float('hora', default=0)
    fecha_sugerida = fields.Date('Fecha inicio sugerida',default=fields.Date.context_today)

    # Sobree escribimos la función por que en una parte del código da error al usar horas
    @api.onchange('activity_type_id')
    def _onchange_activity_type_id(self):
        if self.activity_type_id:
            self.summary = self.activity_type_id.summary

            datos = self._obtener_fechas(self.activity_type_id)
            self.fecha_sugerida = datos['fecha_sugerida']
            self.date_deadline = datos['date_deadline']
            self.hora = datos['hora']
            self.user_id = self.activity_type_id.default_user_id or self.env.user
            if self.activity_type_id.default_description:

                self.note = self.activity_type_id.default_description

    # Funcion que retorna date_deadline, fecha_limite
    def _obtener_fechas(self,activity_type_id):
        datos = {'date_deadline': False, 'hora': False, 'fecha_sugerida': False}
        base = fields.Date.context_today(self)
        base_fecha_sugerida = fields.Date.context_today(self)
        hoy = fields.Datetime.context_timestamp(self, timestamp=datetime.now())

        if activity_type_id.delay_from == 'previous_activity' and 'activity_previous_deadline' in self.env.context:
            base = fields.Date.from_string(self.env.context.get('activity_previous_deadline'))

        if activity_type_id.fecha_sugerida_from  == 'previous_activity' and 'activity_previous_deadline' in self.env.context:
            base_fecha_sugerida = fields.Date.from_string(self.env.context.get('activity_previous_deadline'))

        if activity_type_id.fecha_sugerida_unit != 'horas':
            datos['fecha_sugerida'] = base_fecha_sugerida + relativedelta(**{activity_type_id.fecha_sugerida_unit: activity_type_id.fecha_sugerida_count})
        else:
            hora_fecha_limite = hoy+relativedelta(hours=+activity_type_id.fecha_sugerida_count)
            minuto_final = hora_fecha_limite.strftime('%M')
            datos['fecha_sugerida'] = hora_fecha_limite.strftime('%Y-%m-%d')

        if activity_type_id.delay_unit != 'horas':
            datos['date_deadline'] = base + relativedelta(**{self.activity_type_id.delay_unit: self.activity_type_id.delay_count})
        else:
            # hora_actual = hoy.strftime('%H:%M')
            hora_limite = hoy+relativedelta(hours=+self.activity_type_id.delay_count)
            hora = hora_limite.strftime('%H')
            minuto = hora_limite.strftime('%M')
            datos['date_deadline'] = hora_limite.strftime('%Y-%m-%d')

        return datos
