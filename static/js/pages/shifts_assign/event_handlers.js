shift_assign.initEventListners = function(){
	var shift_assign = this
	var vm = shift_assign.vm
	addEventListener('interval:week:switch', function(e){
		vm.isLoading = true
		vm.start_dtime = topDateChanger.interval.selected_start_dtime
		vm.end_dtime = topDateChanger.interval.selected_end_dtime
		vm.onExitShiftSelection()
		vm.exitCopyToPresent(true)
		shift_assign.debouncedLoadAndGenerate()
	})
	addEventListener('interval:zoom:change', function(e){
		vm.onZoomSelectChange(e.detail.zoom_mode)
	})
	addEventListener('resize', function(e){
		vm.bodyHeightCss = shift_assign.calcBodyHeight()
		vm.tableHeaderHeightCss = shift_assign.calcHeadHeight() +'px'
		vm.scrollFixPadding = getScrollbarSize().width +'px'
		vm.workflowLineWidthCSS = shift_assign.calcWorkflowLineWidth() +'px'
		vm.monthDayWidth = shift_assign.getMonthDayWidth()
		vm.headButtsLeftCss = shift_assign.calcHeadButtsLeftPos()
		vm.headButtsWidthCss = shift_assign.calcHeadButtsWidth()
	})
	document.body.addEventListener('click', function(e){
		if(e.target.findElemByClass('shift') ||
			 e.target.findElemByClass('small-dropdown') ||
			 e.target.findElemByClass('sa-dropdown') ||
			 e.target.findElemByClass('select2-container')) return
		vm.editShiftData = null
	})
	document.body.addEventListener('click', function(e){
		if(e.target.findElemByClass('sa-dropdown') ||
			 e.target.findElemByClass('sa-filters-expand-btn') ||
			 e.target.findElemByClass('select2-container')) return
		vm.isFiltersDDVisible = false
	})
	document.body.addEventListener('scroll', function(e){
		vm.editShiftData = null
	})
	$('body').on('orgunits:loaded', function(e){
		shift_assign.loadAndGenerate()
	})
	$('#top_org_select_control').on('change', function () {
		shift_assign.loadAndGenerate()
		vm.exitCopyToPresent()
		vm.onExitShiftSelection()
		vm.onExitMassActions()
	})
}
shift_assign.getMonthDayWidth = function(){
	return shift_assign.calcWorkflowLineWidth() / topDateChanger.interval.month.duration * Date.day +'px'
},
shift_assign.calcBodyHeight = function(){
	var fullHeight = window.innerHeight - ae$('.tw-body').getBoundingClientRect().top - 35 - getScrollbarSize().height
	var blocks = shift_assign.vm ? shift_assign.vm.blocks : []
	var lastBlock = blocks.last || {}
	var rowsHeight = (lastBlock.topOffset + lastBlock.height) || (55 * 3)
	return Math.min(fullHeight, rowsHeight)+ 'px'
}
shift_assign.calcHeadHeight = function(){
	return ae$('.tw-head').getBoundingClientRect().height+'px'
}
shift_assign.calcWorkflowLineWidth = function(){
	return ae$('.tw-head .days-line').getBoundingClientRect().width
}
shift_assign.calcHeadHeight = function(){
	return ae$('.tw-head').getBoundingClientRect().height
}
shift_assign.calcHeadButtsLeftPos = function(){
	var r = ae$('.m-portlet__head-text').getBoundingClientRect()
	return r.width + 32 + 'px'
}
shift_assign.calcHeadButtsWidth = function(){
	var r = ae$('.m-portlet__head').getBoundingClientRect()
	return r.width - r.left- ae$('.m-portlet__head-text').getBoundingClientRect().width + 'px'
}