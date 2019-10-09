page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-empl-select-dd', {
			name: 'sa-empl-select-dd',
			props: ['shifts', 'compWrap', 'onEmplSelect', 'targetEl', 'selectTab'],
			template: '\
				<div class="empl-select-dd" ref="comp_body" :style="{left: leftCss, top: topCss}">\
					<div role="group" class="btn-group btn-group-sm empl-filter-select">\
						<button type="button" class="btn" :class="emplsFilter == \'main\' ? \'btn-primary\' : \'btn-secondary\'" @click="onChangeEmplsFilterClick(\'main\')">Основные</button>\
						<button type="button" class="btn" :class="emplsFilter == \'all\' ? \'btn-primary\' : \'btn-secondary\'"   @click="onChangeEmplsFilterClick(\'all\')"  >Все</button>\
						<button type="button" class="btn" :class="emplsFilter == \'search\' ? \'btn-primary\' : \'btn-secondary\'"   @click="onChangeEmplsFilterClick(\'search\')"  ><i class="fa fa-search"></i></button>\
					</div>\
					<div class="inner">\
						<template v-if="emplsFilter == \'search\'">\
							<input class="form-control m-input search-input" autofocus="true" placeholder="Поиск по сотрудникам" name="schedule-empl-search" v-model="searchQuery" @keyup.enter="doForceSearch" :disabled="isEmplsLoading"></input>\
							<i class="fa fa-search search-input-icon"></i>\
							<div class="errow-row" style="opacity: 0.5" v-if="showNoResultsLabel">\
								<span>Ничего не найдено</span>\
							</div>\
						</template>\
						<div class="loading-rotator" v-if="isEmplsLoading"><i class="fa fa-spinner fa-spin m--font-primary"></i></div>\
						<div class="errow-row m--font-danger" v-if="error">\
							<span v-text="error.message"></span>\
						</div>\
						<div class="empl"\
							v-if="!isEmplsLoading"\
							v-for="empl in employees"\
							@click="empl.selectable && onEmplSelectLocal(empl)"\
							:class="{\
								\'selected\': selectedEmployeeByUser && selectedEmployeeByUser.id == empl.id,\
								\'disabled\': !empl.selectable,\
							}"\
						>\
							<div class="empl-text" v-text="empl.text"></div>\
							<div class="empl-viol" v-if="empl.city" v-text="empl.city"></div>\
							<div class="empl-viol" v-if="empl.violation_text" v-text="empl.violation_text"></div>\
						</div>\
					</div>\
					<button type="button" class="btn btn-success btn-sm apply-butt" :disabled="!isSaveAllowed" @click="onEmplSelect(selectedEmployeeByUser)">Применить</button>\
				</div>\
			',
			data: function(){return{
				isEmplsLoading: true,
				employees: [],
				selectedEmployeeByUser: null,
				error: null, 
				topCss: 0,
				leftCss: 0,
				minSearchSize: 3,
				isSaveAllowed: false,
				emplsFilter: this.selectTab || 'main',
				searchQuery: '',
				showNoResultsLabel: false,
			}},
			methods:{
				onChangeEmplsFilterClick: function(newFilter){
					this.emplsFilter = newFilter
					if(newFilter != 'search')
						loadEmpls(this)
						else
						this.employees = []
				},
				onCallEmplLoading: function(){
					loadEmpls(this)
				},
				onClearSelectClick: function(){
					this.selectedEmployeeByUser = [emptyEmpl]
				},
				onEmplSelectLocal: function(empl){
					this.selectedEmployeeByUser = empl
					this.isSaveAllowed = true
				},
				doSearch: function(){
					var compVm = this
					if(!compVm.searchQuery || compVm.searchQuery.length < compVm.minSearchSize) {
						compVm.searchResults = []
						return
					}
					this.doForceSearch()
				},
				doForceSearch: function(){
					var compVm = this
					if(!compVm.searchQuery) {
						compVm.searchResults = []
						return
					}
					this.isEmplsLoading = true
					this.error = null
					compVm.compWrap.loadEmplsForShift(
						{
							shift: compVm.shifts[0],
							tab: 'all',
							search: this.searchQuery
						},
						function(r){
							var respEmpls = r.employees || []
							compVm.employees = respEmpls
							compVm.isEmplsLoading = false
							if(!respEmpls.length){
								compVm.showNoResultsLabel = true
							}
						}, function(r){
							handleError(r, compVm)
							compVm.isEmplsLoading = false
						}
					)
				}
			},
			watch:{
				searchQuery: function(){
					this.showNoResultsLabel = false
					// this.doSearch()
				}
			},
			mounted: function(){
				if(this.emplsFilter != 'search') 
					loadEmpls(this)
					else
					this.isEmplsLoading = false
				var ddBody = this.$refs.comp_body
				var targetEl = this.targetEl
				var pos = calcPosForDropDown(targetEl.getBoundingClientRect(), ddBody.getBoundingClientRect())
				this.leftCss = pos.left + 'px'
				this.topCss = pos.top + 'px'
			}
		})
		var emptyEmpl = {id: 'none', text: 'Не задан', selectable: true}
		var loadEmpls = function(compVm){
			compVm.isEmplsLoading = true
			compVm.error = null
			var shift = compVm.shifts[0]
			compVm.compWrap.loadEmplsForShift(
				{
					shift: shift,
					tab: compVm.emplsFilter
				},
				function(r){
					compVm.isEmplsLoading = false
					var respEmpls = r.employees || []
					var epls = []
					epls = epls.concat(emptyEmpl)
					epls = epls.concat(respEmpls)
					compVm.employees = epls.uniqByKey('id')
					findSelectedEmpl(compVm)
				}, function(r){
					handleError(r, compVm)
					compVm.isEmplsLoading = false
					var epls = []
					epls = epls.concat(emptyEmpl)
					compVm.employees = epls.uniqByKey('id')
					findSelectedEmpl(compVm)
				}
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