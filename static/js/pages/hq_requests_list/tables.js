$('body').on('orgunits:loaded', function(){
	datatable = $('.m_datatable').mDatatable({
		stateSave: true,
		stateSaveCallback: function(settings,data) {
			localStorage.setItem( 'local_dataTables_' + settings.sInstance, JSON.stringify(data) )
		},
		stateLoadCallback: function(settings) {
			return JSON.parse( localStorage.getItem( 'local_dataTables_' + settings.sInstance ) )
		},
		translate: tables_l10n,
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
						agency_id: function(){
							return filters.agency_select.getValue();
						},
						start: function() {
							return getStartDateFromDatachanger()
						},
						month: function() {
							return getStartDateFromDatachanger()
						},
						end: function() {
							return getEndDateFromDatachanger()
						},
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						var agencies = raw['agency_list'];
						setOrUpdateAgencySelect(agencies);

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
		search: {
			input: $('#generalSearch'),
		},
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
				filterable: false, // disable or enable filtering
				width: 80,
			},  {
				field: 'agency__name',
				title: 'Агентство',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 220,
				template: function(row){
					return valueToCell(row, {type: 'agency'})
				}
			},  {
				field: 'period',
				title: 'Период',
				sortable: false,
				width: 150,
				template: function (row) {
					return valueToCell(row, {type: 'period'})
				},
			},  {
				field: 'dt_accepted',
				title: 'Получено',
				sortable: false,
				width: 150,
				template: function (row) {
					return valueToCell(row, {type: 'dt_accepted'})
				},
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
			},{
				field: 'action',
				title: '',
				sortable: false,
				width: 33,
				template: function (row) {
					return '<a href="/hq-shifts-confirm/?request_id=' + row.id + '" class="employee_edit m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Просмотр"> <i class="fa fa-eye"></i></a>'
				}
			},
		],
	});
	tableReloader = new TableReloader(datatable)
})