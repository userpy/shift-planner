var topDateChanger = new function(){
	var storageKey = 'group_topDateChanger_'+ request_page_party +'_'
	var topDateChanger = this
	var vm
	this.init = function(){
		interval.init()
		var initialData = {
			start_dtime: interval.selected_start_dtime,
			zoomMode: interval.zoom_mode,
			zoomOptions: [{text: 'Неделя', id: 'week'}, {text: 'Месяц', id: 'month'}],
			mode: date_changer_mode,
		}
		vm = new Vue({
			el: '.top-date-changer-nest',
			template: '\
				<div class="date-switcher">\
					<div class="btn-group m-btn-group" role="group">\
						<div class="btn btn-secondary radius-left interval-prev-btn" @click="onPrevNextIntervalClick(\'prev\')"> <i class="fa fa-caret-left"></i> </div>\
						<input class="month-select form-control" id="date_switcher_ym_select">\
						<button type="button" \
							v-if="zoomMode != \'month\'"\
							v-for="btn, index in weekButts" \
							class="btn" \
							:class="{\'btn-primary\': btn.isSelected, \'btn-secondary\': !btn.isSelected, \'radius-left\': index == 0, \'radius-right\': index == weekButts.length}" \
							v-text="btn.label" \
							@click="onWeekClick(btn.number)"\
						></button>\
						<div \
							class="btn btn-secondary radius-left interval-next-btn"\
							@click="onPrevNextIntervalClick(\'next\')" \
							:style="{\'margin-left\': zoomMode == \'month\' ? \'-5px!important\' : \'bla\'}"\
							> <i class="fa fa-caret-right"></i> </div>\
					</div>\
					<div class="zoom-select">\
						<vue-jq-select\
							:options="zoomOptions"\
							:selected-options="selectedZoomOptions"\
							:on-change="onZoomSelectChange"\
						></vue-jq-select>\
					</div>\
				</div>\
			',
			data: initialData,
			computed: {
				weekButts: function(){
					var start_dtime = this.start_dtime
					var data = []
					for(var weekNum = 0; weekNum < interval.weeks_number; weekNum++){
						var start_date = new Date(interval.start_dtime + weekNum.weeks)
						var end_date = new Date(interval.start_dtime + (weekNum+1).weeks - 1)
						data.push({
							isSelected: interval.week.number == weekNum,
							label: ''+
								(start_date.getDate()).toLen(2)  +'.'+ (start_date.getMonth()+1).toLen(2) +'–'+
								(end_date.getDate()).toLen(2)    +'.'+ (end_date.getMonth()+1).toLen(2),
							number: weekNum
						})
					}
					return data
				},
				selectedZoomOptions: function(){
					return [{id: this.zoomMode}]
				}
			},
			mounted: function(){
				$('#date_switcher_ym_select').datepicker({
					format: 'MM yyyy',
					autoclose: true,
					startView: 1,
					minViewMode: 1,
					maxViewMode: 2,
					clearBtn: true,
					language: 'ru',
				})
				$('#date_switcher_ym_select').datepicker('setDate', new Date(interval.month.start_dtime))
				$('#date_switcher_ym_select').on('change', this.onYMSelectChange)
				var compVm = this
				addEventListener('interval:week:switch', function(e){
					compVm.start_dtime = compVm.zoomMode == 'week' ? interval.week.start_dtime : interval.month.start_dtime
				})
			},
			methods: {
				onZoomSelectChange: function(zoomMode){
					this.zoomMode = zoomMode
					this.start_dtime = zoomMode == 'week' ? interval.week.start_dtime : interval.month.start_dtime
					interval.zoom_mode = zoomMode
					localStorage.setItem(storageKey +'zoomMode', zoomMode)
					throwEvent('interval:zoom:change', {zoom_mode: zoomMode})
				},
				onWeekClick: function(weekNum){
					interval.switchToWeek(weekNum)
				},
				onYMSelectChange: function(e){
					var date = $('#date_switcher_ym_select').data('datepicker').getDate()
					interval.switchToYearMonth(date.getFullYear(), date.getMonth())
				},
				onPrevNextIntervalClick: function(dir){
					if(this.zoomMode == 'week')
						switchToWeek(dir)
						else
						switchToMonth(dir)
				}
			},
			watch:{
				start_dtime: function(){
					$('#date_switcher_ym_select').datepicker('setDate', new Date(interval.month.start_dtime))
				}
			}
		})
	}
	var switchToWeek = function(dir){
		if(dir == 'next'){
			//вперед
			var week = interval.week.number + 1
			if(week >= interval.weeks_number) {
				var switch_year = interval.month.number==11 ? (interval.year+1) : interval.year
				var switch_month = interval.month.number==11 ? 0 : interval.month.number+1
				function weekFunc(){
					return new Date(interval.start_dtime).getDate()==1 ? 0 : 1
				}
				interval.switchAll(switch_year, switch_month, weekFunc)
			} else {
				interval.switchToWeek(week)
			}
		}else{
			//назад
			var week = interval.week.number - 1
			if(week<0) {
				var switch_year = interval.month.number==0 ? (interval.year-1) : interval.year
				var switch_month = interval.month.number==0 ? 11 : interval.month.number-1
				function weekFunc(){
					var firstDay = new Date(interval.year, interval.month.number + 1, 1, 12)
					return interval.weeks_number - (firstDay.getDay()==1 ? 1 : 2)
				}
				interval.switchAll(switch_year, switch_month, weekFunc)
			} else {
				interval.switchToWeek(week)
			}
		}
	}
	var switchToMonth = function(dir){
		if(dir == 'next'){
			var switch_month = interval.month.number==11 ? 0 : interval.month.number+1
			var switch_year = interval.month.number==11 ? (interval.year+1) : interval.year
			function weekFunc(){
				return new Date(interval.start_dtime).getDate()==1 ? 0 : 1
			}
			interval.switchAll(switch_year, switch_month, weekFunc)
		}else{
			var switch_month = interval.month.number==0 ? 11 : interval.month.number-1
			var switch_year = interval.month.number==0 ? (interval.year-1) : interval.year
			function weekFunc(){
				var firstDay = new Date(interval.year, interval.month.number + 1, 1, 12)
				return interval.weeks_number - (firstDay.getDay()==1 ? 1 : 2)
			}
			interval.switchAll(switch_year, switch_month, weekFunc)
		}
	}
	this.interval = new function(){return {
			year: 0,
			start_dtime: 0,
			end_dtime: 0,
			weeks_number: 0,
			get duration(){
				return this.end_dtime - this.start_dtime
			},
			get selected_start_dtime(){
				return this.zoom_mode == 'week' ? this.week.start_dtime : this.month.start_dtime
			},
			get selected_end_dtime(){
				return this.zoom_mode == 'week' ? this.week.end_dtime : this.month.end_dtime
			},
			get selected_month(){
				var now = new Date()
				var month = now.getMonth()
				var localMonth = +localStorage.getItem(storageKey +'app:month')
				if(localMonth === 0 || localMonth > 0) month = localMonth
				return month
			},
			get selected_month_start_dtime(){
				var now = new Date()
				var month = this.selected_month
				return now.startOfMonth().setMonth(month)
			},
		
			week: {
				number: 0,
				start_dtime: 0,
				end_dtime: 0,
				get duration(){ return this.end_dtime - this.start_dtime },
			},
		
			month: {
				number: 0,
				get start_dtime(){ return new Date(interval.year, this.number, 1).getTime() },
				get end_dtime(){ return new Date(interval.year, this.number+1, 1).getTime() },
				get duration(){ return this.end_dtime - this.start_dtime },
				toString: function(){ return interval.year +'-'+ (this.number+1).toLen(2) }
			},
		
			init: function() {
				var now = new Date()

				var year =  +localStorage.getItem(storageKey +'app:year')  || now.getFullYear()

				var month = now.getMonth()
				var localMonth = +localStorage.getItem(storageKey +'app:month')
				if(localMonth === 0 || localMonth > 0) month = localMonth

				var week = ((now.getDate() + now.startOfMonth().getISODay()-1) / 7 |0)
				var localWeek = +localStorage.getItem(storageKey +'app:week')
				if(localWeek === 0 || localWeek > 0) week = localWeek
				
				this.zoom_mode = localStorage.getItem(storageKey +'zoomMode') || 'week'
				if(date_changer_mode == 'month') this.zoom_mode = 'month'
				this.switchAll(year, month, week)
			},
		
			// Переключает год, месяц и неделю разом.
			// В качестве недели может быть функция, она будет вызвана после
			// обновления года, месяца, границ месяца и кол-ва недель,
			// и должна будет вернуть номер недели (на случай,
			// если это номер как-то вычисляет из границ интервала).
			switchAll: function(year, month, week, force) {
				// if (Model.data.modified && !force) throw new Error('trying to switch month while changes are not saved')
				if (month == null) month = this.month.number
				if (year == null) year = this.year
				if (week == null) week = this.week.number
		
				var start = new Date(year, month, 1).startOfWeek()
				var end = new Date(year, month+1, 7).startOfWeek()

				this.year = year
				this.month.number = month
				this.start_dtime = start.getTime()
				this.end_dtime = end.getTime()
				this.weeks_number = interval.duration / Date.week

				localStorage.setItem(storageKey +'app:year', year)
				localStorage.setItem(storageKey +'app:month', month)

				throwEvent('interval:full:switch')
				if (typeof week == 'function') week = week()
				this._switchToWeek(Math.min(Math.max(0, week), this.weeks_number-1), true)
			},
		
			switchToYearMonth: function(year, month, force) {
				this.switchAll(year, month, null, force)
			},
		
			switchToWeek: function(week){
				this._switchToWeek(week, false)
			},
			_switchToWeek: function(week, monthChanged){
				this.week.number = week
				this.week.start_dtime = interval.start_dtime + Date.week*week
				this.week.end_dtime = interval.week.start_dtime + Date.week
				localStorage.setItem(storageKey +'app:week', week)
				throwEvent('interval:week:switch', {monthChanged: monthChanged})
			}
		}
	}()
	var interval = this.interval

	addEventListener('interval:call:zoomSwitch', function(e){
		var zoomMode = e.detail.zoomMode
		vm.onZoomSelectChange(zoomMode)
	})
	addEventListener('interval:call:weekSwitch', function(e){
		var weekNum = e.detail.weekNum
		vm.onWeekClick(weekNum)
	})

}()
document.addEventListener("DOMContentLoaded", function(event) {
	topDateChanger.init()
})