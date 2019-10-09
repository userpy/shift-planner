var saRowsInViewportMix = {
	data: function(){return{
		higlightedDayCodes: [],
		higlightedDayCodesCopyToPresent: [],
		prevHiglightedDayCodes: [], // выделение слетает после клика, после клика срабатывает копирование. Надо кэшировать выбранные дни
		higlightedShifts: [],
		prevHiglightedShifts: []
	}},
	methods:{
		onEmplRowClick: function(row){
			return
		},
		onDayInDaysLineClick: function(day_dtime){
			return
		},
		reactivateRowsZoneHighlight: function(){
			this.higlightedDayCodes = this.prevHiglightedDayCodes.slice()
			this.higlightedShifts = this.prevHiglightedShifts.slice()
		},
		clearHighlightRowsUnderZone: function(){
			this.prevHiglightedDayCodes = this.higlightedDayCodes
			if(this.isCopyInPresent){
				this.higlightedDayCodesCopyToPresent = []
			} else {
				this.higlightedDayCodes = []
			}
			this.prevHiglightedShifts = this.higlightedShifts
			this.higlightedShifts = []
			this.closeAllMassEditChildFrames()
		},
		applySelection: function(doAfter){
			// вызывается, когда кнопка мыши была отпущена
			// создать выделение, только если в нем есть смены
			if(this.isCopyInPresent) return // если происходит выделение, куда копировать, то выделить нужно все дни
			this.isLoading = true
			var compVm = this
			setTimeout(function(){
				compVm.findHighlightedShiftsInDays()
				compVm.isLoading = false
				doAfter()
			}, 0)
		},
		showZoneIfAnyShiftSelected: function(){
			var isShouldBeVisible = this.currWorkMode == 'promo' || this.currWorkMode == 'broker' || this.higlightedShifts.length
			this.higlightedDayCodes = isShouldBeVisible ? this.higlightedDayCodes : []
			this.hoveredDayLineDtimes = isShouldBeVisible ? this.hoveredDayLineDtimes : []
			this.selectedURowCodes = isShouldBeVisible ? this.selectedURowCodes : []
		},
		highlightRowsUnderZone: jQuery.throttle(200, function(){
			var compVm = this
			if(!this.isSelectingViaMouse || !this.selectionZoneCss) return
			this.removeHoverSelectionFromDayAndRows()
			var hoveredTableDayCodes = this.findHoveredTableDayCodes()
			if(hoveredTableDayCodes.length) {
				if(this.isCopyInPresent){
					this.higlightedDayCodesCopyToPresent = hoveredTableDayCodes
				}else{
					this.higlightedDayCodes = hoveredTableDayCodes
				}
				return 
			}
			
			var rows = this.findRowsInViewPort()
			if(!rows.length) return

			var hoveredQuotasDayCodes = this.findHoveredQuotasDayCodes(rows)
			if(hoveredQuotasDayCodes.length) {
				if(this.isCopyInPresent){
					this.higlightedDayCodesCopyToPresent = hoveredQuotasDayCodes
				}else{
					this.higlightedDayCodes = hoveredQuotasDayCodes
				}
				return
			}

			var dayWidth = rows[0].days[0].rect.width
			var dayHeight = rows[0].days[0].rect.height
			var sz = { // нужно расширить выделенную зону на ширину одного блока дня, чтобы частично накрытые дни тоже считались выделенными
				top: +this.selectionZoneCss.top.slice(0, -2) - dayHeight,
				left: +this.selectionZoneCss.left.slice(0, -2) - dayWidth,
				width: +this.selectionZoneCss.width.slice(0, -2) + dayWidth*2, // умножение на два, потому что мы меняем не координаты границы, а ширину. В нее входят две увеличенные границы
				height: +this.selectionZoneCss.height.slice(0, -2) + dayHeight*2,
			}
			// найти коды дней под зоной
			var dayCodes = rows.reduce(function(p,c){
				return p.concat(c.days)
			},[]).filter(function(d){
				return (
					d.rect.top > sz.top && //дальше от верха, чем зона
					d.rect.left > sz.left && //дальше от левого края, чем зона
					d.rect.left + d.rect.width < sz.left + sz.width && //правый конец заканчивается раньше, чем у зоны
					d.rect.top + d.rect.height < sz.top + sz.height //нижний конец заканчивается раньше, чем у зоны
					) 
			}).map(function(d){return d.dayCode})
			if(this.isCopyInPresent){
				this.higlightedDayCodesCopyToPresent = dayCodes
			}else{
				this.higlightedDayCodes = dayCodes
				//this.higlightedDayCodes = this.higlightedDayCodes.concat(dayCodes)
			}
		}),
		findHighlightedShiftsInDays: function(){
			// собрать все выделенные дни, взять из них смены, отфильтровать дни без смен
			var compVm = this
			if(this.hoveredDayLineDtimes.length){
				var higlightedShifts = []
				// выделение столбцов дней, смены оптимальнее искать по дате начала
				var h_dtStart = this.hoveredDayLineDtimes[0]
				var h_dtEnd = this.hoveredDayLineDtimes[this.hoveredDayLineDtimes.length -1] + Date.day
				this.rawShiftsData.forEach(function(s){
					if(s.start_dtime >= h_dtStart && s.start_dtime < h_dtEnd) higlightedShifts.push(s)
				})
				this.higlightedShifts = higlightedShifts
				this.showZoneIfAnyShiftSelected()
				return
			}

			this.higlightedShifts = this.higlightedDayCodes.map(function(dc){
				var dayWithCode
				compVm.forEachDay(function(d){
					if(d.code == dc) dayWithCode = d
				})
				return dayWithCode
			}).filter(function(d){return d.shifts.length}).reduce(function(p,c){
				return p.concat(c.shifts)
			},[])
			//this.higlightedShifts = getUnique(this.higlightedShifts,'id')

			
			this.showZoneIfAnyShiftSelected()
		},
		findHoveredQuotasDayCodes: function(rows){
			var compVm = this
			var sz = {
				top: +this.selectionZoneCss.top.slice(0, -2),
				left: +this.selectionZoneCss.left.slice(0, -2),
				width: +this.selectionZoneCss.width.slice(0, -2),
				height: +this.selectionZoneCss.height.slice(0, -2),
			}
			var dayRowEl = this.widgetBody.querySelector('.days-line')
			var dayRowRect = dayRowEl.getBoundingClientRect()
			if(sz.left > dayRowRect.left) return [] //выделение не в колонке магазинов
			var dayCodes = []
			var selectedURowCodes = []
			rows.forEach(function(r){
				var rTop = r.rect.top
				var rBot = r.rect.top + r.rect.height
				var sTop = sz.top
				var sBot = sz.top + sz.height
				if( !((rTop > sTop && rTop < sBot) || (rBot > sTop && rBot < sBot)) ) return
				r.days.forEach(function(d){dayCodes.push(d.dayCode); selectedURowCodes.push(d.urowCode)})
			})
			this.selectedURowCodes = selectedURowCodes
			return dayCodes
		},
		findHoveredTableDayCodes: function(){
			var hoveredDays = []
			var compVm = this
			var dayRowEl = this.widgetBody.querySelector('.days-line')
			var dayRowRect = dayRowEl.getBoundingClientRect()
			var dayWidth = compVm.zoomMode == 'week' ? dayRowRect.width / 7 : +compVm.monthDayWidth.slice(0, -2)
			var interval = compVm.zoomMode == 'week' ? topDateChanger.interval.week : topDateChanger.interval.month
			var selectionZoneLeft = Math.min(this.selectionCurrCoords.x, this.selectionStartCoords.x)
			var selectionZoneRight = Math.max(this.selectionCurrCoords.x, this.selectionStartCoords.x)
			var selectionZoneTop = Math.min(this.selectionCurrCoords.y, this.selectionStartCoords.y)

			if(selectionZoneLeft < dayRowRect.left) return []//рамка не закрывает дни
			if(selectionZoneTop > dayRowRect.top + dayRowRect.height) return [] //рамка ниже дней

			var columnsOnLeftNotSelected = (selectionZoneLeft - dayRowRect.left) / dayWidth | 0
			var columnsSelected = ((selectionZoneRight - dayRowRect.left) / dayWidth | 0) - columnsOnLeftNotSelected + 1
			var selectionStartDtime = interval.start_dtime + columnsOnLeftNotSelected * Date.day
			var hoveredDayLineDtimes = []
			for(var i = selectionStartDtime; i < selectionStartDtime + columnsSelected * Date.day && i < interval.end_dtime; i += Date.day){
				hoveredDays = hoveredDays.concat(this.daysGroupedByStartDtime[i])
				hoveredDayLineDtimes.push(i)
			}
			this.hoveredDayLineDtimes = hoveredDayLineDtimes
			return hoveredDays.map(function(d){return d.code})
		},
		findRowsInViewPort: function(){
			var compVm = this
			var allRows = this.widgetBody.querySelectorAll('.tw-body .tw-u-row')
			var bodyEl = this.widgetBody.querySelector('.tw-body')
			var tBodyRect = bodyEl.getBoundingClientRect()
			var isLastVisibleRowFound = false
			var dayWidth = null
			return allRows.map(function(r){
				if(isLastVisibleRowFound) return null
				var rRect = r.getBoundingClientRect()
				dayWidth = dayWidth || ( compVm.zoomMode == 'week' ? rRect.width / 7 : +compVm.monthDayWidth.slice(0, -2) )
				var rBottOffset = rRect.top + rRect.height
				if(tBodyRect.top > rBottOffset) return null
				if(tBodyRect.top + tBodyRect.height < rRect.top) {isLastVisibleRowFound = true; return null}
				var days = r.querySelectorAll('.day').map(function(d, count){
					return {
						day: d,
						rect: {
							top: rRect.top,
							height: rRect.height,
							left: rRect.left + count*dayWidth,
							width: dayWidth
						},
						urowCode: d.dataset.urowCode,
						dayCode: d.dataset.dayCode,
					}
				})
				return {
					row: r,
					rect: rRect,
					days: days
				}
			}).filter(function(r){return r})
		}
	}
}

// функция возвращает массив уникальных объектов
// на входе массив объектов
// ключ по которому фильтровать
function getUnique(arr, comp) {
	var unique = arr
  .map(function(e) {
    return e[comp];
  })
  .map(function(e, i, final) { 
    return final.indexOf(e) === i && i;
  })
  .filter(function(e) {
    return arr[e];
  })
  .map(function(e) {
    return arr[e];
  });
  
	return unique;
}

// function getUnique(arr, comp) {
// 	const unique = arr
// 		.map(e => e[comp])
// 	  	.map((e, i, final) => final.indexOf(e) === i && i)
// 	    .filter(e => arr[e]).map(e => arr[e]);
  
// 	return unique;
// }