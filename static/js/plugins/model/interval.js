Model.interval = {
	year: 0,
	start_dtime: 0,
	end_dtime: 0,
	weeks_number: 0,
	get duration(){
		return this.end_dtime - this.start_dtime
	},

	week: {
		number: 0,
		start_dtime: 0,
		end_dtime: 0,
		get duration(){ return this.end_dtime - this.start_dtime },
	},

	month: {
		number: 0,
		get start_dtime(){ return new Date(Model.interval.year, this.number, 1).getTime() },
		get end_dtime(){ return new Date(Model.interval.year, this.number+1, 1).getTime() },
		get duration(){ return this.end_dtime - this.start_dtime },
		toString: function(){ return Model.interval.year +'-'+ (this.number+1).toLen(2) }
	},

	init: function() {
		if (Model.DEBUG) {
			this.switchToYearMonth(2015, 7)
		} else {
			var now = new Date()
			var year = now.getFullYear()
			var month = now.getMonth()
			var week = (now.getDate() + now.startOfMonth().getISODay()-1) / 7 |0
			// var year = Model.settings.get('app:year', now.getFullYear())
			// var month = Model.settings.get('app:month', now.getMonth())
			// var week = Model.settings.get('app:week', (now.getDate() + now.startOfMonth().getISODay()-1) / 7 |0)
			this.switchAll(year, month, week)
		}
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
		this.weeks_number = Model.interval.duration / Date.week

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
		this.week.start_dtime = Model.interval.start_dtime + Date.week*week
		this.week.end_dtime = Model.interval.week.start_dtime + Date.week
		throwEvent('interval:week:switch', {monthChanged: monthChanged})
	}
}
