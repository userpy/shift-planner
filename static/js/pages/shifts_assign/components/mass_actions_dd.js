page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-mass-action-dd', {
			name: 'sa-mass-action-dd',
			props: ['shifts', 'on-copy-to-future-start', 'on-copy-to-present-start', 
							'on-exit-shift-selection', 'on-edit-start', 'on-edit-success', 
							'on-delete-success', 'on-edit-error', 'short-cut-start-copy-to-present',
							'higlighted-day-codes', 'widget-body', 'compWrap', 'is-dtime-readonly',
							'settings', 'curr-work-mode', 'create-avail', 'remove-avails', 'is-any-avail-in-zone','body-scroll-pos'
						],
			template: '\
				<div class="sa-selection-options" :style="{top: cssTop, left: cssLeft}" ref="ddBody">\
					<div class="butts-wrap">\
						<template v-if="!currWorkMode">\
							<button type="button" v-if="settings.isAllowedTo.copyHere"        class="m-btn btn btn-secondary" @click="onCopyToPresentStart"> <i class="fa fa-copy"></i> Копировать (Ctrl + C) </button>\
							<button type="button" v-if="settings.isAllowedTo.copyToFuture"    class="m-btn btn btn-secondary" @click="onCopyToFutureStart"> <i class="fa fa-copy"></i> Повторить в будущем </button>\
							<button type="button" v-if="settings.isAllowedTo.changeEmployee && !isAnyShiftReadonly" class="m-btn btn btn-secondary" @click="onExpandEmplSelectClick"> <i class="fa fa-user"></i> Назначить сотрудника <i class="fa fa-angle-right icon-expand" ref="change_empl_butt"></i> </button>\
							<button type="button" v-if="settings.isAllowedTo.remove && !isAnyShiftReadonly"         class="m-btn btn btn-secondary" @click="onRemoveShiftClick"> <i class="fa fa-trash m--font-danger"></i> Удалить </button>\
							<button type="button"                                             class="m-btn btn btn-secondary" @click="onExitShiftSelection"> <i class="fa fa-times"></i> Снять выделение</button>\
						</template>\
						<template v-if="isAvailMode">\
							<button type="button" class="m-btn btn btn-secondary" @click="createAvailLocal"> <i class="fa fa-plus"></i> Отметить как недоступное </button>\
							<button type="button" v-if="isAnyAvailInZone" class="m-btn btn btn-secondary" @click="removeAvailsLocal"> <i class="fa fa-trash m--font-danger"></i> Удалить недоступности </button>\
							<button type="button" class="m-btn btn btn-secondary" @click="onExitShiftSelection"> <i class="fa fa-times"></i> Снять выделение</button>\
						</template>\
					</div>\
					<sa-empl-select-dd v-if="isShowingEmplSelectDd"\
						:shifts="shifts"\
						:comp-wrap="compWrap"\
						:on-empl-select="onEmplChange"\
						:target-el="changeEmplButt"\
					></sa-empl-select-dd>\
				</div>'
			,
			data: function(){return{
				selectedEmployee: null,
				error: null,
				isSmthLoading: false,
				ddBody: null,
				isShowingEmplSelectDd: false
			}},
			computed: {
				isAvailMode: function(){
					return this.currWorkMode == 'promo' || this.currWorkMode == 'broker' 
				},
				isAnyShiftReadonly: function(){
					var compVm = this
					return this.localShifts.some(function(s){
						return compVm.isDtimeReadonly(s.start_dtime)
					})
				},
				localShifts: function(){
					return (this.shifts || []).map(function(s){return new Shift(s)})
				},
				changeEmplButt: function(){
					return this.$refs.change_empl_butt
				},
				cssTop: function(){
					var daysRowRect = this.widgetBody.ae$('.days-line').getBoundingClientRect()
					var top = Math.max(
						daysRowRect.top + daysRowRect.height, 
						this.visibleDayElemRect.top-this.bodyScrollPos) + 20
					return Math.min(top, window.innerHeight - 200)+ 'px'

				},
				cssLeft: function(){
					var left = this.visibleDayElemRect.left
					var ddWidth = 210
					if(left + ddWidth > window.innerWidth) left = window.innerWidth - ddWidth - 20
					return left + 'px'
				},
				visibleDayElemRect: function(){
					var day = null
					var count = this.higlightedDayCodes.length - 1
					while(!day && count>=0){
						day = ae$('[data-day-code="'+ this.higlightedDayCodes[count] +'"]')
						count--
					}
					return day.getBoundingClientRect()
				},
				onClickAfterEmplSelectExpandBt: function(){return this.onClickAfterEmplSelectExpand.bind(this)}
			},
			methods:{
				createAvailLocal: function(){
					this.createAvail()
					this.onExitShiftSelection()
				},
				removeAvailsLocal: function(){
					this.removeAvails()
					this.onExitShiftSelection()
				},
				onClickAfterEmplSelectExpand: function(e){
					var target = e.target
					if(!target.findElemByClass('empl-select-dd')){
						document.body.removeEventListener('click', this.onClickAfterEmplSelectExpandBt)
						this.isShowingEmplSelectDd = false
					}
				},
				onExpandEmplSelectClick: function(){
					this.isShowingEmplSelectDd = true
					var compVm = this
					document.body.removeEventListener('click', this.onClickAfterEmplSelectExpandBt)
					Vue.nextTick(function(){
						document.body.addEventListener('click', compVm.onClickAfterEmplSelectExpandBt)
					})
				},
				onRemoveShiftClick: function(){
					if(!confirm('Удалить '+ this.shifts.length +' смены?')) return
					this.onEditStart()
					removeShifts(this)
				},
				onChildLoadingStart: function(){
					this.isSmthLoading = true
				},
				onChildLoadingEnd: function(){
					this.isSmthLoading = false
				},
				onEmplChange: function(newEmpl){
					this.selectedEmployee = newEmpl
					document.body.removeEventListener('click', this.onClickAfterEmplSelectExpandBt)
					this.isShowingEmplSelectDd = false
					this.onSaveChangesClick()
					this.onExitShiftSelection()
				},
				onSaveChangesClick: function(){
					var compVm = this
					var shifts = compVm.localShifts
					shifts = shifts.map(function(s){
						s.employee = compVm.selectedEmployee || s.employee
						s.employee_id = s.employee ? s.employee.id : null
						return s
					})
					saveShiftData(compVm)
				},
			},
			mounted: function(){
				this.ddBody = this.$refs.ddBody
				addEventListener('keydown', this.shortCutStartCopyToPresent)
			},
			destroyed: function(){
				removeEventListener('keydown', this.shortCutStartCopyToPresent)
			},
		})
		var saveShiftData = function(compVm){
			var shifts = compVm.localShifts.map(function(s){
				var newS = new Shift(s)
				newS.employee = compVm.selectedEmployee || newS.employee
				newS.employee_id = newS.employee ? newS.employee.id : null
				return newS
			})
			compVm.onEditStart()
			shift_assign.massAddOrEditShifts(
				{shifts: shifts},
				function(r){ compVm.onExitShiftSelection(); compVm.onEditSuccess(r)} ,
				function(r){ compVm.onEditError(); handleError(r, compVm) }
			)
		}
		var removeShifts = function(compVm){
			shift_assign.removeShifts(
				compVm.localShifts,
				function(){ compVm.onExitShiftSelection(); compVm.onDeleteSuccess(compVm.localShifts)},
				function(r){compVm.onEditError(); handleError(r, compVm) }
			)
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
	}
}())



{/* <div class="sse-row text-row">\
Смен выбрано: <span v-text="localShifts.length"></span>\
</div>\
<div class="sse-row">\
<button class="btn btn-secondary" @click="onCopyToFutureStart" :disabled="!shifts.length">Повторить в будущем</button>\
</div>\
<div class="sse-row">\
<button class="btn btn-secondary" @click="onCopyToPresentStart" :disabled="!shifts.length">Копировать здесь</button>\
</div>\
<div class="sse-row employee-row" v-if="localShifts.length">\
<sa-empl-select\
	:shifts="localShifts"\
	:on-empl-change="onEmplChange"\
	:on-loading-start="onChildLoadingStart"\
	:on-loading-end="onChildLoadingEnd"\
></sa-empl-select>\
</div>\
<div class="sse-row errow-row m--font-danger" v-if="error">\
<span v-text="error.message"></span>\
</div>\
<div class="sse-row controls-row" v-if="!confirmShiftDeletion && localShifts.length">\
<button class="btn btn-success" :disabled="isSmthLoading" @click="onSaveChangesClick" >ОК</button>\
<div class="btn btn-danger btn-copy" style="margin-left: 15px" @click="confirmShiftDeletion = true"><i class="fa fa-trash-alt"></i></div>\
</div>\
<div class="sse-row controls-row" v-if="confirmShiftDeletion">\
<button class="btn btn-danger" style="margin-right: 15px" @click="onRemoveShiftClick" v-text="localShifts.length > 1? \'Удалить смены\' : \'Удалить смену\'"></button>\
<button class="btn btn-secondary" @click="confirmShiftDeletion = false">Отмена</button>\
</div>\
</div>\  */}