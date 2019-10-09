page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-empl-select', {
			name: 'sa-empl-select',
			props: ['shifts', 'onEmplChange', 'compWrap', 'shouldCheckAvailableEmpls', 'onLoadingStart', 'onLoadingEnd'],
			template: '\
				<div class="empl-select" ref="comp_body">\
					<div class="alert alert-warning" v-if="warning" v-text="emplNotAllowed"></div>\
					<div class="errow-row m--font-danger" v-if="error">\
						<span v-text="error.message"></span>\
					</div>\
					<button type="button" class="btn btn-secondary change-empl-butt" ref="changeEmplButt" @click="onExpandEmplSelectClick($event)">\
						<span v-text="selectedEmpl.text"></span>\
						<i class="fa fa-angle-down"></i>\
					</button>\
					<sa-empl-select-dd v-if="isShowingEmplSelectDd"\
						:shifts="shifts"\
						:comp-wrap="compWrap"\
						:on-empl-select="onEmplChangeLocal"\
						:target-el="changeEmplButt"\
						:select-tab="changeEmplDdTab"\
					></sa-empl-select-dd>\
					<div class="clear-select" @click="onClearSelectClick"><i class="fa fa-times"></i></div>\
				</div>\
			',
			data: function(){return{
				selectedEmpl: this.shifts[0].employee || emptyEmpl,
				isShowingEmplSelectDd: false,
				prevStartDtime: this.shifts[0].start_dtime,
				prevEndDtime: this.shifts[0].end_dtime,
				warning: null,
				changeEmplDdTab: null,
				emplNotAllowed: 'Назначенный ранее сотрудник не может взять смену в это время', //todo l10n
				error: null,
			}},
			computed:{
				changeEmplButt: function(){
					return this.$refs.changeEmplButt
				},
				selectedEmployee: function(){
					if(this.shifts.length > 1){
						// когда много смен, нужно выбрать правильного сотрудника в селекторе
						findSelectedEmpl(this)
					} else {
						if(this.warning){
							return emptyEmpl
						}
						return (this.shifts[0].employee || emptyEmpl)
					}
				},
				recheckEmpls: function(){
					var compVm = this
					return $.debounce(500, false, function(){checkIfEmplAllowed(compVm)}) 
				},
				onClickAfterEmplSelectExpandBt: function(){return this.onClickAfterEmplSelectExpand.bind(this)}
			},
			methods:{
				onClickAfterEmplSelectExpand: function(e){
					var target = e.target
					if(!target.findElemByClass('empl-select-dd')){
						document.body.removeEventListener('click', this.onClickAfterEmplSelectExpandBt)
						this.isShowingEmplSelectDd = false
					}
				},
				onExpandEmplSelectClick: function(e){
					this.isShowingEmplSelectDd = true
					this.changeEmplDdTab = null
					var compVm = this
					var bRect = this.changeEmplButt.getBoundingClientRect()
					if(e.clientX > bRect.left + bRect.width - 50) this.changeEmplDdTab = 'search'
					document.body.removeEventListener('click', this.onClickAfterEmplSelectExpandBt)
					Vue.nextTick(function(){
						document.body.addEventListener('click', compVm.onClickAfterEmplSelectExpandBt)
					})
				},
				onClearSelectClick: function(){
					this.selectedEmpl = emptyEmpl
					this.onEmplChange( emptyEmpl )
				},
				onEmplChangeLocal: function(employee){
					this.selectedEmpl = employee
					this.onEmplChange( employee )
					document.body.removeEventListener('click', this.onClickAfterEmplSelectExpandBt)
					this.isShowingEmplSelectDd = false
				},
				openSelect: function(){
					var compVm = this
					Vue.nextTick(function(){
						$(compVm.$refs.comp_body.ae$('select')).data('select2').open()
					})
				},
			},
			watch:{
				shifts: function(){
					var shift = this.shifts[0]
					if(this.shouldCheckAvailableEmpls && shift.start_dtime !== this.prevStartDtime || shift.end_dtime !== this.prevEndDtime && shift.employee_id){
						// при смене времени проверяет, что выбранный в смене сотрудник все еще досупен
						this.onLoadingStart()
						this.recheckEmpls(this)
					}
					this.prevStartDtime =  shift.start_dtime
					this.prevEndDtime =  shift.end_dtime
				}
			}
		})
		var emptyEmpl = {id: 'none', text: 'Не задан'}
		var checkIfEmplAllowed = function(compVm){
			compVm.onLoadingStart()
			shift_assign.checkIfEmplAllowed(
				{shift: compVm.shifts[0]},
				function(r){
					compVm.onLoadingEnd()
					// если сотрудник больше не подходит, выбрать пустого
					var respEmpls = r.employees || []
					if(!respEmpls.length){
						if(compVm.shifts[0].employee_id != emptyEmpl.id) compVm.selectedEmpl = [emptyEmpl]
						compVm.warning = true
					}
				},
				function(r){handleError(r, compVm); compVm.onLoadingEnd()}
			)
		}
		var findSelectedEmpl = function(compVm){
			var shift = compVm.shifts[0]
			var firstSelectedEmplId = shift.employee ? shift.employee.id : 'none'
			var isEmplDiff = false
			var shiftEmployee = shift.employee ? shift.employee : emptyEmpl
			compVm.shifts.forEach(function(s){
				var sEmplEid = s.employee ? s.employee.id : 'none'
				if(!isEmplDiff && firstSelectedEmplId != sEmplEid) isEmplDiff = true
			})
			compVm.selectedEmployeeByUser = isEmplDiff ? [emptyEmpl] : [shiftEmployee]
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