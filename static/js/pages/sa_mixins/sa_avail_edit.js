var saAvailEditMix = {
	data: function(){return{
		optsForModeSelect:[
			{id: 'outsource', text: 'Аутсорсинг'},
			{id: 'promo', text: 'Промоутеры'},
			{id: 'broker', text: 'Брокеры'},
		],
	}},
	computed:{
		selectedModeOpt: function(){
			return [{id: this.currWorkMode}]
		},
		isAvailSelectionMode: function(){
			return (this.currWorkMode == 'promo' || this.currWorkMode == 'broker') && this.higlightedDayCodes.length
		},
		isAvailSelectionEnabled: function(){
			return this.currWorkMode == 'promo' || this.currWorkMode == 'broker'
		},
		isAnyAvailInZone: function(){
			var dayCodesD = this.higlightedDayCodes.map(this.parseDayCode)
			var aaoHash = {}
			var rawAvailsData = this.rawAvailsData
			dayCodesD.forEach(function(dcd){
				aaoHash[dcd.area_id +'**'+ dcd.agency_id +'**'+ dcd.organization_id] = dcd
			})
			var startEnd = this.getAvailSelectionStartEnd(dayCodesD)
			var start_dtime = startEnd.start_dtime
			var end_dtime = startEnd.end_dtime

			var isAnyAvailInZone = false
			Object.keys(aaoHash).forEach(function(k){
				var dcd = aaoHash[k]
				rawAvailsData.forEach(function(av){
					if(isAnyAvailInZone) return
					if ((av.end_dtime >= start_dtime && av.start_dtime < end_dtime) &&
									 av.agency_id == dcd.agency_id && 
									 av.area_id == dcd.area_id && 
									 av.organization_id == dcd.organization_id
									 ){
						isAnyAvailInZone = true
					}
				})
			})
			return isAnyAvailInZone
		}
	},
	methods: {
		getAvailSelectionStartEnd: function(dayCodesD){
			var dayCodesD = dayCodesD || this.higlightedDayCodes.map(this.parseDayCode)
			// посчитать количество строк и дней в строках выделено
			var fdcd = dayCodesD[0] // firstDayCodeData
			// этот хвостик должен быть одинаков у всех дней внутри строчки [firstDayCodeData.area_id, firstDayCodeData.organization_id, firstDayCodeData.urow_index ]
			var targetDaysInRowLength = 0
			dayCodesD.forEach(function(dcd){
				if(
					dcd.area_id == fdcd.area_id &&
					dcd.organization_id == fdcd.organization_id &&
					dcd.urow_index == fdcd.urow_index
					) targetDaysInRowLength ++
			})
			var start_dtime = dayCodesD[0].start_dtime
			var end_dtime = start_dtime + Date.day * (targetDaysInRowLength - 1)
			return {
				start_dtime: start_dtime,
				end_dtime: end_dtime,
			}
		},
		onAvailClick: function(avail, e){
			if(this.higlightedDayCodes.length) return
			var editAvailData = {
				avail: new Availability(avail)
			}
			editAvailData.targetEl = e.target.findElemByClass('avail')
			this.editAvailData = editAvailData
		},
		onEditAvailSuccess: function(){
			this.compWrap.loadAndGenerate()
		},
		onDeleteAvailSuccess: function(){
			this.compWrap.loadAndGenerate()
		},
		onModeSelectChange: function(val){
			this.currWorkMode = val
			this.compWrap.loadAndGenerate()
		},
		createAvail: function(){
			var compVm = this
			var compWrap = this.compWrap
			var dayCodesD = this.higlightedDayCodes.map(this.parseDayCode)
			var newAvails = []
			var availsToRemove = []
			var aaoHash = {}
			dayCodesD.forEach(function(dcd){
				availsToRemove = availsToRemove.concat(compVm.findAvailsOnDtime(dcd))
				aaoHash[dcd.area_id +'**'+ dcd.agency_id +'**'+ dcd.organization_id] = dcd
			})

			var startEnd = this.getAvailSelectionStartEnd(dayCodesD)
			var start_dtime = startEnd.start_dtime
			var end_dtime = startEnd.end_dtime

			console.log('start:', start_dtime)
			console.log('end:', end_dtime)

			Object.keys(aaoHash).forEach(function(k){
				newAvails.push(compVm.createAvailObj(aaoHash[k], start_dtime, end_dtime))
			})
			this.rawAvailsData = this.rawAvailsData.concat(newAvails)
			compWrap.generate()
			compVm.isLoading = true
			compWrap.massAddOrEditAvails(
				newAvails, 
				function(r){
					if(newAvails.length > r.length) ViolationWarnings.showFor(null, {message:'Не удалось создать '+ (newAvails.length - r.length) +'недоступностей, так как в интервале существуют смены', type: 'warning'})
					compWrap.loadAndGenerate()
				}, 
				function(r){compWrap.loadAndGenerate() }
			)
		},
		removeAvails: function(){
			var compVm = this
			var dayCodesD = this.higlightedDayCodes.map(this.parseDayCode)
			var availsToCrop = []
			var availsToRemove = []
			
			var aaoHash = {}
			dayCodesD.forEach(function(dcd){
				aaoHash[dcd.area_id +'**'+ dcd.agency_id +'**'+ dcd.organization_id] = dcd
			})

			var startEnd = this.getAvailSelectionStartEnd(dayCodesD)
			var start_dtime = startEnd.start_dtime
			var end_dtime = startEnd.end_dtime
			
			var rawAvailsData = this.rawAvailsData
			Object.keys(aaoHash).forEach(function(k){
				var dcd = aaoHash[k]
				rawAvailsData.forEach(function(av){
					if ((av.start_dtime >= start_dtime && av.end_dtime <= end_dtime) &&
							av.agency_id == dcd.agency_id && 
							av.area_id == dcd.area_id && 
							av.organization_id == dcd.organization_id
						){
						availsToRemove.push(av)
						return 
					}
					if ((av.end_dtime >= start_dtime && av.start_dtime < end_dtime) &&
							av.agency_id == dcd.agency_id && 
							av.area_id == dcd.area_id && 
							av.organization_id == dcd.organization_id
						){
						var nav = new Availability(av)
						if(nav.start_dtime < start_dtime && nav.end_dtime > end_dtime){
							var nav2 = new Availability(nav, {isNewId: true})
							nav2.setEnd(nav.end_dtime)
							nav2.setStart(end_dtime)
							availsToCrop.push(nav2)
						}
						if(nav.end_dtime > start_dtime) nav.setEnd(start_dtime)
						if(nav.start_dtime > end_dtime) nav.setStart(end_dtime)
						availsToCrop.push(nav)
					}
				})
			})
			availsToCrop.sort(function(a,b){
				return (b.id || 0) - (a.id || 0)
			})
			this.removeAndEditAvails(availsToCrop, availsToRemove)
		},
		removeAndEditAvails: function(availsToCrop, availsToRemove){
			var compWrap = this.compWrap
			var editAvails = function(){
				compWrap.massAddOrEditAvails(
					availsToCrop, 
					compWrap.loadAndGenerate, 
					function(r){compWrap.loadAndGenerate() }
				)
			}
			if(availsToRemove.length){
				compWrap.removeAvails(
					availsToRemove, 
					editAvails, 
					function(r){compWrap.loadAndGenerate() }
				)
			}else{
				editAvails()
			}
		},
		findAvailsOnDtime: function(dcd){
			return this.rawAvailsData.filter(function(av){
				return (av.start_dtime >= dcd.start_dtime && av.start_dtime < dcd.start_dtime + Date.day) &&
								 av.agency_id == dcd.agency_id && 
								 av.area_id == dcd.area_id && 
								 av.organization_id == dcd.organization_id
			})
		},
		createAvailObj: function(dcd, start_dtime, end_dtime){
			var av = new Availability({
				area_id: dcd.area_id,
				agency_id: dcd.agency_id,
				organization_id: dcd.organization_id,
			})
			av.setStart(start_dtime)
			av.setEnd(end_dtime)
			return av
		}
	}
}