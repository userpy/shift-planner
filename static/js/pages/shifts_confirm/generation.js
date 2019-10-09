shift_confirm.loadAndGenerate = function(){
	shift_confirm.vm.isLoading = true
	shift_confirm.loadData(shift_confirm.generate.bind(shift_confirm))
}

shift_confirm.generate = function(){
	var shift_confirm = this

	var vm = shift_confirm.vm
	vm.rawShiftsDataBackup = vm.rawShiftsData.slice()
	shifts = shift_confirm.joinRawAndChangedShifts()
	var shiftsGroupedByOrganization = groupShiftsByOrganizations(shifts)

	shifts.sort(function(a,b){return b.start_dtime - a.start_dtime})
	
	let monthDaysLength = getMonthLengthForDtime(shifts.first.start_dtime)
	vm.monthDaysLength = monthDaysLength
	var daysInIntervalLength = shifts.last.start_dtime - shifts.first.start_dtime > 7*Date.day ? 7 : monthDaysLength
	vm.zoomMode = daysInIntervalLength == 7 ? 'week' : 'month'

	vm.start_dtime = daysInIntervalLength == 7 ? new Date(shifts[0].start_dtime).startOfWeek().getTime() : new Date(shifts[0].start_dtime).startOfMonth().getTime()
	vm.monthDayWidth = shift_confirm.getMonthDayWidth()
	var tableStartDtime = vm.start_dtime

	var workload = {}
	vm.rawWorkloadData.forEach(function(w){
		var k = Object.keys(w)[0]
		workload[new Date(k).startOfDay().getTime()] = w[k]
	})

	var blocks = cloneViaJSON(vm.rawRowsData)
	blocks.forEach(function(block){
		var agency_id = block.id
		var c = 0
		block.rows.forEach(function(row){
			var area_id = row.area.id
			var organization_id = row.organization.id
			//row.code = [area_id, organization_id].join('**')
			// добавляем каунтер, чтобы избежать дублирования row.code
			row.code = [area_id, organization_id, c].join('**')
			row.urows = Array.apply(null, Array(+row.size)).map(function(ur, i){
				return {
					code: [area_id, organization_id].join('**')+'**'+ i,
					index: i,
					weeks: genUrowWeeks(agency_id, area_id, organization_id, ur, i)
				}
			})
			row.shiftsDurationSumm = calcRowSumm(row)
			c ++
		})
	})
	var orgFilterValues = []
	var areaFilterValues = []
	blocks = blocks.map(function(b){
		b.rows = b.rows.filter(function(r){
			var isShouldBeVisible = true
			if(orgFilterValues.length){
				isShouldBeVisible = false
				if(~orgFilterValues.indexOf(''+r.organization.id)) isShouldBeVisible = true
			}
			if(isShouldBeVisible && areaFilterValues.length){
				isShouldBeVisible = false
				if(~areaFilterValues.indexOf(''+r.area.id)) isShouldBeVisible = true
			}
			return isShouldBeVisible && r
		})
		return b
	})
	blocks = blocks.filter(function(bl){
		return bl.rows.length
	})
	vm.blocks = blocks
	
	var filteredShifts = shifts.filter(function(s){
		var isShouldBeVisible = true
		if(orgFilterValues.length){
			isShouldBeVisible = false
			if(~orgFilterValues.indexOf(''+s.organization_id)) isShouldBeVisible = true
		}
		if(areaFilterValues.length){
			isShouldBeVisible = false
			if(~areaFilterValues.indexOf(''+s.area_id)) isShouldBeVisible = true
		}
		return isShouldBeVisible && s
	})
	var daySumms = [], totalDaysSumm = 0
	if(vm.zoomMode == 'week'){
		for(var i = 0; i < daysInIntervalLength; i++){
			var day_dtime = tableStartDtime + i*Date.day
			var daySumm = calcSummForInterval(day_dtime, day_dtime + 1..day, filteredShifts)
			totalDaysSumm += daySumm.duration
			daySumms.push({
				duration: daySumm.duration,
				count: daySumm.count,
				cssWidth: 100 / daysInIntervalLength +'%'
			})
		}
	} else {
		var weeks = Date.splitMonthIntoWeeks(tableStartDtime)
		daySumms = weeks.map(function(week){
			var daySumm = calcSummForInterval(week.start_dtime, week.end_dtime, filteredShifts)
			totalDaysSumm += daySumm.duration
			return {
				duration: daySumm.duration,
				count: daySumm.count,
				cssWidth: 100 / daysInIntervalLength * week.length +'%'
			}
		})
	}
	vm.daySumms = daySumms.slice()
	vm.totalDaysSumm = totalDaysSumm
	
	vm.$refs.table_body.scrollTop = vm.bodyScrollPos
	vm.monthDayWidth = shift_confirm.getMonthDayWidth()
	vm.bodyHeightCss = shift_confirm.calcBodyHeight()
	
	// иначе мигает сообщение "нет данных для отображения" после генерации
	// потому что флаг лоадинг снимается, но массив дней движком еще не осознался
	Vue.nextTick(function(){
		setTimeout(function(){
			vm.isLoading = false
		}, 100)
	})

	function genUrowWeeks(agency_id, area_id, organization_id, urow, urow_index){
		var weeks = []
		if(vm.zoomMode == 'week'){
			weeks.push(fillUrow(agency_id, area_id, organization_id, urow_index, tableStartDtime, 7))
		} else {
			var weeksData = Date.splitMonthIntoWeeks(tableStartDtime)
			weeksData.forEach(function(week){
				var daysLength = (week.end_dtime - week.start_dtime) / Date.day
				weeks.push(fillUrow(agency_id, area_id, organization_id, urow_index, week.start_dtime, daysLength))
			})
		}
		return weeks
	}
	function genDayTt(dtime){
		return workload[dtime] ? 'Подтверждено смен ранее: ' +
				workload[dtime].map(function(r){
						return r.text+' '+r.total
					}).join(', ') : ''
	}
	function fillUrow(agency_id, area_id, organization_id, urow_index, start_dtime, daysLength){
		var d = []
		for(var i = 0; i < daysLength; i++){
			var allShifts = findAllShiftInsideDay(start_dtime + i*Date.day, getShiftsGroupedByOrganizations(organization_id), agency_id, area_id, urow_index)
			var day = {
				start_dtime: start_dtime + i*Date.day,
				allShifts: allShifts,
				shifts: findShiftInsideDay(start_dtime + i*Date.day, allShifts, agency_id, area_id, urow_index),
				cssWidth: 100 / daysLength +'%',
				code: [start_dtime + i*Date.day, agency_id, area_id, organization_id, urow_index].join('**'),
				tooltip: genDayTt(start_dtime + i*Date.day)
			}
			d.push(day)
		}
		return d
	}
	function findAllShiftInsideDay(day_start, shifts, agency_id, area_id){
		// найти смены дня для всей строки
		//нет проверки по organization_id, так как предполагается работа со сгруппирванными по этому айди сменами
		var shifts = shifts.filter(function(s){ 
			return s.start_dtime >= day_start &&
					s.start_dtime < day_start + 1..day && 
					s.agency_id == agency_id &&
					s.area_id == area_id
		})
		// задать порядок
		shifts.sort(function(a,b){return a.start_dtime - b.start_dtime})
		return shifts
	}
	function findShiftInsideDay(day_start, shifts, agency_id, area_id, urow_index){
		// найти смены дня для подстроки
		// фильтрация только по подстроке, так как предполагаетася работа с отфильтрованными для дня сменами
		var shifts = shifts.filter(function(s){ 
			return s.urow_index == urow_index
		}).slice(0,3)
		// задать порядок
		shifts.sort(function(a,b){return a.start_dtime - b.start_dtime})
		return shifts
	}
	function shiftDurationReducer(ps, cs){
		return ps + (cs.worktime*60000)
	}
	function calcRowSumm(row){
		return row.urows.reduce(function(pr, cr){// все подстрочки
			return pr + cr.weeks.reduce(function(pw, cw){// все недели
				return pw + cw.reduce(function(pd, cd){// все дни
					return pd + cd.shifts.reduce(shiftDurationReducer, 0)
				}, 0)
			}, 0)
		}, 0)
	}
	function calcSummForInterval(start_dtime, end_dtime, shifts){
		var intervalShifts = shifts.filter(function(s){
			return s.start_dtime >= start_dtime && s.start_dtime < end_dtime
		})
		return {
			duration: intervalShifts.reduce(shiftDurationReducer, 0),
			count: intervalShifts.length
		}
	}
	function getShiftsGroupedByOrganizations(organization_id){
		return shiftsGroupedByOrganization[organization_id] || []
	}
	function groupShiftsByOrganizations(shifts){
		var result = {} //{organization_id:[shifts]}
		shifts.forEach(function(s){
			if(result[s.organization_id])
				result[s.organization_id].push(s)
				else
				result[s.organization_id] = [s]
		})
		return result
	}
	function calcHeightOffsetsForRows(blocks, vm){
		var isBlockOnlyOne = blocks.length <= 1 //когда блок 1, не выводится заголовок
		blocks.forEach(function(block, i){
			var prevBlock = blocks[i-1]
			var topOffset = 0
			var blockHeight = 0	
			if(prevBlock) topOffset = prevBlock.height + prevBlock.topOffset
			if(!isBlockOnlyOne){
				if(prevBlock) topOffset += vm.rowsHeight.rowSeparator
				blockHeight += vm.rowsHeight.rowSeparator
			}
			block.topOffset = topOffset
			block.rows.forEach(function(r, i){
				var prevRow = block.rows[i-1]
				r.height = r.urows.length * vm.rowsHeight.urow
				r.isHiddenByScrolling = false
				if(prevRow) 
					r.topOffset = prevRow.topOffset + prevRow.height
					else
					r.topOffset = topOffset
				blockHeight += r.height
			})
			block.height = blockHeight
		})
		return blocks
	}
}

getMonthLengthForDtime = function(dtime){
	let start_dtime = new Date(dtime).startOfMonth().getTime()
	let end_dtime = new Date(start_dtime).setMonth(new Date(start_dtime).getMonth() +1)
	return (end_dtime - start_dtime) / Date.day
}