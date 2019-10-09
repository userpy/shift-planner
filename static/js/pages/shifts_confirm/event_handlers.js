shift_confirm.initEventListners = function(){
	var shift_confirm = this
	var vm = shift_confirm.vm

	addEventListener('resize', function(e){
		vm.bodyHeightCss = shift_confirm.calcBodyHeight()
		vm.tableHeaderHeightCss = shift_confirm.calcHeadHeight() +'px'
		vm.scrollFixPadding = getScrollbarSize().width +'px'
		vm.workflowLineWidthCSS = shift_confirm.calcWorkflowLineWidth() +'px'
		vm.monthDayWidth = shift_confirm.getMonthDayWidth()
		vm.headButtsLeftCss = shift_confirm.calcHeadButtsLeftPos()
		var portlet = ae$('.m-portlet')
		portlet.style.width = ''
		portlet.style.width = Math.max(portlet.offsetWidth, ae$('.table-widget').offsetWidth+50) + 'px'
		ae$('.m-footer').style.width = portlet.offsetWidth + 50 +'px'
		ae$('.m-footer').style.maxWidth = 'initial'
	})

	$('body').on('orgunits:loaded orgunits:change', function(e){
		shift_confirm.loadAndGenerate()
	})
}
shift_confirm.getMonthDayWidth = function(){
	return shift_confirm.calcWorkflowLineWidth() / shift_confirm.vm.monthDaysLength +'px'
},
shift_confirm.calcBodyHeight = function(){
	var fullHeight = window.innerHeight - ae$('.tw-body').getBoundingClientRect().top - 35 - getScrollbarSize().height
	var blocks = shift_confirm.vm ? shift_confirm.vm.blocks : []
	var lastBlock = blocks.last || {}
	var rowsHeight = (lastBlock.topOffset + lastBlock.height) || (55 * 3)
	return Math.min(fullHeight, rowsHeight)+ 'px'
}
shift_confirm.calcHeadHeight = function(){
	return ae$('.tw-head').getBoundingClientRect().height+'px'
}
shift_confirm.calcWorkflowLineWidth = function(){
	return ae$('.tw-head .days-line').getBoundingClientRect().width
}
shift_confirm.calcHeadHeight = function(){
	return ae$('.tw-head').getBoundingClientRect().height
}
shift_confirm.calcHeadButtsLeftPos = function(){
	var r = ae$('.m-portlet__head-title').getBoundingClientRect()
	return r.width + 32 + 'px'
}
shift_confirm.joinRawAndChangedShifts = function(){
	var vm = shift_confirm.vm
	vm.rawShiftsDataBackup = vm.rawShiftsData.slice()
	var shifts = vm.rawShiftsData
	var changedShifts = vm.changedShifts
	shifts = shifts.map(function(s){
		var isShiftChanged = changedShifts.filter(function(cs){
			return cs.id == s.id
		})
		if(isShiftChanged.length) 
			return isShiftChanged[0]
			else return s
	})
	return shifts
}
shift_confirm.performAction = function(action){
	var shifts = shift_confirm.joinRawAndChangedShifts()
	var shiftsData = shifts.map(function(s){
		return {id: s.id, state: s.state}
	})
	var isAnyRejected = shiftsData.some(function(sd){return sd.state == 'reject'})
	if(isAnyRejected || action == 'reject'){
		$('#modal_reject_confirm').modal({backdrop: true})
	} else {
		apply()
	}
	function apply(reject_reason, inPopup){
		if(inPopup && !reject_reason){
			handleNonServerErrorInModal('Нужно указать причину')
			return
		}
		if(outsource_enable){
			if(inPopup && !checkFormRequirments(ae$('#modal_reject_confirm')) )return
			var data = {
				'request_id': request_id,
				'shifts': JSON.stringify(shiftsData),
				'action': action,
				csrfmiddlewaretoken: csrf_token 
			}
			if(reject_reason) data.reject_reason = reject_reason
			OutRequests['update-request']({
				data: data,
				success: function (result) {
					window.location.href = '/requests-list/'
				},
				error: function (result) {
				}
			});
		}
	}
	if(!shift_confirm.isAlreadyClickedActionPp){
		shift_confirm.isAlreadyClickedActionPp = false
		$('#modal_reject_confirm_btn').on('click', function(){
			apply($('#reject_reason').val(), true)
		})
	}
}

