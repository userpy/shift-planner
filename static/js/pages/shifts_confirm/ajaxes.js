shift_confirm.loadData = function (afterLoad) {
	var vm = this.vm
	var req = '/api-shifts-confirm/?format=json' +
		'&request_id=' + request_id +
		'&_=' + new Date().getTime()
	$.get(req).then(
		function (r) {
			//load shifts
			vm.rawRowsData = r.blocks
			vm.rawShiftsData = r.shifts.map(function(rs){return new Shift(rs)})
			vm.rawShiftsDataBackup = vm.rawShiftsData.slice()
			vm.rawWorkloadData = r.workload
			var changedShifts = []
			vm.rawShiftsData = vm.rawShiftsData.map(function(s){
				var newS = new Shift(s)
				if(!newS.state || newS.state == 'wait') {
					newS.state = 'accept'
					changedShifts.push(newS)
				}
				return shift_confirm.setShiftColor(new Shift(newS))
			})
			afterLoad(r)
		},
		function (r) {
			//todo handle error
			alert(r.responseJSON.non_field_errors)
			return
			var r = {
				"blocks": [
						{
								"id": 1,
								"name": "Квелл-Вест_Санкт-Петербург",
								"rows": [
										{
												"organization": {
														"id": 296,
														"name": "Магазин S190"
												},
												"area": {
														"id": "296_2",
														"name": "Склад",
														"icon": null,
														"color": null
												},
												"size": 1
										}
								]
						}
				],
				"shifts": [
						{
								"id": 109020,
								"start": "2019-02-27T11:00:00+03:00",
								"end": "2019-02-27T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 1774,
								"employee": {
										"id": 1774,
										"text": "Пантин Сергей Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109018,
								"start": "2019-02-26T11:00:00+03:00",
								"end": "2019-02-26T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 20977,
								"employee": {
										"id": 20977,
										"text": "Григорьев Сергей Евгеньевич"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109021,
								"start": "2019-02-24T11:00:00+03:00",
								"end": "2019-02-24T20:00:00+03:00",
								"state": "delete",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": null,
								"employee": null,
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109017,
								"start": "2019-02-23T11:00:00+03:00",
								"end": "2019-02-23T20:00:00+03:00",
								"state": "delete",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": null,
								"employee": null,
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109013,
								"start": "2019-02-22T11:00:00+03:00",
								"end": "2019-02-22T20:00:00+03:00",
								"state": "delete",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": null,
								"employee": null,
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109015,
								"start": "2019-02-20T11:00:00+03:00",
								"end": "2019-02-20T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 1774,
								"employee": {
										"id": 1774,
										"text": "Пантин Сергей Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109010,
								"start": "2019-02-19T11:00:00+03:00",
								"end": "2019-02-19T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 22055,
								"employee": {
										"id": 22055,
										"text": "Губайдуллин Роман Фаридович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109019,
								"start": "2019-02-17T11:00:00+03:00",
								"end": "2019-02-17T20:00:00+03:00",
								"state": "delete",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": null,
								"employee": null,
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109012,
								"start": "2019-02-16T11:00:00+03:00",
								"end": "2019-02-16T20:00:00+03:00",
								"state": "delete",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": null,
								"employee": null,
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109008,
								"start": "2019-02-14T11:00:00+03:00",
								"end": "2019-02-14T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 1774,
								"employee": {
										"id": 1774,
										"text": "Пантин Сергей Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109022,
								"start": "2019-02-13T11:00:00+03:00",
								"end": "2019-02-13T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 20137,
								"employee": {
										"id": 20137,
										"text": "Савинов Александр Александрович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109024,
								"start": "2019-02-12T11:00:00+03:00",
								"end": "2019-02-12T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 1774,
								"employee": {
										"id": 1774,
										"text": "Пантин Сергей Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109023,
								"start": "2019-02-10T11:00:00+03:00",
								"end": "2019-02-10T20:00:00+03:00",
								"state": "delete",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": null,
								"employee": null,
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109009,
								"start": "2019-02-09T11:00:00+03:00",
								"end": "2019-02-09T20:00:00+03:00",
								"state": "delete",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": null,
								"employee": null,
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109014,
								"start": "2019-02-07T11:00:00+03:00",
								"end": "2019-02-07T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 1774,
								"employee": {
										"id": 1774,
										"text": "Пантин Сергей Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109007,
								"start": "2019-02-06T11:00:00+03:00",
								"end": "2019-02-06T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 1774,
								"employee": {
										"id": 1774,
										"text": "Пантин Сергей Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109016,
								"start": "2019-02-05T11:00:00+03:00",
								"end": "2019-02-05T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 22055,
								"employee": {
										"id": 22055,
										"text": "Губайдуллин Роман Фаридович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109011,
								"start": "2019-02-03T11:00:00+03:00",
								"end": "2019-02-03T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 22179,
								"employee": {
										"id": 22179,
										"text": "Иванов Артемий Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						},
						{
								"id": 109006,
								"start": "2019-02-02T11:00:00+03:00",
								"end": "2019-02-02T20:00:00+03:00",
								"state": "accept",
								"agency_id": 1,
								"organization_id": 296,
								"employee_id": 22179,
								"employee": {
										"id": 22179,
										"text": "Иванов Артемий Константинович"
								},
								"area_id": "296_2",
								"worktime": 540,
								"urow_index": 0
						}
				],
				"diff": [],
				"workload": [
					{
							"2019-02-01": [
									{
											"text": "Склад",
											"total": 25
									},
									{
											"text": "ТЗ",
											"total": 31
									}
							]
					}]
		}
			vm.rawRowsData = r.blocks
			vm.rawShiftsData = r.shifts.map(function(rs){
				return shift_confirm.setShiftColor(rs)
			})
			vm.rawWorkloadData = r.workload
			vm.rawShiftsDataBackup = vm.rawShiftsData.slice()
			afterLoad()
		}
	)
}