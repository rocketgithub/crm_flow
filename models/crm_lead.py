# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from psycopg2 import sql, extras
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError
from odoo.addons.phone_validation.tools import phone_validation
from collections import OrderedDict

import logging

class Lead(models.Model):
    _inherit = "crm.lead"

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
