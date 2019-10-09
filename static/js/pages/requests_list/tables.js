$('body').on('orgunits:loaded', function(){
	datatable = $('.m_datatable').mDatatable({
		stateSave: true,
		stateSaveCallback: function(settings,data) {
			localStorage.setItem( 'local_dataTables_' + settings.sInstance, JSON.stringify(data) )
		},
		stateLoadCallback: function(settings) {
			return JSON.parse( localStorage.getItem( 'local_dataTables_' + settings.sInstance ) )
		},
		translate:{
			records:{
				processing:"Поиск..",
				noRecords:"Записей не найдено"
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
						info:"Показаны записи с {" + "{start}} по {" + "{end}} из {" + "{total}}"
					}
				}
			}
		},
		data: {
			type: 'remote',
			source: {
				read: {
					method: 'GET',
					url: '/outsourcing-requests/',
					params: {
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						status: function () {
							return filters.status_select.getValue();
						},
						organization_id: function(){
							return filters.organization_select.getValue();
						},
						date: function () {
							return filters.date_select.getValueAsDate();
						},
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						// sample data mapping
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						var organizations = raw['organization_list']
						setOrUpdateOrgSelect(organizations);

						return dataSet;
					},
				},
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: true,
			serverSorting: true,
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
					pageSizeSelect: [10, 20, 30, 50, 100],
				},
			},
		},

		// columns definition
		columns: [
			{
				field: 'organization__name',
				title: 'Магазин',
				sortable: true,
				filterable: false, // disable or enable filtering
				template: function(row){
					return valueToCell(row, {type: 'organization'})
				}
			}, {
				field: 'jobs',
				title: 'Функции',
				sortable: false,
				width: 80,
				filterable: false, // disable or enable filtering
			},  {
				field: 'period',
				title: 'Период',
				sortable: false,
				width: 150,
				template: function (row) {
					return valueToCell(row, {type: 'period'})
				},
			}, {
				field: 'dt_accepted',
				title: 'Получено',
				sortable: false,
				width: 150,
				template: function (row) {
					return valueToCell(row, {type: 'dt_accepted'})
				}
			}, {
				field: 'shifts_count',
				title: 'Смены',
				sortable: false,
				width: 50,
			}, {
				field: 'duration',
				title: 'Часы',
				sortable: false,
				width: 50,
				template: function (row) {
					return valueToCell(row, {type: 'timedelta_minutes'})
				},
			}, {
				field: 'state',
				title: 'Статус',
				sortable: true,
				template: function (row) {
					var state = {
						'ready': {'title': 'Обработана'},
						'accepted': {'title': 'Получена'},
					};
					return state[row.state].title;
				},
			}, {
				field: 'action',
				title: '',
				sortable: false,
				width: 33,
				template: function (row) {
					var state = {
						'ready': {'title': 'Просмотр', 'class': 'fa fa-eye'},
						'accepted': {'title': 'Рассмотреть', 'class': 'fa fa-edit'},
					};
					return '<a href="/shifts-confirm/?request_id=' + row.id + '" class="employee_edit m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="' + state[row.state].title + ' ">' + '<i class="' + state[row.state].class + '"</i></a>'
					}
			},
		],
	});
	tableReloader = new TableReloader(datatable)
})
