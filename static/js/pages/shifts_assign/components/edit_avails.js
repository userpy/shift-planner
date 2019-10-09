page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-edit-avail', {
			name: 'sa-edit-avail',
			props: ['avail-data', 'on-edit-start',
							'on-edit-error', 'on-exit-selection', 
							'comp-wrap', 'settings', 'workflowwidth'],
			template: '\
			<div class="sa-dropdown"\
				:style="{top: cssTop, left: cssLeft}" \
				ref="ddBody">\
				<div class="sse-row head-row">\
					<b v-text="avail.id > 0 ? \'Недоступность\' : \'Новая недоступность\'"></b>\
					<div class="btn m-btn--pill btn-secondary btn-sm" @click="onExitSelection"><i class="fa fa-times"></i></div>\
				</div>\
				<div class="sse-row time-row">\
					<vue-jq-date-range-picker\
						:start_dtime="avail.start_dtime"\
						:end_dtime="avail.end_dtime"\
						:on-change="onRangeChange"\
					></vue-jq-date-range-picker>\
				</div>\
				<div class="sse-row errow-row m--font-danger" v-if="error">\
					<span v-text="error.message"></span>\
				</div>\
				<div class="sse-row controls-row" v-if="!confirmDeletion">\
					<button class="btn btn-success" :disabled="avail.start_dtime >= avail.end_dtime" @click="onSaveChangesClick" >ОК</button>\
					<div class="btn btn-danger btn-copy" style="margin-left: 15px"  v-if="avail.id > 0" @click="confirmDeletion = true"><i class="fa fa-trash-alt"></i></div>\
				</div>\
				<div class="sse-row controls-row" v-if="confirmDeletion">\
					<button class="btn btn-danger" style="margin-right: 15px" @click="onRemoveAvailClick">Удалить недоступность</button>\
					<button class="btn btn-secondary" @click="confirmDeletion = false">Отмена</button>\
				</div>\
			</div>\
			',
			data: function(){return{
				confirmDeletion: false,
				error: null,
				cssTop: 0,
				cssLeft: 0,
				avail: new Availability(this.availData.avail),
				violations: [],
			}},
			computed: {
				timeStart: function(){
					return this.avail.start_dtime 
				},
				timeEnd: function(){
					return this.avail.end_dtime 
				},
			},
			mounted: function(){
				var ddBody = this.$refs.ddBody
				var targetEl = this.availData.targetEl
				var pos = calcPosForDropDown(targetEl.getBoundingClientRect(), ddBody.getBoundingClientRect())
				this.cssTop = pos.top +'px'
				var workWidth = parseFloat(this.workflowwidth.split('.')[0])
				this.cssLeft = pos.left > workWidth ? workWidth : pos.left
				this.cssLeft += 'px'
			},
			methods: {
				onRangeChange: function(start, end){
					this.avail.setStart(start)
					this.avail.setEnd(end)
				},
				onSaveChangesClick: function(){
					if(!isValid(this)) return
					saveAvailData(this)
				},
				onRemoveAvailClick: function(){
					this.onEditStart()
					removeAvail(this)
				}
			},
		})
	}
	var removeAvail = function(compVm){
		var compWrap = compVm.compWrap
		shift_assign.removeAvails(
			[compVm.avail],
			function(){
				compVm.onExitSelection()
				compWrap.loadAndGenerate()
			},
			function(r){compVm.onEditError(); handleError(r, compVm) }
		)
	}
	var saveAvailData = function(compVm){
		var avail = new Availability(compVm.avail)
		compVm.onEditStart()
		var compWrap = compVm.compWrap
		compWrap.massAddOrEditAvails(
			[avail],
			function(){
				compVm.onExitSelection()
				compWrap.loadAndGenerate()
			},
			function(r){compVm.onEditError(); handleError(r, compVm) }
		)
	}
	var isValid = function(compVm){
		var avail = compVm.avail
		if(avail.start_dtime > avail.end_dtime){
			showError({
				message: 'Дата начала больше даты окончания' //todo l10n
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