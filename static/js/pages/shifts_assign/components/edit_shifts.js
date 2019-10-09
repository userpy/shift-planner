page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-edit-shift', {
			name: 'sa-edit-shift',
			props: ['shift-data', 'on-edit-start', 'on-edit-success', 
							'on-delete-success', 'on-edit-error', 'on-exit-shift-selection', 
							'all-shifts', 'comp-wrap', 'settings'],
			template: '\
			<div class="sa-dropdown"\
				:style="{top: cssTop, left: cssLeft}" \
				ref="ddBody"\
				:class="{\'readonly-form\': shiftData.isReadonly}">\
				<div class="sse-row head-row">\
					<b v-text="shift.id > 0 ? \'Смена\' : \'Новая смена\'"></b>\
					<div class="btn m-btn--pill btn-secondary btn-sm" @click="onExitShiftSelection"><i class="fa fa-times"></i></div>\
				</div>\
				<div class="sse-row time-row" :class="{\'readonly\': !settings.isAllowedTo.changeTime}">\
					<vue-time-select\
						:time="timeStart"\
						@change.native="onTimeStartChange"\
					></vue-time-select>\
					<span style="padding: 0 9px">–</span>\
					<vue-time-select\
						:time="timeEnd"\
						@change.native="onTimeEndChange"\
					></vue-time-select>\
				</div>\
				<div class="sse-row errow-row m--font-danger" v-if="error">\
					<span v-text="error.message"></span>\
				</div>\
				<div class="sse-row employee-row" :class="{\'readonly\': !settings.isAllowedTo.changeEmployee}">\
					<sa-empl-select\
						:comp-wrap="compWrap"\
						:shifts="[shift]"\
						:on-empl-change="onEmplChange"\
						:on-loading-start="onChildLoadingStart"\
						:on-loading-end="onChildLoadingEnd"\
					></sa-empl-select>\
				</div>\
				<div class="sse-row errow-row violation-row" v-if="violations" v-for="viol in violations">\
					<div class="violation-text" :class="getClassForViolMessage(viol)">\
						<span v-text="viol.message"></span>\
						<br/>\
					</div>\
				</div>\
				<div class="sse-row controls-row" v-if="!confirmShiftDeletion && !shiftData.isReadonly">\
					<button class="btn btn-success" :disabled="isSmthLoading || (shift.start_dtime >= shift.end_dtime )" @click="onSaveChangesClick" >ОК</button>\
					<div class="btn btn-danger btn-copy" style="margin-left: 15px"  v-if="shift.id > 0 && settings.isAllowedTo.remove" @click="confirmShiftDeletion = true"><i class="fa fa-trash-alt"></i></div>\
				</div>\
				<div class="sse-row controls-row" v-if="confirmShiftDeletion">\
					<button class="btn btn-danger" style="margin-right: 15px" @click="onRemoveShiftClick">Удалить смену</button>\
					<button class="btn btn-secondary" @click="confirmShiftDeletion = false">Отмена</button>\
				</div>\
			</div>\
			',
			data: function(){return{
				isSmthLoading: false,
				selectedEmployee: null,
				confirmShiftDeletion: false,
				error: null,
				cssTop: 0,
				cssLeft: 0,
				shift: new Shift(this.shiftData.shift),
				violations: [],
			}},
			computed: {
				timeStart: function(){
					var start_dtime = this.shift.start_dtime 
					return start_dtime - new Date(start_dtime).startOfDay()
				},
				timeEnd: function(){
					var end_dtime = this.shift.end_dtime 
					return end_dtime - new Date(end_dtime).startOfDay()
				},
			},
			mounted: function(){
				var ddBody = this.$refs.ddBody
				var targetEl = this.shiftData.targetEl
				var pos = calcPosForDropDown(targetEl.getBoundingClientRect(), ddBody.getBoundingClientRect())
				this.cssTop = pos.top +'px'
				this.cssLeft = pos.left +'px'
				if(this.shift.has_violations && this.settings.isAllowedTo.checkViolations) loadViolations(this)
			},
			methods: {
				getClassForViolMessage: function(viol){
					switch (viol.level) {
						case 'low':
							return 'm--font-info'
						case 'medium':
							return 'm--font-warning'
						case 'high':
							return 'm--font-danger'
						default:
							return ''
					}
				},
				onChildLoadingStart: function(){
					this.isSmthLoading = true
				},
				onChildLoadingEnd: function(){
					this.isSmthLoading = false
				},
				onEmplChange: function(newEmpl){
					this.selectedEmployee = newEmpl
					var shift = this.shift
					shift.employee = newEmpl
					shift.employee_id = shift.employee ? shift.employee.id : null
					this.shift = shift
					if(newEmpl && newEmpl.id!='none' && this.settings.isAllowedTo.checkViolations) loadViolations(this)
				},
				onTimeStartChange: function(e){
					var dtime = e.target.getTime()
					var shift = this.shift
					var day_dtime = new Date(shift.start_dtime).startOfDay().getTime()
					shift.setStart(day_dtime + dtime, true)
					this.shift = shift
				},
				onTimeEndChange: function(e){
					var dtime = e.target.getTime()
					var shift = this.shift
					var day_dtime = new Date(shift.start_dtime).startOfDay().getTime()
					shift.setEnd(day_dtime + dtime, true)
					if(shift.start_dtime > shift.end_dtime) shift.setEnd(day_dtime + dtime + 1..day, true)
					this.shift = shift
				},
				onSaveChangesClick: function(){
					if(!isValid(this)) return
					saveShiftData(this)
				},
				onRemoveShiftClick: function(){
					this.onEditStart()
					removeShift(this)
				}
			},
		})
	}
	var loadViolations = function(compVm){
		compVm.compWrap.loadShiftViolations(
			{shift: compVm.shift},
			function(r){compVm.violations = r},
			function(r){compVm.onEditError(); handleError(r, compVm) }
		)
	}
	var removeShift = function(compVm){
		shift_assign.removeShifts(
			[compVm.shift],
			function(){compVm.onDeleteSuccess([compVm.shift])},
			function(r){compVm.onEditError(); handleError(r, compVm) }
		)
	}
	var saveShiftData = function(compVm){
		var shift = new Shift(compVm.shift)
		var oldShifts = compVm.allShifts.filter(function(s){return s.id == shift.id})
		if(oldShifts.length && isEquivalent(oldShifts[0], shift)) {compVm.onExitShiftSelection(); return}
		compVm.onEditStart()
		shift.employee = compVm.selectedEmployee || shift.employee
		shift.employee_id = shift.employee ? shift.employee.id : null
		shift_assign.addOrEditShift(
			shift,
			compVm.onEditSuccess,
			function(r){ compVm.onEditError(); handleError(r, compVm) }
		)
	}
	var isValid = function(compVm){
		var allShifts = compVm.allShifts
		var shift = compVm.shift
		if(shift_assign.isShiftIntersectsWithAny(allShifts, shift)){
			showError({
				message: 'Смена пересекается с соседней' //todo l10n
			}, compVm)
			return false
		}
		if(shift.duration < 4..hours){
			showError({
				message: 'Смена должна быть дольше четырех часов' //todo l10n
			}, compVm)
			return false
		}
		return true
	}
	var errTimer
	var handleError = function(r, compVm){
		var r = r.responseJSON || {}
		var errors = Object.keys(r).map(function(ok){
			return r[ok]
		}).join('; ') || null
		showError({	message: r.message || errors || 'Произошла неизвестная ошибка' }, compVm) //todo l10n
	}
	var showError = function(error, compVm){
		clearTimeout(errTimer)
		compVm.error = null
		Vue.nextTick(function(){
			compVm.error = error
			errTimer = setTimeout(function(){compVm.error = null}, 3000)
		})
	}
}())