var saShiftEditMix = {
	methods:{
		onEditStart: function(){
			this.isLoading = true
		},
		onEditSuccess: function(r, isNoGenerate){
			this.editShiftData = null
			var newRawShiftsData = cloneViaJSON(this.rawShiftsData)
			var editedShifts = r.map(function(s){return new Shift(s)})
			editedShifts.forEach(function(s){
				// для каждой пришедшей смены
				// заменить старую смену, если такая была
				var used = false
				newRawShiftsData = newRawShiftsData.map(function(os){
					if(os.id != s.id) return os
					used = true
					return s
				})
				if(used) return s
				// иначе добавить смену в массив
				newRawShiftsData.push(s)
			})
			// удалить все смены с отрицательным айди
			newRawShiftsData = newRawShiftsData.filter(function(s){
				return s.id > 0
			}).map(function(s){return new Shift(s)})
			this.rawShiftsData = newRawShiftsData
			if(!isNoGenerate) this.compWrap.generate()
		},
		onDeleteSuccess: function(shifts){
			this.editShiftData = null
			var deletedSids = shifts.map(function(s){return s.id})
			var newRawShiftsData = cloneViaJSON(this.rawShiftsData)
			newRawShiftsData = newRawShiftsData.filter(function(s){
				return !~deletedSids.indexOf(s.id)
			}).map(function(s){return new Shift(s)})
			this.rawShiftsData = newRawShiftsData
			this.compWrap.generate()
		},
		onEditError: function(){
			this.isLoading = false
		},
		onExitMassActions: function(){
			this.clearHighlightRowsUnderZone()
		},
		onExitShiftSelection: function(){
			this.editShiftData = null
			this.editAvailData = null
			this.isCopyToFuture = false
			this.higlightedShifts = []
			this.higlightedDayCodes = []
			this.higlightedDayCodesCopyToPresent = []
			this.removeHoverSelectionFromDayAndRows()
		},
	}
}