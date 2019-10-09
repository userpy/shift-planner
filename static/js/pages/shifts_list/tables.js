$('body').on('orgunits:loaded', function(){
	datatable = $('#m_datatable').mDatatable({
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
					url: '/api-shifts-list/?format=json',
					params: {
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						date: function(raw) {
							return filters.date_select.getValueAsDate();
						},
						status: function() {
							return filters.status_select.getValue()
						},
						organization_id: function() {
							return filters.organization_select.getValue()
						},
						'datatable[query][generalSearch]': function() {
							if($('#generalSearch').val().length >= 3)
								return $('#generalSearch').val();
							return '';
						},
						'_': function(){return new Date().getTime()}
					},
					map: function(raw) {
						var dataSet = raw;
						if(typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						var organizations = raw['organization_list'];
						setOrUpdateOrgSelect(organizations);
						return dataSet;
					},
				},
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: false,
			serverSorting: true,
		},
		// layout definition
		layout: {
			scroll: false,
			footer: false
		},
		// column sorting
		sortable: false,
		pagination: true,
		toolbar: {
			// toolbar items
			items: {
				// pagination
				pagination: {
					// page size select
					pageSizeSelect: [10, 20, 30, 50, 100],
				},
			},
		},
		// columns definition
		columns: [{
			field: 'request.organization.parent.name',
			title: 'Город',
			filterable: false,
			width: 100,
			template: function(row) {
				if(row.request.organization.parent)
					if(row.request.organization.parent.kind == 'city')
						return row.request.organization.parent.name;
					else
						return "";
				else
					return "";
			},
		}, {
			field: 'request.organization.name',
			title: 'Магазин',
			filterable: false, // disable or enable filtering
		}, {
			field: 'job',
			title: 'Функция',
		}, {
			field: 'start',
			title: 'Дата',
			width: 150,
			template: function(row) {
				return valueToCell(row, {type: 'start'})
			},
		}, {
			field: 'shift',
			title: 'Смена',
			width: 150,
			template: function(row) {
				return valueToCell(row, {type: 'period_hours'})
			},
		}, {
			field: 'agency_employee.name',
			title: 'ФИО',
			template: function(row) {
				if(row.agency_employee)
					return row.agency_employee.name;
				else
					return "<hr style='background-color: #909090;'>";
			},
		}, {
			field: 'submit_employee',
			title: 'Действия',
			width: 150,
			template: function(row) {
				// https://stackoverflow.com/questions/1606797/use-of-apply-with-new-operator-is-this-possible
				// берется дата из пришедшей строчки, у нее такой формат "2018-08-01 10:00". Гугл подсказывает, что у даты формат должен быть RFC2822 или ISO 8601, чтобы его понял ие. 
				// было решено пока обрабатывать такое, а потом научить сервер присылать стандартное время, как везде было
				var start = new Date(row.start)
				start.setHours(0);
				start.setMinutes(0);
				start.setSeconds(0);
				var now = new Date();
				now.setHours(0);
				now.setMinutes(0);
				now.setSeconds(-1);

				if(start < now)
					return '';
				var text = "Назначить";
				var class_name = 'btn-primary'
				if(row.agency_employee) {
					employee_id = row.agency_employee.id
					value = row.agency_employee.name
					text = "Сменить";
					class_name = "btn-secondary";
				} else {
					employee_id = 0;
					value = "Не назначен"
				}
				return '<button class="btn ' + class_name + '" data-toggle="modal" data-target="#modal_set_shift" shift_id="' + row.id + '" employee_id="' + employee_id + '" >' + text + '</button>'
			},
		}],
	});
	tableReloader = new TableReloader(datatable)
})