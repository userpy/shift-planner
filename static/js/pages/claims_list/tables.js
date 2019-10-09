$('body').on('orgunits:loaded', function(){
	datatable = $('.m_datatable').mDatatable({
		translate:{
			records:{
				processing:"Поиск..",
				noRecords:"Претензий не найдено"
			},
			toolbar:{
				pagination:{
					items:{
						default:{
							first:"Первая",
							prev:"Предыдущая",
							next:"Следующая",
							last:"Последняя",
							more:"Больше",
							input:"Ввести",
							select:"Выбрать"
						},
						info:"Показаны претензии с {" + "{start}} по {" + "{end}} из {" + "{total}}"
					}
				}
			}
		},
		data: {
			type: 'remote',
			source: {
				read: {
					method: 'GET',
					url: '/api-get-claims/',
					params: {
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						organization_id: function(){
							return filters.organization_select.getValue()
						},
						status_code: function(){
							return filters.status_select.getValue()
						},
						date: function () {
							return filters.date_select.getValueAsDate()
						},
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						setOrUpdateOrgSelect(raw['org_list']);

						return dataSet;
					}
				}
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: true,
			serverSorting: true
		},

		layout: {
			scroll: false,
			footer: false
		},

		sortable: true,
		pagination: true,
		toolbar: {
			items: {
				pagination: {
					pageSizeSelect: [10, 20, 30, 50, 100]
				}
			}
		},
		columns: [
			{
				field: 'number',
				title: '#',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 100,
				template: function(row){
					return valueToCell(row, {type: 'tnumber'})
				}
			},
			{
				field: 'organization__name',
				title: 'Магазин',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 120,
				template: function(row){
					return valueToCell(row, {type: 'organization'})
				}
			},  {
				field: 'claim_type',
				title: 'Вид',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 80,
				template: function(row){
					return valueToCell(row, {type: 'claim_type'})
				}
			}, {
				field: 'status__name',
				title: 'Статус',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 120,
				template: function (row) {
					return valueToCell(row, {type: 'status_name'})
				}
			},
			{
				field: 'dt_updated',
				title: 'Обновлена',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 120,
				template: function (row) {
					return valueToCell(row, {type: 'dt_updated'})
				}
			},  {
				field: 'text',
				title: 'Текст',
				sortable: false,
				filterable: false, // disable or enable filtering
				width: 350,
				template: function(row){
					return valueToCell(row, {type: 'text'})
				}
			}, {
				field: 'dt_status_changed',
				title: 'Смена статуса',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 120,
				template: function (row) {
					return valueToCell(row, {type: 'dt_status_changed'})
				}
			}, {
				field: 'attachments',
				title: 'Файлы',
				sortable: false,
				filterable: false, // disable or enable filtering
				width: 120,
				template: function (row) {
					return valueToCell(row, {type: 'attachments'})
				}
			}
		]
	}).css('cursor','pointer');
	tableReloader = new TableReloader(datatable)
})