shift_assign.loadPromoSchedule = function (afterLoad) {
	var vm = this.vm
	var start_dtime = topDateChanger.interval.selected_start_dtime
	var end_dtime = topDateChanger.interval.selected_end_dtime
	var req = '/api-'+ sa_settings.apiKey +'-schedule/?format=json' +
		'&orgunit=' + (orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null) +
		'&start=' + new Date(start_dtime).toISODateString() +
		'&end=' + new Date(end_dtime-1).toISODateString() +
		'&month=' + new Date(topDateChanger.interval.selected_month_start_dtime).toISODateString() +
		'&party=' + request_page_party +
		'&mode=' + (vm.currWorkMode || '') +
		'&_=' + new Date().getTime()
	$.get(req).then(
		function (r) {
			//load shifts
			vm.rawRowsData = r.blocks
			vm.rawShiftsData = r.shifts.map(function(rs){return new Shift(rs, {reverseIds: sa_settings.reverseIds})})
			vm.rawShiftsDataBackup = vm.rawShiftsData.slice()
			vm.rawAvailsData = r.avails.map(function(rs){return new Availability(rs, {reverseIds: true})})
			afterLoad()
		},
		function (r) {
			if(r.responseJSON.non_field_errors){
				vm.emptyTablePlaceholderErrored = r.responseJSON.non_field_errors
				vm.rawRowsData = []
				vm.rawShiftsData = []
				vm.rawShiftsDataBackup = []
				vm.rawAvailsData = []
				afterLoad()
				return
			}
			vm.rawRowsData = [
				{
					"id": 250,
					"name": "Демо-данные, отображаемые в случае ошибки загрузки данных таблицы с сервера",
					"rows": [
						{
							"organization": {
								"id": 1,
								"name": "Магазин № 00"
							},
							"area": {
								"id": 1,
								"name": "AV",
								"color": "",
								"icon": ""
							},
							"size": "1"
						},
						{
							"organization": {
								"id": 1,
								"name": "Магазин № 00"
							},
							"area": {
								"id": 2,
								"name": "Photo-Avto",
								"color": "",
								"icon": ""
							},
							"size": "2"
						},
						{
							"organization": {
								"id": 1,
								"name": "Магазин № 00"
							},
							"area": {
								"id": 4,
								"name": "SHA",
								"color": "",
								"icon": ""
							},
							"size": "4"
						},
						{
							"organization": {
								"id": 1,
								"name": "Магазин № 00"
							},
							"area": {
								"id": 5,
								"name": "LHA",
								"color": "",
								"icon": ""
							},
							"size": "3"
						}
					]
				}
			]
			vm.rawAvailsData = [
				{
					"id": 1,
					"start": "2019-05-08T11:15:00+03:00",
					"end": "2019-05-08T18:15:00+03:00",
					"area_id": 2,
					"agency_id": 250,
					"organization_id": 1
				}
			].map(function(rs){return new Availability(rs, {reverseIds: true})})
			vm.rawShiftsData = [
				{
					"id": 55126,
					"start": "2019-05-08T03:00:00+03:00",
					"end": "2019-05-08T23:59:00+03:00",
					"state": "accept",
					"area_id": 2,
					"agency_id": 250,
					"organization_id": 1,
					"employee_id": null,
					"employee": null,
					"worktime": 480,
					urow_index: 0
				},
			].map(function(rs){return new Shift(rs, {reverseIds: sa_settings.reverseIds})})
			vm.rawShiftsDataBackup = vm.rawShiftsData.slice()
			afterLoad()
		}
	)
}
shift_assign.exportPromoSchedule = function () {
	var vm = this.vm
	var start_dtime = topDateChanger.interval.selected_start_dtime
	var end_dtime = topDateChanger.interval.selected_end_dtime
	var req = '/api-'+ sa_settings.apiKey +'-schedule/?format=json' +
		'&orgunit=' + (orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null) +
		'&start=' + new Date(start_dtime).toISODateString() +
		'&end=' + new Date(end_dtime-1).toISODateString() +
		'&party=' + request_page_party +
		'&mode=' + (vm.currWorkMode || '') +
		'&_=' + new Date().getTime() +
		'&xlsexport=true'
	blobXHR({
		url: req,
	})
}
shift_assign.addOrEditShift = function(shift, onOk, onErr){
	if(shift.start_dtime > shift.end_dtime ) shift.stretchEnd(Date.day)
	var req = '/api-'+ sa_settings.apiKey +'-shift/?format=json'+
		(shift.id && shift.id > 0? '&shift_id='+ shift.id : '')+
		'&_='+ new Date().getTime()
	if(shift.employee_id == 'none'){
		delete shift.employee_id
		delete shift.employee
	}
	var data = Object.assign({}, shift)
	data.csrfmiddlewaretoken = csrf_token
	$.ajax({
		url: req,
		type: 'post',
		data: data,
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
}
shift_assign.removeShifts = function(shifts, onOk, onErr){
	var shift_ids = shifts.map(function(s){return s.id})
	$.ajax({
		url: '/api-'+ sa_settings.apiKey +'-shift/',
		headers:{
			'X-CSRFToken': csrf_token,
		},
		data:{
			shift_ids: JSON.stringify(shift_ids),
		},
		type: 'DELETE',
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
}
shift_assign.removeAvails = function(avails, onOk, onErr){
	var avail_ids = avails.map(function(a){return a.id})
	$.ajax({
		url: '/api-availability/',
		headers:{
			'X-CSRFToken': csrf_token,
		},
		data:{
			avail_ids: JSON.stringify(avail_ids),
		},
		type: 'DELETE',
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
} 
shift_assign.checkIfEmplAllowed = function(p, onOk, onErr){
	var shift = p.shift
	if(!shift.employee_id) onOk({})
	var req ='/api-free-employees/'
	$.ajax({
		url: req,
		type: 'get',
		dataType: 'json',
		data:{
			format: 'json',
			organization_id: shift.organization_id,
			agency_id: shift.agency_id,
			shift_id: shift.id,
			agency_employee_id: shift.employee_id,
			start: shift.start,
			end: shift.end,
			_: new Date().getTime()
		},
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
} 
shift_assign.loadEmplsForShift = function(p, onOk, onErr){
	var shift = p.shift
	var tab = p.tab
	var req ='/api-free-employees/'
	var data = {
		format: 'json',
		organization_id: shift.organization_id,
		agency_id: shift.agency_id,
		shift_id: shift.id,
		tab: tab,
		start: shift.start,
		end: shift.end,
		party: request_page_party,
		_: new Date().getTime()
	}
	if(p.search) data.search = p.search
	$.ajax({
		url: req,
		type: 'get',
		dataType: 'json',
		data: data,
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
}
shift_assign.massAddOrEditShifts = function(p, onOk, onErr){
	var shifts = p.shifts
	var isOverwrite = p.isOverwrite
	var req = '/api-'+ sa_settings.apiKey +'-shift/'

	shifts = shifts.map(function(shift){
		if(p.isAdding) delete shift.id
		if(shift.employee_id == 'none'){
			delete shift.employee_id
			delete shift.employee
		}
		return Object.assign({}, shift)
	})

	var data = {
		shifts: JSON.stringify(shifts),
		csrfmiddlewaretoken: csrf_token,
		overwrite: isOverwrite
	}
	$.ajax({
		url: req,
		type: 'post',
		data: data,
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
}
shift_assign.massAddOrEditAvails = function(avails, onOk, onErr){
	var req = '/api-availability/?_='+ new Date().getTime()
	var data = {
		avails: JSON.stringify(avails.map(
			function(avail){
				a = Object.assign({}, new Availability(avail, {reverseIds: true}))
				if(a.id < 0) delete a.id
				return a
			}
		)),
		csrfmiddlewaretoken: csrf_token,
		overwrite: true
	}
	$.ajax({
		url: req,
		type: 'post',
		data: data,
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
}

shift_assign.loadShiftViolations = function(p, onOk, onErr){
	var shift = p.shift
	var req ='/api-shift-violations/'
	$.ajax({
		url: req,
		type: 'get',
		dataType: 'json',
		data:{
			format: 'json',
			start: shift.start,
			agency_employee_id: shift.employee.id,
			_: new Date().getTime()
		},
		success: function(r){
			onOk && onOk(r)
		}, error: function(r){
			onErr && onErr(r)
		}
	})
}