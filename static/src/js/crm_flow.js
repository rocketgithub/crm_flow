odoo.define('crm_flow.crm_flow', function (require) {
"use strict";


var mailUtils = require('mail.utils');
var core = require('web.core');
var mailUtils = require('mail.utils');
var time = require('web.time');
var session = require('web.session');
var rpc = require('web.rpc');
var QWeb = core.qweb;
var _t = core._t;


var Activity = require('mail.Activity');

// Pasamos como parametro extra tipos_actividades en la función por que necesitamos saber si el tipo de activdad usa horas
// por cada actividad normalmente retorna un diccionario donde contiene una llave llamada activity_type_id donde solo retorna el id
// y nombre de actividad, pero no si son horas o no, tipos_actividades info extra una de esllas son si se usa por horas o no
var setDelayLabel = function (activities,tipos_actividades){
    var today = moment().startOf('day');
    _.each(activities, function (activity){

        // Asigamos delay_unit y delay_count a la activdad que actual
        _.each(tipos_actividades, function (tipo) {
            console.log(tipo)
            if (activity.activity_type_id[0] == tipo.id){
                activity.activity_type_id.push(tipo.delay_unit)
                activity.activity_type_id.push(tipo.delay_count)
            }
        });

        var toDisplay = '';
        var diff = activity.date_deadline.diff(today, 'days', true); // true means no rounding
        var texto_horas = "";
        var ahora = new Date();
        var horasRestantes = false;
        var dias = 0;
        var horas = 0;
        var minutos = 0;


        activity['end_date'] = activity.create_date._i //Asignamos la fecha inicial a la final para despues sumar horas en caso fuera necesario
        var cantidad_horas = activity.activity_type_id[3]  //Asignamos horas se encuentra en la posición 3 del arreglo
        activity['end_date'].setHours(activity['end_date'].getHours() + cantidad_horas) //Sumamos horas

        var fecha_inicio = new Date(activity.create_date._d);    //Convertimos a tipo Fecha para hacer la resta
        var fecha_fin = new Date(activity['end_date']);

        if (ahora <= fecha_fin){
            // Obtenemos días, horas, minutos
            var delta = Math.abs(fecha_fin - ahora) / 1000;
            dias = Math.floor(delta / 86400);
            delta -= dias * 86400;
            horas = Math.floor(delta / 3600) % 24;
            delta -= horas * 3600;
            minutos = Math.floor(delta / 60) % 60;
            delta -= minutos * 60;
        }

        console.log(horas)
        console.log(minutos)
        if (activity.activity_type_id[2] == 'horas' & (horas >= 1 || minutos >= 1)){
            // Si existen horas agregamos string necesarios
            var horasRestantes = horas.toString()+ ' horas y ' + minutos.toString() + ' minutos'
            texto_horas = " en "+horasRestantes.toString()
        }

        if (diff === 0){
            toDisplay = _t("Today");

            if (activity.activity_type_id[2] == 'horas' & (horas >= 1 || minutos >= 1)){
                toDisplay = _t("Today")+_t(texto_horas);
            }else{
                toDisplay = _t("Vencido");
                activity.state = "overdue";
            }
        } else {
            if (diff < 0){ // overdue
                if (diff === -1){
                    toDisplay = _t("Yesterday");
                } else {
                    toDisplay = _.str.sprintf(_t("%d days overdue"), Math.abs(diff));
                }
            } else { // due
                if (diff === 1){
                    toDisplay = _t("Tomorrow");


                    if (activity.activity_type_id[2] == 'horas' & (horas >= 1 || minutos >= 1)){
                        toDisplay = _t("Tomorrow") + _t(texto_horas);
                    }


                } else {
                    toDisplay = _.str.sprintf(_t("Due in %d days"), Math.abs(diff));

                    if (activity.activity_type_id[2] == 'horas' & (horas >= 1 || minutos >= 1)){
                        toDisplay = _.str.sprintf(_t("Due in %d days")+_t(texto_horas), Math.abs(diff));
                    }


                }
            }
        }
        activity.label_delay = toDisplay;
    });
    console.log(activities)
    return activities;
};

var setFileUploadID = function (activities) {
    _.each(activities, function (activity) {
        if (activity.activity_category === 'upload_file') {
            activity.fileuploadID = _.uniqueId('o_fileupload');
        }
    });
    return activities;
};

var Acti = Activity.include({
    events: {
        'click .o_edit_activity': '_onEditActivity',
        'change input.o_input_file': '_onFileChanged',
        'click .o_mark_as_done': '_onMarkActivityDone',
        'click .o_mark_as_done_upload_file': '_onMarkActivityDoneUploadFile',
        'click .o_activity_template_preview': '_onPreviewMailTemplate',
        'click .o_schedule_activity': '_onScheduleActivity',
        'click .o_activity_template_send': '_onSendMailTemplate',
        'click .o_unlink_activity': '_onUnlinkActivity',
    },

    init: function (parent, options) {
        this._super.apply(this, arguments);
    },

    // Retornamos falso para que no deje editar
    _onEditActivity: function (ev) {
        return false;
    },

    _render: function () {
        _.each(this._activities, function (activity) {
            var note = mailUtils.parseAndTransform(activity.note || '', mailUtils.inline);
            var is_blank = (/^\s*$/).test(note);
            if (!is_blank) {
                activity.note = mailUtils.parseAndTransform(activity.note, mailUtils.addLink);
            } else {
                activity.note = '';
            }
        });
        //Declaramos variables de objetos a utilizar rpc, dentro de rpc no pueden se llamados comunmente
        var actividades = this._activities;
        var $el = this.$el;
        var _bindOnUploadAction = this._bindOnUploadAction;
        var _unbindOnUploadAction = this._unbindOnUploadAction;

        // Hacemos el rpc.query para buscaros lo tipos de actividad, acitivities no con contiene algúnos detos que necesitamos
        // id,delay_unit y delay_count
        rpc.query({
            model: 'mail.activity.type',
            method: 'search_read',
            args: [[],['id','delay_unit','delay_count']],
        }).then(
            function (tipos_actividades) {
                var activities = setFileUploadID(setDelayLabel(actividades,tipos_actividades));
                if (activities.length) {
                    var nbActivities = _.countBy(activities, 'state');
                    console.log(nbActivities)
                    $el.html(QWeb.render('mail.activity_items', {
                        uid: session.uid,
                        activities: activities,
                        nbPlannedActivities: nbActivities.planned,
                        nbTodayActivities: nbActivities.today,
                        nbOverdueActivities: nbActivities.overdue,
                        dateFormat: time.getLangDateFormat(),
                        datetimeFormat: time.getLangDatetimeFormat(),
                        session: session,
                        widget: this,
                    }));
                    _bindOnUploadAction(actividades);
                } else {
                    _unbindOnUploadAction(actividades);
                    $el.empty();
                }
            }
        );
    },

    _markActivityDone: function (params) {
        var activityID = params.activityID;
        var feedback = params.feedback || false;
        var attachmentIds = params.attachmentIds || [];

        this._rpc({
            model: 'crm.lead',
            method: 'cambiar_estado',
            args: [[],[activityID]],
        }).then(
            function (data) {

                location.reload();
            }
        );

        return this._sendActivityFeedback(activityID, feedback, attachmentIds)
            .then(this._reload.bind(this, { activity: true, thread: true }));
    },

});


});
