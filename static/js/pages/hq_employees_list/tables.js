
// Инициализация таблицы сотрудников
$('body').on('orgunits:loaded', function(){
	datatable = $('#hq_employees_datatable_table').mDatatable({
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
					url: '/api-employees-list/?format=json',
					params: {
						csrfmiddlewaretoken: csrf_token ,
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						agency_id: function() {
							return filters.agency_select.getValue()
						},
						violation_ids: function() {
							return filters.violation_select.getValueAsFixedArrStr()
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
						EL_EMPLOYEES_LIST = dataSet;

						var agencies = raw['agency_list']
						var violations = raw['violations_list']
						setOrUpdateAgencySelect(agencies);
						setOrUpdateViolationSelect(violations);

						return dataSet;
					},
				},
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: false,
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
		// search: {
		// input: $('#generalSearch'),
		// },
		columns: [{
			field: 'check',
			title: '#',
			filterable: false,
			sortable: false,
			width: 20,
			textAlign: 'center',
			selector: {
				class: 'm-checkbox--solid m-checkbox--brand'
			},
		}, {
			field: 'surname',
			title: 'ФИО',
			filterable: false,
			sortable: true,
			width: 250,
			template: function(row) {
				return row.name
			}
		}, {
			field: 'id',
			title: '',
			filterable: false,
			sortable: true,
			width: 0,
			template: function(row) {
				return '<span style="display:none" data-empl-id='+ row.id +'>'+ row.id +'</span>'
			}
		}, {
			field: 'date_of_birth',
			title: 'Дата рождения',
			filterable: false,
			sortable: false,
			width: 80,
			template: function (row) {
				return valueToCell(row, {type: 'date_of_birth'})
			}
		}, {
			field: 'external_number',
			title: 'ТН',
			filterable: false,
			sortable: true,
			width: 80
		}, {
			field: 'jobs',
			title: 'Функции',
			sortable: false,
			width: 80,
		}, {
			field: 'organizations',
			title: 'Город',
			sortable: false,
			width: 100,
			template: function(row) {
				var orgs = '';
				if(row.organizations != null)
					for(var i = 0; i < row.organizations.length; i++)
						orgs += row.organizations[i] + '<br/>';
				return orgs;
			}
		}, {
			field: 'agency',
			title: 'Агентство',
			sortable: false,
			width: 150,
		}, {
			field: 'violations',
			title: 'Информация',
			sortable: false,
			width: 220,
			template: function(row) {
				var violations = '';
				var colorClass = '';
				var iconClass = '';
				if(row.end_date == null)
					violations += "Работает c " + row.start_date.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1') + "</br>";
				else {
					var now = new Date();
					now.setHours(0);
					now.setMinutes(0);
					now.setSeconds(-1);
					var end = new Date(row.end_date);
					end.setHours(0);
					end.setMinutes(0);
					end.setSeconds(0);
					if(end < now){
					    violations += "Уволен с " + row.end_date.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1') + "</br>";
                    }
					else{
					    violations += "Работает до " + row.end_date.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1') + "</br>";
                    }
				}
				if(row.violations != null){
					for(var i = 0; i < row.violations.length; i++){
						switch(row.violations[i]['level']) {
							case 'low':
								colorClass = 'm--font-info';
								iconClass = 'fa-info-circle';
								break;
							case 'medium':
								colorClass = 'm--font-warning';
								iconClass = 'fa-exclamation-triangle';
								break;
							case 'high':
								colorClass = 'm--font-danger';
								iconClass = 'fa-exclamation-circle';
								break;
  							default:
								break;
						}
						violations += '<span class="'+ colorClass + '">' + row.violations[i]['message'] + '</span><br/>';
					};
				return violations;
				}
			}
		}],
	})
	.css('cursor','pointer');
	
	tableReloader = new TableReloader(datatable)
})
$('#generalSearch').on('keyup', function(e){
	if (e.keyCode == 13) {
		if ($(this).val().length >= 3)
			tableReloader.reload();
	}
	if ($(this).val().length == 0)
		tableReloader.reload();
});