var copyToPresentMix = {
	data: function(){return{
		isCopyInPresent: false,
		shiftsToRemove: [],
		rawShiftsDataBackup: [],
	}},
	computed:{
		shortCutStartCopyToPresentBt: function(){
			return this.shortCutStartCopyToPresent.bind(this)
		},
		shortCutApplyCopyToPresentBt: function(){
			return this.shortCutApplyCopyToPresent.bind(this)
		} 
	},
	methods:{
		shortCutApplyCopyToPresent: function(e){
			// v-key is 86
			// esc is 27
			if(e.ctrlKey && e.keyCode == 86) this.applyCopyToPresent()
			if(e.keyCode == 27) this.exitCopyToPresent()
		},
		shortCutStartCopyToPresent: function(e){
			// c-key is 67
			// ctrl-c
			if(e.ctrlKey && e.keyCode == 67) this.startCopyToPresent()
			// if(!this.isCopyInPresent) return
		},
		startCopyToPresent: function(){
			this.isCopyInPresent = true
			addEventListener('keydown', this.shortCutApplyCopyToPresentBt)
		},
		applyCopyToPresent: function(){
			this.createNewShiftsToPresent()
			this.compWrap.generate()
			this.massAddAndDeleteShifts(
				this.rawShiftsData.filter(function(s){return s.id < 0}),
				this.shiftsToRemove.filter(function(s){return s.id > 0})
			)
			this.isCopyInPresent = false
			this.shiftsToRemove = []
			removeEventListener('keydown', this.shortCutApplyCopyToPresentBt)
			this.onExitShiftSelection()
		},
		exitCopyToPresent: function(withoutUpdate){
			this.isCopyInPresent = false
			this.closeAllMassEditChildFrames()
			this.shiftsToRemove = []
			this.higlightedShifts = []
			this.rawShiftsData = this.rawShiftsDataBackup.slice()
			if(!withoutUpdate) this.compWrap.generate()
			this.removeHoverSelectionFromDayAndRows()
			removeEventListener('keydown', this.shortCutApplyCopyToPresentBt)
			this.onExitShiftSelection()
		},
		removeAllSelections: function(){
			this.removeHoverSelectionFromDayAndRows()
			this.clearZoneSelection()
			this.onExitShiftSelection()
		},
		removeHoverSelectionFromDayAndRows: function(){
			// убирает выделение с правой части строк и дней в полоске дней
			this.hoveredDayLineDtimes = []
			this.selectedURowCodes = []
		},
		createNewShiftsToPresent: function(){
			var newShifts = []
			var shiftsToRemove = []

			// сколько дней-строчек в копируемой области
			var highlightedDays = []
			var compVm = this
			this.forEachDay(function(d){
				if(~compVm.higlightedDayCodes.indexOf(d.code)) highlightedDays.push(d)
			})
			var selectedDaysInRowLength = 0
			var selectedUrowsLength = 0
			// посчитать количество строк и дней в строках выделено
			var fdcd = this.parseDayCode(highlightedDays[0]) // firstDayCodeData
			// этот хвостик должен быть одинаков у всех дней внутри строчки [firstDayCodeData.area_id, firstDayCodeData.organization_id, firstDayCodeData.urow_index ]
			highlightedDays.forEach(function(d){
				var dcd = compVm.parseDayCode(d)
				if(
					dcd.area_id == fdcd.area_id &&
					dcd.organization_id == fdcd.organization_id &&
					dcd.urow_index == fdcd.urow_index
					) selectedDaysInRowLength ++
			})
			selectedUrowsLength = highlightedDays.length / selectedDaysInRowLength
			
			// сколько дней-строчек в целевой области 
			var daysToCopy = []
			this.forEachDay(function(d){
				if(~compVm.higlightedDayCodesCopyToPresent.indexOf(d.code)) daysToCopy.push(d)
			})
			var targetDaysInRowLength = 0
			var targetUrowsLength = 0
			// посчитать количество строк и дней в строках выделено
			var fdcd = this.parseDayCode(daysToCopy[0]) // firstDayCodeData
			// этот хвостик должен быть одинаков у всех дней внутри строчки [firstDayCodeData.area_id, firstDayCodeData.organization_id, firstDayCodeData.urow_index ]
			daysToCopy.forEach(function(d){
				var dcd = compVm.parseDayCode(d)
				if(
					dcd.area_id == fdcd.area_id &&
					dcd.organization_id == fdcd.organization_id &&
					dcd.urow_index == fdcd.urow_index
					) targetDaysInRowLength ++
			})
			targetUrowsLength = daysToCopy.length / targetDaysInRowLength

			// удалить старые смены
			daysToCopy.forEach(function(d, index){
				if(compVm.isDayReadonly(d)) return
				if(d.shifts.length) shiftsToRemove = shiftsToRemove.concat(d.shifts)
				var refDay = findRefDay(index)
				var protShifts = refDay.shifts
				var ddata = compVm.parseDayCode(d)

				protShifts.forEach(function(ps){
					var newShift = new Shift(ps, {isNewId: true})
					newShift.organization_id = ddata.organization_id,
					newShift.area_id = ddata.area_id,
					newShift.agency_id = ddata.agency_id,
					newShift.urow_index = ddata.urow_index

					var shiftParentDayDate = new Date(newShift.start_dtime).startOfDay().getTime()
					var delta = ddata.start_dtime - shiftParentDayDate
					newShift.move(delta)
					newShifts.push(newShift)
				})
			})
			if(shiftsToRemove.length) ViolationWarnings.showFor(null, {message: 'Будет удалено '+ shiftsToRemove.length +' смен'})
			var shiftToRemoveIds = shiftsToRemove.map(function(s){return s.id})
			this.shiftsToRemove = shiftsToRemove
			this.rawShiftsData = this.rawShiftsData.slice().concat(newShifts).filter(function(s){return !~shiftToRemoveIds.indexOf(s.id)})

			function findRefDay(index){
				var sdayNum = (index % targetDaysInRowLength) % selectedDaysInRowLength
				var srowNum = (index/targetDaysInRowLength|0) % selectedUrowsLength
				return highlightedDays[ sdayNum + srowNum * selectedDaysInRowLength]
			}
		},
		closeAllMassEditChildFrames: function(){
			this.isCopyToFuture = false
		}
	}
}