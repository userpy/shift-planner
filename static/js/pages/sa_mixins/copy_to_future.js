var copyToFutureMix = {
	data: function(){return{
		isCopyToFuture: false
	}},
	methods:{
		startCopyToFuture: function(){
			this.isCopyToFuture = true
		},
		exitCopyToFuture: function(){
			this.isCopyToFuture = false
		},
		getSelectedWeekStart: function(){
			var shifts = this.higlightedShifts
			shifts.sort(function(a,b){return a.start_dtime - b.start_dtime})
			var lastShift = new Shift(shifts[0])
			return new Date(lastShift.start_dtime).startOfWeek().getTime()
		},
		applyCopyToFuture: function(start_dtime, end_dtime){
			var end_dtime = new Date(new Date(end_dtime).setHours(23)).setMinutes(59)
			var shifts = this.higlightedShifts
			var newShifts = []
			//создать количество смен, явно перекрывающее выбранный интервал
			var hugeIntervalStart = new Date(start_dtime).startOfWeek().getTime()
			var hugeIntervalEnd = new Date(end_dtime + 1..week).startOfWeek().getTime()
			var weeksInHInterval = (hugeIntervalEnd - hugeIntervalStart) / 1..week
			var deltaWeeks = (hugeIntervalStart - this.getSelectedWeekStart()) / 1..week // через столько недель начинается выбранный интервал
			for(var i = 0; i < weeksInHInterval; i++){
				//создать пачку смен со сдвигом
				var ss = shifts.slice().map(function(s){
					var newShift = new Shift(s, {isNewId: true})
					//добавить к смене сдвиг до выбранного интервала и количество недель в интервале
					var delta = (deltaWeeks + i) * 1..week
					newShift.move(delta)
					return newShift
				})
				newShifts = newShifts.concat(ss)
			}
			//выкинуть смены, которые выходят за рамки интервала
			newShifts = newShifts.filter(function(s){
				return s.start_dtime > start_dtime && s.start_dtime < end_dtime
			})
			this.isLoading = true
			this.isCopyToFuture = false
			var compVm = this
			var compWrap = this.compWrap
			this.compWrap.massAddOrEditShifts(
				{shifts: newShifts, isOverwrite: false, isAdding: true}, 
				function(){ compVm.isLoading = false; compWrap.loadAndGenerate()}, 
				function(){ compVm.isLoading = false /*todo on err*/}
			)
		},
	}
}