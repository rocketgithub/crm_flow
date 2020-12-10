# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Team(models.Model):
    _inherit = 'crm.team'

    tipo_cita_id = fields.Many2one('calendar.appointment.type','Tipo de Cita')
