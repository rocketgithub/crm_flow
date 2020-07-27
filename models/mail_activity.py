# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
import pytz

from odoo import api, exceptions, fields, models, _

from odoo.tools.misc import clean_context
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

_logger = logging.getLogger(__name__)


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

    def done_ac(self,actividad):
        actividad_id = self.env['mail.activity'].search([('id','in',actividad)])
        if actividad_id:
            actividad_id.action_done()
        return True

    @api.onchange('activity_type_id')
    def _onchange_activity_type_id(self):
        if self.activity_type_id:

            self.summary = self.activity_type_id.summary
            # Date.context_today is correct because date_deadline is a Date and is meant to be
            # expressed in user TZ
            base = fields.Date.context_today(self)

            if self.activity_type_id.delay_from == 'previous_activity' and 'activity_previous_deadline' in self.env.context:
                base = fields.Date.from_string(self.env.context.get('activity_previous_deadline'))

            if self.activity_type_id.delay_unit != 'horas':
                self.date_deadline = base + relativedelta(**{self.activity_type_id.delay_unit: self.activity_type_id.delay_count})
            else:


                # self.date_deadline = base


                hoy = fields.Datetime.context_timestamp(self, timestamp=datetime.now())
                # hora_actual = hoy.strftime('%H:%M')
                logging.warn(hoy)
                hora_limite = hoy+relativedelta(hours=+self.activity_type_id.delay_count)
                logging.warn('HOR LIMITE')
                logging.warn(hora_limite)
                hora = hora_limite.strftime('%H')
                minuto = hora_limite.strftime('%M')
                logging.warn(hora_limite)
                hora_final = int(hora) + int(minuto)/60

                self.date_deadline = hora_limite.strftime('%Y-%m-%d')
                self.hora = float(hora_final)

            self.user_id = self.activity_type_id.default_user_id or self.env.user
            if self.activity_type_id.default_description:

                self.note = self.activity_type_id.default_description
