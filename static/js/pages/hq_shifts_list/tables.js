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
						start: function() {
							return getStartDateFromDatachanger()
						},
						month: function() {
							return getStartDateFromDatachanger()
						},
						end: function() {
							return getEndDateFromDatachanger()
						},
						status: function() {
							return filters.status_select.getValue();
						},
						agency_id: function() {
							return filters.agency_select.getValue();
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
						var agencies = raw['agency_list'];
						setOrUpdateAgencySelect(agencies);
						
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
						return '—';
				else
					return '—';
			},
		}, {
			field: 'request.organization.name',
			title: 'Магазин',
			filterable: false, // disable or enable filtering
		}, {
			field: 'job',
			title: 'Функция',
			width: 150,
		}, {
			field: 'start',
			title: 'Дата',
			width: 150,
			template: function(row) {
				return valueToCell(row, {type: 'start'});
			},
		}, {
			field: 'shift',
			title: 'Смена',
			width: 150,
			template: function(row) {
				return valueToCell(row, {type: 'period_hours'});
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
		}, ],
	});
	tableReloader = new TableReloader(datatable)
})