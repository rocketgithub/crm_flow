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


