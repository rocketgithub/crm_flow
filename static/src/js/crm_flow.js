odoo.define('crm_flow.crm_flow', function (require) {
"use strict";


// var mailUtils = require('mail.utils');
//
var AbstractField = require('web.AbstractField');
// var BasicModel = require('web.BasicModel');
// var config = require('web.config');
var core = require('web.core');
var mailUtils = require('mail.utils');
// var field_registry = require('web.field_registry');
var session = require('web.session');
var framework = require('web.framework');
var time = require('web.time');

var QWeb = core.qweb;
var _t = core._t;


var Activity = require('mail.Activity');


var setDelayLabel = function (activities){

    function float_to_hour(num) {
        var sign = num >= 0 ? 1 : -1;
        var min = 1 / 60;
        // Get positive value of num
        num = num * sign;
        // Separate the int from the decimal part
        var intpart = Math.floor(num);
        var decpart = num - intpart;
        // Round to nearest minute
        decpart = min * Math.round(decpart / min);
        var minutes = Math.floor(decpart * 60);
        // Sign result
        sign = sign == 1 ? '' : '-';
        // pad() adds a leading zero if needed
        // return sign + intpart + 'h' + pad(minutes, 2);
        return parseFloat(sign + intpart + '.' + minutes);
    }

    var today = moment().startOf('day');
    _.each(activities, function (activity){
        var toDisplay = '';
        var diff = activity.date_deadline.diff(today, 'days', true); // true means no rounding
        var horas = activity.hora;
        var texto_horas = "";
        var hora_convertida = "";


        var today = new Date();
        var hora = today.getHours();
        var minuto = today.getMinutes();
        var horasRestantes = false;


        if (horas >= 1){
            var hora_convertida = float_to_hour(horas);
            var timeStart = activity.date_deadline._d;
            var horaTimeStart = hora_convertida.toString().split('.')[0];
            var minutoTimeStart = hora_convertida.toString().split('.')[1];
            timeStart.setHours(parseInt(horaTimeStart), parseInt(minutoTimeStart));
            var timeEnd = today;

            var hourDiff = timeStart - timeEnd;
            var diffHrs = ((hourDiff % 86400000) / 3600000);

            horasRestantes = float_to_hour(diffHrs)
            texto_horas = " con "+horasRestantes.toString() +" hora (s)"
        }

        if (diff === 0){
            toDisplay = _t("Today");

            if (horas >= 1){
                toDisplay = _t("Today")+_t(texto_horas);
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


                    if (horas >= 1){
                        toDisplay = _t("Tomorrow") + _t(texto_horas);
                    }


                } else {
                    toDisplay = _.str.sprintf(_t("Due in %d days"), Math.abs(diff));

                    if (horas >= 1){
                        toDisplay = _.str.sprintf(_t("Due in %d days")+_t(texto_horas), Math.abs(diff));
                    }


                }
            }
        }
        activity.label_delay = toDisplay;
    });
    return activities;
};


/**
 * Set the file upload identifier for 'upload_file' type activities
 *
 * @param {Array} activities list of activity Object
 * @return {Array} : list of modified activity Object
 */
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
        'click .o_mark_as_done_next':'_onMarkActivityNextStage',
        'click .o_mark_as_done_upload_file': '_onMarkActivityDoneUploadFile',
        'click .o_activity_template_preview': '_onPreviewMailTemplate',
        'click .o_schedule_activity': '_onScheduleActivity',
        'click .o_activity_template_send': '_onSendMailTemplate',
        'click .o_unlink_activity': '_onUnlinkActivity',
    },


    init: function (parent, options) {
        this._super.apply(this, arguments);
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
        var activities = setFileUploadID(setDelayLabel(this._activities));
        // this.showa();
        if (activities.length) {
            var nbActivities = _.countBy(activities, 'state');
            this.$el.html(QWeb.render('mail.activity_items', {
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
            this._bindOnUploadAction(this._activities);
        } else {
            this._unbindOnUploadAction(this._activities);
            this.$el.empty();
        }
    },
    _onMarkActivityNextStage: function (ev, options) {
        ev.preventDefault();
        var activityID = $(ev.currentTarget).data('activity-id');
        // self._onMarkActivityDone(e)

        var options2 = _.defaults(options || {}, {
            model: 'mail.activity',
            args: [[],[activityID]],
        });
        this._rpc({
                model: options2.model,
                method: 'done_ac',
                args: options2.args,
            })
            .then(
                this._reload.bind(this, {activity: true})
            );


        options = _.defaults(options || {}, {
            model: 'crm.lead',
            args: [[],[activityID]],
        });
        // self._onMarkActivityDone(ev);
        return this._rpc({
                model: options.model,
                method: 'cambiar_estado',
                args: options.args,
            })
            .then(
                function (data) {

                    location.reload();
                }
            );

    },


});


});
