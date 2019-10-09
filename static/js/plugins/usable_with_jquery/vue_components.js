VueComponents = {
	init: function(){
		this.compInits.forEach(function(ci) {
			ci()
		})
		//filters
		Vue.filter('fullDate', function(time){
			return new Date(time).dmy() +' '+ new Date(time).hm()
		})
		Vue.filter('timeDeltaHM', function(time){
			return Date.delta.hm(time)
		})
		Vue.filter('timeDeltaH', function(time){
			return Date.delta.h(time)
		})
	},
	compInits: [
		//select box
		function(){
			function selectOptions(select, selectedOptions, params){
				if( !selectedOptions || (selectedOptions && selectedOptions instanceof Array && !selectedOptions.length) ) {
					if( select.options.length && select.options[0].value == 'not-set') select.selectOption(select.options[0], true)
					return
				}
				if( typeof selectedOptions == 'Array')
					selectedOptions.map(function(o){ o.id && !o.value ? o.value = o.id : o })
					else
					selectedOptions.id && !selectedOptions.value ? selectedOptions.value = selectedOptions.id : false
				if( ~params.old.indexOf('multiselect') )
					select.selectOptions(selectedOptions, true)
					else
					select.selectOption(selectedOptions, true)
			}
			function getParams(comp){
				var params = comp.params || {}
				if( !params.old ) params.old = []
				if( !params.new ) params.new = {}
				if( !params.classes ) params.classes = []
				return params
			}
			Vue.component('vue-select-box', {
				name: 'vue-select-box',
				props: ['options', 'selected-options', 'params'],
				template: '#vp_selectbox',
				watch: {
					options: {
						handler: function(){
							var params = getParams(this)
							var select = this.$refs['selector-body']
							var opts = this.options || []
							opts.map(function(o){o.id && !o.value ? o.value = o.id : o})
							select.wipeOptions(true)
							select.addOptions(opts, true)
							selectOptions(select, this.selectedOptions, params)
						},
						deep: true
					},
					selectedOptions: {
						handler: function(){
							var params = getParams(this)
							var select = this.$refs['selector-body']
							selectOptions(select, this.selectedOptions, params)
						},
						deep: true
					},
					params:{
						handler: function(){
							// todo сделать адекватно
							var params = getParams(this)
							var select = this.$refs['selector-body']
							select.classList.toggle('disabled', ~params.old.indexOf('disabled'))
						},
						deep: true
					}
				},
				mounted: function () {
					var select = this.$refs['selector-body']
					var params = getParams(this)
					var opts = this.options || []
					opts.map(function(o){o.id && !o.value ? o.value = o.id : o})
					InitCustomSelect(select, params.old, params.new)
					select.addOptions(opts, true)
					selectOptions(select, this.selectedOptions, params)
					params.classes.forEach(function(c){select.classList.add(c)})
				}
			})
		},
		// date-select
		function(){
			function getParams(comp){
				var params = comp.params || {}
				if( !params.forInput ) params.forInput = {}
				if( !params.classes ) params.classes = []
				return params
			}
			Vue.component('vue-date-select', {
				name: 'vue-date-select',
				props: ['date', 'params', 'disabled'],
				template: '#vp_dateselect',
				watch: {
					params: {
						handler: function(){
							var params = getParams(this)
							var select = this.$refs['selector-body']
							select.setParams(params.forInput)
						},
						deep: true
					},
					date: {
						handler: function(){
							var select = this.$refs['selector-body']
							select.setDate(this.date, true)
						},
						deep: true
					},
					disabled: {
						handler: function(){
							var select = this.$refs['selector-body']
							select.disabled = this.disabled ? true : false
						},
						deep: true
					},
				},
				mounted: function () {
					var select = this.$refs['selector-body']
					var params = getParams(this)
					UI.DateInputWithDropdown(this.date, select, params.forInput)
					select.disabled = this.disabled ? true : false
					params.classes.forEach(function(c){select.classList.add(c)})
				}
			})
		},
		//date-interval-select
		function(){
			Vue.component('vue-date-interval-select', {
				name: 'vue-date-interval-select',
				props: ['date-from', 'date-to', 'params-from', 'params-to', 'disabled-from', 'disabled-to'],
				template: '\
<div class="date-range-wrap" ref="el-body">\
	<vue-date-select\
		:date="dateFrom"\
		:params="paramsFrom"\
		:disabled="disabledFrom"\
		v-on:change.native="onFromChange"\
	></vue-date-select>\
	<div class="separator">—</div>\
	<vue-date-select\
		:date="dateTo"\
		:params="paramsTo"\
		:disabled="disabledTo"\
		v-on:change.native="onToChange"\
	></vue-date-select>\
</div>',
				methods:{
					onFromChange: function(e){
						var date = e.target.getDate().getTime()
						this.$refs["el-body"].throwEvent('from-change', {date: date})
					},
					onToChange: function(e){
						var date = e.target.getDate().getTime()
						this.$refs["el-body"].throwEvent('to-change', {date: date})
					},
				},
				watch:{
					dateFrom: function(){
						if(this.dateFrom > this.dateTo)
							ViolationWarnings.showFor(this.$refs["el-body"].ae$('.date-input-with-dropdown'), {message: L10n.labels.valids.endBeforeStart})
					},
					dateTo: function(){
						if(this.dateFrom > this.dateTo) 
						ViolationWarnings.showFor(this.$refs["el-body"].ae$('.date-input-with-dropdown'), {message: L10n.labels.valids.endBeforeStart})
					},
				}
			})
		},
		// time-select
		function(){
			function getParams(comp){
				var params = comp.params || {}
				if( !params.forInput ) params.forInput = {}
				if( !params.classes ) params.classes = []
				return params
			}
			Vue.component('vue-time-select', {
				name: 'vue-time-select',
				props: ['time', 'params'],
				template: '\
				<div class="vue-time-select-wrap">\
					<div ref="selector-body"></div>\
				</div>\
				',
				watch: {
					params: {
						handler: function(){
							//todo
							return
							var params = getParams(this)
							var select = this.$refs['selector-body']
							select.setParams(params.forInput)
						},
						deep: true
					},
					time: {
						handler: function(){
							var select = this.$refs['selector-body']
							select.setTime(this.time, true)
						},
						deep: true
					},
				},
				mounted: function () {
					var select = this.$refs['selector-body']
					var params = getParams(this)
					aeTimeInputWithDropdown(this.time, select, params.forInput)
					params.classes.forEach(function(c){select.classList.add(c)})
					if(params.toolTip) new Tooltipable(select, params.toolTip, params.toolTipDelay || 500)
					addEventListener('custom-mousedown', function(){
						select.closePopup()
					})
				},
				beforeDestroy: function(){
					this.$refs['selector-body'].closePopup()
				},
			})
		},
		// mobilable table
		function(){
			Vue.component('vue-mobilable-table', {
				name: 'vue-mobilable-table',
				props: ['rows', 'params'],
				template: '#vp_mobilableTable',
				mounted: function () {
					MobilableTable.updateSizes(this.$refs['table-elem'])
				},
				updated: function () {
					var tableEl = this.$refs['table-elem']
					this.ae$nextTick(function () {
						MobilableTable.updateSizes(tableEl)
					})
				},
			})
		},
		// checkbox
		function(){
			Vue.component('vue-checkbox', {
				name: 'vue-checkbox',
				props: ['title', 'is-checked'],
				template: '\
<div class="vue-checkbox">\
	<i class="fa fa-square-o not-checked" v-if="!isChecked"></i>\
	<i class="fa fa-check-square-o checked" v-if="isChecked"></i>\
	<span v-if="title" v-text="title"></span>\
</div>'
			})
		},
		//loading screen
		function(){
			Vue.component('vue-loading-screen', {
				name: 'vue-loading-screen',
				props: ['target', 'message', 'type', 'heightUntil', 'messageColor', 'backgroundColor'],
				template: '<div class="vue-loading-screen" ref="el-body"></div>',
				data: function(){
					return{
						messageColor_local: this.messageColor || this.type == 'text' ? '#4a5266' : '',
						backgroundColor_local: this.backgroundColor || this.type == 'text' ? 'white' : '',
					}
				},
				mounted: function(){
					LoadingScreen.showFor(this.target, {
						message: this.message,
						messageColor: this.messageColor_local,
						backgroundColor: this.backgroundColor_local,
						heightUntil:  this.heightUntil
					})
				},
				destroyed: function(){
					LoadingScreen.hideFor(this.target)
				},
			})
		},
		//jq select
		function(){
			Vue.component('vue-jq-select', {
				name: 'vue-jq-select',
				props: ['options', 'selected-options', 'select-params', 'elem-params', 'on-change'],
				template: '<div> <select ref="select-body" :multiple="elemParams && elemParams.isMultiple"></select> </div>',
				data: function(){
					return {$select: null}
				},
				mounted: function(){
					var vm = this
					var $select = $(this.$refs['select-body'])
					this.$select = $select
					var selectParams = this.selectParams || {}
					this.oldOptions = this.options
					var selectParams = Object.assign({
						data: this.options,
						placeholder: 'Выберите вариант'
					}, selectParams)
					$select.select2(selectParams)
				
					$select.val(this.selectedOptionStrs).trigger('change')
					$select.on('change', function () {
						var newValue = $(this).val()
						if(!newValue && !vm.selectedOptions.length) return
						vm.onChange(newValue)
					})
				},
				beforeDestroy: function(){
					this.$select.select2('close')
				},
				data:function(){return{
					oldOptions: []
				}},
				computed:{
					selectedOptionStrs: function(){
						return (this.selectedOptions || []).map(function(o){return ''+(o? o.id : '')})
					}
				},
				watch: {
					options: function(){
						if(this.options.isEqualTo(this.oldOptions)) return
						this.oldOptions = this.options.slice()
						this.$select.empty()
						this.$select.select2({data: this.options})
						this.$select.val(this.selectedOptionStrs).trigger('change')
					},
					selectedOptionStrs: function(){
						var vals = this.selectedOptionStrs.simpleIniq() // убирает таинственное задваивание
						var currVals = [].concat(this.$select.val()) //потому что селект может вернуть одно значение, а может массив
						if(vals.isEqualTo(currVals)) return
						this.$select.val(vals).trigger('change')
					},
				}
			})
		},
		//jq timepicker
		function(){
			Vue.component('vue-jq-time-picker', {
				name: 'vue-jq-time-picker',
				props: ['dtime', 'on-change'],
				template: '\
				<div>\
					<div class="input-group timepicker">\
						<div class="input-group-prepend">\
							<span class="input-group-text">\
								<i class="la la-clock-o"></i>\
							</span>\
						</div>\
						<input class="form-control m-input" readonly="" ref="picker-body" placeholder="" type="text">\
					</div>\
				</div>',
				data: function(){
					return {$picker: null}
				},
				mounted: function(){
					var compVm = this
					var $picker = $(this.$refs['picker-body'])
					this.$picker = $picker
					$picker.timepicker({
						minuteStep: 15,
						defaultTime: this.dtime,
						showMeridian: false
					})
					$picker.on('change', function(){
						var timeStr = $(this).data("timepicker").getTime()
						var startDate = new Date(compVm.dtime).startOfDay()
						startDate.setHours(timeStr.split(':')[0])
						startDate.setMinutes(timeStr.split(':')[1])
						compVm.onChange(startDate.getTime())
					})
				},
				watch: {
					dtime: function(){
						this.$picker.timepicker('setTime', this.dtime);
					},
				}
			})
		},
		//jq date range picker
		function(){
			Vue.component('vue-jq-date-range-picker', {
				name: 'vue-jq-date-range-picker',
				props: ['start_dtime', 'end_dtime', 'min_dtime', 'on-change'],
				template: '\
				<div>\
					<div class="input-group">\
						<input type="text" class="form-control m-input input-date-range" readonly  placeholder="Select date range" ref="picker-body"/>\
						<div class="input-group-append">\
							<span class="input-group-text"><i class="la la-calendar-check-o"></i></span>\
						</div>\
					</div>\
				</div>',
				data: function(){
					return {$picker: null}
				},
				mounted: function(){
					var compVm = this
					var $picker = $(this.$refs['picker-body'])
					this.$picker = $picker
					$picker.daterangepicker({
						buttonClasses: 'm-btn btn',
						applyClass: 'btn-primary',
						cancelClass: 'btn-secondary',
						locale: dateRangePickerl10n,
						startDate: new Date(this.start_dtime).startOfDay(),
						endDate: new Date(this.end_dtime).startOfDay(),
						minDate: this.min_dtime == 'today' ? new Date().startOfDay() : this.min_dtime ? new Date(this.min_dtime) : null,
					}, function(start, end, label) {
						compVm.onChange(start, end)
					})
				},
				watch: {
					start_dtime: function(){
						this.$picker.data('daterangepicker').setStartDate(new Date(this.start_dtime))
					},
					end_dtime: function(){
						this.$picker.data('daterangepicker').setEndDate(new Date(this.end_dtime))
					},
					min_dtime: function(){ 
						console.warn('No watcher for min_dtime change in <vue-jq-date-range-picker>. Plugin doesnt support this')
					}
				}
			})
		},
		//days line
		function(){
			Vue.component('vue-days-line', {
				name: 'vue-days-line',
				props: ['start_dtime', 'zoom-mode', 'is-readonly', 'on-zoom-select-change',
							 'on-day-click', 'selected-dtimes'],
				template: '\
				<div class="days-line" :class="zoomMode != \'month\' ? \'\' : \'clickable\' ">\
					<div class="hor-flex-parent" v-if="zoomMode == \'day\' ">\
					</div>\
					<div class="hor-flex-parent" v-if="zoomMode == \'week\' ">\
						<div class="item hor-flex-child-long"\
							v-for="day in daysInWeek"\
							:key="day.start_dtime"\
							:style="day.cssWidth"\
							:class="{\
								\'selected\': selectedDtimes && ~selectedDtimes.indexOf(day.start_dtime)\
							}"\
							@click="onDayClickLocal(day.start_dtime)"\
							>\
							<div class="label">\
								<b v-text="day.label"></b>\
								<span v-text="day.dates"></span>\
							</div>\
							<div class="hor-flex-parent sline">\
								<div class="hor-flex-child-long sline-label-mid">утро</div>\
								<div class="hor-flex-child-long sline-label-mid">день</div>\
								<div class="hor-flex-child-long sline-label-mid">вечер</div>\
							</div>\
						</div>\
					</div>\
					<div class="hor-flex-parent" v-if="zoomMode == \'month\' ">\
						<div class="item hor-flex-child-long ver-flex-parent" v-for="week in weeksInMonth" :style="{width: week.cssWidth}">\
							<div class="label ver-flex-child-long" @click="onWeekClickLocal(week.number)">\
								<b v-text="week.label"></b>\
								<span v-text="week.isoNumber"></span>\
							</div>\
							<div class="hor-flex-parent sline ver-flex-child-long">\
								<div class="hor-flex-child-long sline-label-mid item"\
									v-for="day in week.days"\
									:key="day.start_dtime"\
									v-text="day.label" \
									:class="{\
										\'selected\': selectedDtimes && ~selectedDtimes.indexOf(day.start_dtime)\
									}"\
									@click="onDayClickLocal(day.start_dtime)"\
								></div>\
							</div>\
						</div>\
					</div>\
				</div>\
				',
				computed: {
					weeksInMonth: function(){
						var start_dtime = this.start_dtime
						var end_dtime = new Date(start_dtime).setMonth(new Date(start_dtime).getMonth()+1)- 1..day
						var weeks = []
						var count = 0
						var daysInMonth = (end_dtime - start_dtime) / 1..day
						for(var i = start_dtime; i<=end_dtime; start_dtime += 7..day){
							var startDay = Date.fixDay(new Date(i).getDay())
							var wStartDate = i
							var wEndDate = wStartDate + (7-startDay-1)*1..day
							if(wEndDate > end_dtime) wEndDate = end_dtime
							var daysInWeek = (wEndDate - wStartDate) / 1..day + 1
							var week = {
								start_dtime: startDay,
								isCurrent: startDay == new Date().startOfWeek().getTime(),
								label: daysInWeek < 3 ? 'Н' : 'Неделя',
								isoNumber: new Date(wStartDate).getISOWeekNumber(),
								number: count,
								days: []
							}
							for(var d = 0; d < daysInWeek; d++){
								var date = wStartDate + d*1..day
								week.days.push({
									start_dtime: date,
									label: new Date(date).getDate(),
								})
							}
							week.cssWidth = 100 / daysInMonth * week.days.length + '%'
							weeks.push(week)
							i = wEndDate + 1..day
							count++
						}
						return weeks
					},
					daysInWeek: function(){
						var start_dtime = this.start_dtime
						var dayNames = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"] //todo l10n
						dayNames = dayNames.map(function(n){return n.toLowerCase()})
						var realCurrDayStartDtime = new Date().startOfDay().getTime()
						var days = []
						for(var i=0; i<7; i++){
							var date = new Date(start_dtime + (24..hours)*i)
							days.push({
								isCurrent: date.getTime() == realCurrDayStartDtime,
								label: dayNames[i],
								dates: date.getDate().toLen(2) + '.' + (date.getMonth()+1).toLen(2),
								cssWidth: 100 / 7 + '%',
								number: i,
								start_dtime: date.getTime()
							})
						}
						return days
					},
				},
				methods: {
					onWeekClickLocal: function(weekNum){
						this.onZoomSelectChange ? this.onZoomSelectChange('week') : null
						throwEvent('interval:call:zoomSwitch', {zoomMode: 'week'})
						throwEvent('interval:call:weekSwitch', {weekNum: weekNum})
					},
					onDayClickLocal: function(dayNum){
						this.onDayClick && this.onDayClick(dayNum)
					}
				},
			})
		}
	]
}
document.addEventListener("DOMContentLoaded", function(event) {
	VueComponents.init()
})