
// // Обработчик наведения на последнюю ячейку строки
// $('#employees_datatable_table').
// 	on('mouseenter', 'td:last-child', function(e) {
// 		$(this).find('a').addClass('a-active');
// });
// $('#employees_datatable_table').
// 	on('mouseleave', 'td:last-child', function(e) {;
// 		$(this).find('a').removeClass('a-active');
// });
$('#employees_datatable_table').css('cursor','pointer');

// Инициализация таблицы сотрудников
$('body').on('orgunits:loaded', function(){
	//требуется загрузить организации для работы
	datatable = $('#employees_datatable_table').mDatatable({
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
						csrfmiddlewaretoken: csrf_token,
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						state: function() {
							return filters.status_select.getValue();
						},
						violation_ids: function() {
							return filters.violation_select.getValueAsFixedArrStr()
						},
						'datatable[query][generalSearch]': function() {
							if($('#generalSearch').val().length >= 3)
								return $('#generalSearch').val();
							return '';
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
					map: function(raw) {
						var dataSet = raw;
						if(typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						EL_EMPLOYEES_LIST = dataSet;
						var violations = raw['violations_list']
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
		// <!--search: {-->
		// <!--input: $('#generalSearch'),-->
		// <!--},-->
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
			field: 'number',
			title: 'ТН',
			filterable: false,
			sortable: true,
			width: 80
		}, {
			field: 'jobs',
			title: 'Функции',
			width: 80,
			sortable: false,
		}, {
			field: 'organizations',
			title: 'Клиенты',
			sortable: false,
			width: 150,
			template: function(row) {
				var orgs = '';
				if(row.organizations != null)
					for(var i = 0; i < row.organizations.length; i++)
						orgs += row.organizations[i]['organization__headquater__short'] + ' - ' + row.organizations[i]['organization__name'] + ' - ' + row.organizations[i]['number'] + '<br/>';
				if(row.open_recruitment_events.length > 0) {
					for(var i = 0; i < row.open_recruitment_events.length; i++)
						orgs += '<i class="m-menu__link-icon fa fa-clock" title="Ожидает подтверждения клиентом"></i> ' + row.open_recruitment_events[i]['headquater__short'] + ' - ' + row.open_recruitment_events[i]['organization__name'] + '<br/>';
				}
				if(row.closed_orghistory.length > 0) {
					for(var i = 0; i < row.closed_orghistory.length; i++)
						orgs += '<i class="m-menu__link-icon fa fa-ban" title="Ожидает увольнения"></i> ' + row.closed_orghistory[i]['organization__headquater__short'] + ' - ' + row.closed_orghistory[i]['organization__name'] + '<br/>';
				}
				return orgs;
			}
		}, {
			field: 'violations',
			title: 'Информация',
			sortable: false,
			width: 180,
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
$('body').on('orgunits:loaded orgunits:change', function(){
	tableReloader.reload()
})
