var shift_assign = new function(){
	this.morningStart = 6..hours
	this.lightDayStart = 14..hours
	this.nightStart = 18..hours

	var shift_assign = this
	this.vm = null
	this.components = []
	this.init = function(){
		initComponents()
		var data = getInitialData()
		var vm = new Vue({
			el: '.shifs_assign_nest',
			template: '#shifs_assign_template',
			data: data,
			mixins: [copyToFutureMix, copyToPresentMix, selectIntervalMix, saRowsInViewportMix, saShiftEditMix, saAvailEditMix],
			methods:{
				onMousedownFix: function(e){
					e.stopPropagation()
					throwEvent('custom-mousedown', {native:e})
				},
				onZoomSelectChange: function(zoomMode){
					this.zoomMode = zoomMode
					this.start_dtime = topDateChanger.interval.selected_start_dtime
					shift_assign.loadAndGenerate()
				},
				isDtimeReadonly: function(dtime){
					var todayDate = new Date().startOfDay()
					var twoMonthDate = todayDate.startOfMonth().setMonth(todayDate.getMonth()+3) -1
					if(this.zoomMode == 'week'){
						if(dtime < topDateChanger.interval.month.start_dtime ||
							dtime >= topDateChanger.interval.month.end_dtime) return true
					} 
					return dtime < todayDate.getTime() || dtime > twoMonthDate
				},
				isDayReadonly: function(day){
					return this.isDtimeReadonly(day.start_dtime) || day.shifts.length >= 3 
				},
				isDaySelectedToEdit: function(day){
					return this.editShiftData && this.editShiftData.dayCode == day.code
				},
				calcWeekWidth: function(week){
					if(this.zoomMode == 'week') return '100%'
					return week.length * 100 / topDateChanger.interval.month.duration * Date.day + '%'
				},
				onDayZoneClick: function(p, e){
					if(this.isCopyInPresent) return
					if(this.higlightedDayCodes.length) return
					if(!this.settings.isAllowedTo.createShift) return
					e.stopImmediatePropagation()
					var start = p.start_dtime + shift_assign[p.zone]
					var end = start + 6..hours
					var shift = new Shift({
						area_id: p.area_id,
						organization_id: p.organization_id,
						agency_id: p.agency_id,
						urow_index: p.urow_index,
						employee_id: null,
						start: new Date( Model.tz.addOffsetFromServer(start)).toISOString(),
						end: new Date(Model.tz.addOffsetFromServer(end)).toISOString(),
					})
					this.editShiftData = {
						targetEl: e.target.findElemByClass('day-back-wrap'),
						dayCode: p.code,
						shift: shift
					}
				},
				onShiftClick: function(shift, e){
					if(this.isCopyInPresent) return
					if(this.higlightedDayCodes.length) return
					var editShiftData = {
						shift: new Shift(shift)
					}
					editShiftData.targetEl = e.target.findElemByClass('shift')
					editShiftData.isReadonly = shift.start_dtime < new Date().startOfDay().getTime()
					this.editShiftData = editShiftData
				},
				massAddOrEditShifts: function(shifts){
					if(!shifts.length) return
					this.isLoading = true
					var comp = this
					shift_assign.massAddOrEditShifts(
							{shifts: shifts, isOverwrite: true, isAdding: true}, 
							function(r){comp.onEditSuccess(r)}, 
							function(){shift_assign.loadAndGenerate()/*todo on err*/}
						)
				},
				massAddAndDeleteShifts: function(shiftsToAdd, shiftsToRemove){
					this.isLoading = true
					var compVm = this
					if(shiftsToRemove.length){
						shift_assign.removeShifts(
							shiftsToRemove,
							function(){
								compVm.rawShiftsData = compVm.rawShiftsData.filter(function(s){return s.id > 0})
								shift_assign.generate()
								shift_assign.massAddOrEditShifts(
									{shifts: shiftsToAdd, isOverwrite: true, isAdding: true}, 
									function(r){ compVm.onEditSuccess(r) },
									function(r){compVm.onEditError(); compVm.alertError(r, compVm) }
								)
							},
							function(r){compVm.onEditError(); compVm.alertError(r, compVm) }
						)
					} else {
						shift_assign.massAddOrEditShifts(
							{shifts: shiftsToAdd, isOverwrite: true, isAdding: true}, 
							function(r){ compVm.onEditSuccess(r) },
							function(r){compVm.onEditError(); compVm.alertError(r, compVm) }
						)
					}
				},
				callExport: function(){
					this.compWrap.exportPromoSchedule()
				},
				onExitFilters: function(){
					this.isFiltersDDVisible = false
				},
				onOrgFilterChange: function(values){
					this.orgFilterValues = values.map(function(id){return {id: id}}) || []
					shift_assign.generate()
				},
				onAreaFilterChange: function(values){
					this.areaFilterValues = values.map(function(id){return {id: id}}) || []
					shift_assign.generate()
				},
				parseDayCode: function(day){
					var codes = (day.code ? day.code : day).split('**')
					// start_dtime + i*Date.day, agency_id, area_id, organization_id, urow_index
					// in generation.js
					return {
						start_dtime: +codes[0],
						agency_id: codes[1],
						area_id: codes[2],
						organization_id: codes[3],
						urow_index: codes[4],
					}
				},
				parseUrowCode: function(urow){
					var codes = urow.code.split('**')
					// area_id, organization_id, urow_index
					// in generation.js
					return {
						area_id: codes[0],
						organization_id: codes[1],
						urow_index: codes[2],
					}
				},
				forEachDay: function(func){
					this.blocks.forEach(function(b){
						b.rows.forEach(function(r){
							r.urows.forEach(function(ur){
								ur.weeks.forEach(function(w){
									w.forEach(func)
								})
							})
						})
					})
				},
				checkVisibleOnScrollRows: $.throttle(200, false, function(){
					var visibleZoneFix = this.rowsHeight.urow * 15 //увеличение видимой области на несколько строк
					var scrollTop = this.bodyScrollPos
					var bodyHeight = parseFloat(this.bodyHeightCss)
					var blocks = this.blocks.slice()
					var firstVisibleRowTopOffset = null
					var lastVisibleRow = null, lastRow = null
					var areVisibleRowsEnded = false
					blocks.forEach(function(block){
						var visibleRowsInBlock = []
						block.rows.forEach(function(row, i){
							lastRow = row
							if(areVisibleRowsEnded){
								// если мы уже поняли, что видимые строки кончились, 
								// то можно скрывать остальные строки без лишних проверок
								row.isHiddenByScrolling = true
							}
							if( row.topOffset + row.height < scrollTop - visibleZoneFix || //строчка над областью видимости
								  row.topOffset > scrollTop + bodyHeight + visibleZoneFix)   //строчка под областью видимости
								{
								if(lastVisibleRow) areVisibleRowsEnded = true
								row.isHiddenByScrolling = true
								return
							} 
							row.isHiddenByScrolling = false
							lastVisibleRow = row
							if(!row.isHiddenByScrolling) visibleRowsInBlock.push(row)
							if(firstVisibleRowTopOffset === null) firstVisibleRowTopOffset = row.topOffset
						})
						if(!visibleRowsInBlock.length) 
							block.isHiddenByScrolling = true
							else
							block.isHiddenByScrolling = false
					})
					if(!firstVisibleRowTopOffset) firstVisibleRowTopOffset = 0
					if(!lastRow || !lastVisibleRow) return // если таких нет, значит строчек нет
					this.bodyPaddingTopCSS = firstVisibleRowTopOffset +'px' //оффсет первой видимой строчки
					this.bodyPaddingBottomCSS = 
						(lastRow.topOffset + lastRow.height) - 
						(lastVisibleRow.topOffset + lastVisibleRow.height) +'px' //оффсет последней + ее высота - оффсет последней видимой + ее высота
					this.blocks = blocks
				}),
				onScroll: function(e){
					this.editShiftData = null
					this.bodyScrollPos = this.$refs.table_body.scrollTop
					this.checkVisibleOnScrollRows(this.bodyScrollPos)
				},
				alertError: function(r, compVm){
					var r = r.responseJSON || {}
					var errors = Object.keys(r).map(function(ok){
						return r[ok]
					}).join('; ') || null
					alert(r.message || errors || 'Произошла неизвестная ошибка') //todo l10n
				}
			},
			computed:{
				widgetBody: function(){
					return this.$refs["widget-body"]
				}
			},
			mounted: function(){
				this.bodyHeightCss = shift_assign.calcBodyHeight()
				this.tableHeaderHeightCss = shift_assign.calcHeadHeight() +'px'
				this.workflowLineWidthCSS = shift_assign.calcWorkflowLineWidth() +'px'
				this.headButtsWidthCss = shift_assign.calcHeadButtsWidth()
				this.headButtsLeftCss = shift_assign.calcHeadButtsLeftPos()
				this.monthDayWidth = shift_assign.calcWorkflowLineWidth() / topDateChanger.interval.month.duration * Date.day +'px'
				var compVm = this
				addEventListener('mousedown',function(e){
					compVm.isMousePressed = true
				})
				addEventListener('mouseup',function(e){
					compVm.isMousePressed = false
				})
			},
			updated: function(){
				this.$refs.table_body.scrollTop = this.bodyScrollPos
			}
		})
		this.vm = vm
		this.initEventListners()
	}
	initComponents = function(){
		page_main_widget.components.forEach(function(c){c.init()})
	}
	getInitialData = function(){
		var defaultSettings = sa_settings || { isAllowedTo:{} }
		return{
			isMousePressed: false,
			isSelectionBoxVisible: false, //включает отображение границ выделяемой области
			compWrap: shift_assign,
			tableHeaderHeightCss: 0,
			bodyPaddingTopCSS: 0,
			bodyPaddingBottomCSS: 0,
			workflowLineWidthCSS: 0,
			headButtsLeftCss: 0, // отступ слева у верхних таблицы
			headButtsWidthCss: 0,
			monthDayWidth: 0,
			rowsHeight:{
				rowSeparator: 34,
				urow: 54
			},
			bodyScrollPos: 0,
			start_dtime: topDateChanger.interval.selected_start_dtime,
			end_dtime: topDateChanger.interval.selected_end_dtime,
			zoomMode: topDateChanger.interval.zoom_mode,
			scrollFixPadding: getScrollbarSize().width +'px',
			bodyHeightCss: 0,
			isLoading: true,
			editShiftData: null,
			editAvailData: null,
			rawRowsData: [],
			rawShiftsData: [],
			rawAvailsData: [],
			daysGroupedByStartDtime: {}, // нужно для оптимизации выделения столбцов-дней
			hoveredDayLineDtimes: [], // нужно для подсветки дней в полоске дней при выделении
			selectedURowCodes: [], // нужно для подсветки левой части строк при выделении
			blocks: [],
			daySumms: [],
			totalDaysSumm: 0,
			isFiltersDDVisible: false,
			orgFilterValues: [], //{id: id}
			areaFilterValues: [],//{id: id}
			settings: defaultSettings,
			emptyTablePlaceholderErrored: null,
			currWorkMode: defaultSettings.defaultWorkMode//что делает текущее выделение
		}
	}
	this.isShiftIntersectsWithAny = function(allShifts, shift){
		if(allShifts.some(function(as){
			return shift.organization_id == as.organization_id &&
						 shift.agency_id       == as.agency_id       &&
						 shift.organization_id == as.organization_id &&
						 shift.area_id         == as.area_id         &&
						 shift.urow_index      == as.urow_index      &&
						 shift.id              != as.id              &&
						 isIntersects(shift.start_dtime, shift.end_dtime, as.start_dtime, as.end_dtime)
			}))return true; else return false
	}
}()
document.addEventListener("DOMContentLoaded", function(event) {
	shift_assign.init()
});

var scrollBarSize
getScrollbarSize = function(){
	if(scrollBarSize){
		return {width: scrollBarSize.width, height: scrollBarSize.height}
	}
	var div = document.createElement('div')
	div.style.position = 'absolute'
	div.style.top = '90000px'
	div.style.overflow = 'scroll'
	document.body.appendChild(div)
	var width = div.getBoundingClientRect().width
	var height = div.getBoundingClientRect().height
	div.remove()
	scrollBarSize =  {width: width, height: height}
	return {width: width, height: height}
}
addEventListener('resize', function(){
	scrollBarSize = null
})
