var jobs_datatable, events_datatable, organizations_datatable, docs_datatable, transitions_datatable
// Таблица мероприятий
function init_events_datatable(){
	events_datatable = $('#events_datatable_table').mDatatable({
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
					url: '/api-employee-events/?format=json',
					params: {
						csrfmiddlewaretoken: csrf_token,
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						agency_employee_id: employee_id,
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						EVENTS = dataSet;
						return dataSet;
					},
				},
			},
			pageSize: 10,
	
			// <!--saveState: false,-->
			// <!--serverPaging: true,-->
			// <!--serverFiltering: true,-->
			// <!--serverSorting: true,-->
			serverPaging: true,
			serverFiltering: false,
			serverSorting: false,
		},
		// Перезапись 'field' обязательна в случае, если мы скрываем колонки. В деталях строки отображается поле 'field' вместо 'title'
		columns: [
				{
				field: 'dt_created',
				title: 'Дата и время',
				sortable: false,
				template: function(row){
					return valueToCell(row, {type: 'dt_created_full'})
				}
			}, {
				field: 'headquater',
				title: 'Клиент',
				sortable: false,
				template: function(row){
					return valueToCell(row, {type: 'headquater'})
				}
			}, {
				field: 'organization',
				title: 'Город',
				sortable: false,
				width: 100,
				template: function(row){
					return valueToCell(row, {type: 'organization'})
				}
			}, {
				field: 'kind',
				title: 'Событие',
				sortable: false,
				template: function(row){
					var translate = new Map();
					translate.set('recruitment', 'Прикрепление к клиенту');
					translate.set('reject', 'Отклонение');
					translate.set('accept_recruitment', 'Прием подтвержден');
					translate.set('reject_recruitment', 'Клиент не подтверждает прикрепление сотрудника');
					translate.set('dismissal', 'Открепление от клиента');
          translate.set('change', 'Изменение персональных данных');
          translate.set('agency', 'Переназначение агентства');
	
					return translate.get(row.kind);
				}
			},	{
				field: 'guid',
				title: 'GUID',
				filterable: false,
				sortable: false,
			},	{
				field: 'user',
				title: 'Пользователь',
				filterable: false,
				sortable: false,
				template: function(row){
					return valueToCell(row, {type: 'user'})
				}
			}, {
				field: 'info',
				title: 'Информация',
				width: 150,
				filterable: false,
				sortable: false,
				template: function(row){
					var info = '';
					if (row.kind === 'recruitment' || row.kind === 'accept_recruitment'){
						info += 'Принят ' + row.recruitment_date.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1');
					}
					else if (row.kind === 'reject_recruitment'){
						info += row.reject_reason;
					}
					else if (row.kind === 'dismissal'){
						info += 'Уволен ' + row.dismissal_date.replace(/(\d+)[-](\d+)[-](\d+)/, '$3.$2.$1');
						if (row.blacklist == true)
							info += ' без возможности повторного приема';
						if (row.dismissal_reason !== '')
							info += ' по причине "' + row.dismissal_reason + '"';
					}
					return info;
				}
			}],
		});
}
	
// таблица функции
function init_jobs_datatable(){
	var columns = [{
			field: 'job',
			title: 'Функция',
			filterable: false,
			width: 200,
		}, {
			field: 'start',
			title: 'Действует с',
			filterable: false,
			width: 160,
			template: function(row){
				return valueToCell(row, {type: 'start'})
			}
		},  {
			field: 'end',
			title: 'Действует по',
			filterable: false,
			width: 160,
			template: function(row){
				return valueToCell(row, {type: 'end'})
			}
		}
	]
	if(request_page_party){
		columns.push(	{
			field: 'action',
			title: 'Действие',
			filterable: false,
			width: 130,
			template: function(row){
				var edit_button = '<div job_id="' + row.job_id + '" job_his_id="' + row.id + '" class="jobs_edit m-portlet__nav-link btn m-btn m-btn--hover-accent m-btn--icon m-btn--icon-only m-btn--pill" title="Редактировать">							<i class="la la-edit"></i>						</div>';
				var remove_button = '<div job_id="' + row.job_id + '" job_his_id="' + row.id + '" class="jobs_remove m-portlet__nav-link btn m-btn m-btn--hover-danger m-btn--icon m-btn--icon-only m-btn--pill" title="Удалить">							<i class="la la-trash"></i>						</div>';
				return edit_button + remove_button;
			}})
	}
	jobs_datatable = $('#jobs_datatable_table').mDatatable({
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
					url: '/api-job-histories/?format=json',
					params: {
						csrfmiddlewaretoken: csrf_token,
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						agency_employee_id: employee_id,
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						JOBS = dataSet;
						return dataSet;
					},
				},
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: false,
			serverSorting: false,
		},
		layout: {
			scroll: false,
			footer: false
		},
		sortable: false,
		pagination: true,
		toolbar: {
			items: {
				pagination: {
					pageSizeSelect: [10, 20, 30, 50, 100],
				},
			},
		},
		columns: columns
		});
}
// таблица документы
function init_docs_datatable(){
	var columns = [{
			field: 'doc_type',
			title: 'Документ',
			filterable: false,
			width: 200,
			template: function(row){
				return row.doc_type.name
			}
		}, {
			field: 'start',
			title: 'Действует с',
			filterable: false,
			width: 160,
			template: function(row){
				return valueToCell(row, {type: 'start'})
			}
		}, {
			field: 'end',
			title: 'Действует до',
			filterable: false,
			width: 160,
			template: function(row){
				return valueToCell(row, {type: 'end'})
			}
		}, {
			field: 'text',
			title: 'Комментарий',
			filterable: false,
			width: 160,
			template: function(row){
				return valueToCell(row, {type: 'text'}) + '<span class="span-helper"'+// потому что ни один пример апи таблицы не заработал
				'data-doc_id="' + row.id +
			'" ></span>'
			}
		}, {
			field: 'has_files',
			title: 'Наличие файла',
			filterable: false,
			width: 160,
			template: function(row){
				if(row.has_files) {
					return '<i class="m-menu__link-icon fa fa-plus-circle" title="Файл загружен"></i>'
				}else{
					return '<i class="m-menu__link-icon fa fa-minus-circle" title="Файл не загружен"></i>'
				}
			}
		}
	]
	docs_datatable = $('#docs_datatable_table').mDatatable({
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
					url: '/api-employee-docs/?format=json',
					params: {
						csrfmiddlewaretoken: csrf_token,
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						agency_employee_id: employee_id,
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						DOCS = dataSet;
						return dataSet;
					},
				},
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: false,
			serverSorting: false,
		},
		layout: {
			scroll: false,
			footer: false
		},
		sortable: false,
		pagination: true,
		toolbar: {
			items: {
				pagination: {
					pageSizeSelect: [10, 20, 30, 50, 100],
				},
			},
		},
		columns: columns
	}).
	css('cursor','pointer');

	var doc_id 
	if(request_page_party){
		$('#docs_datatable_table').on('m-datatable--on-layout-updated', function () {
			$('#docs_datatable_table tr').on('click', function(e){
				var td = e.target.findElemByTag('td')
				if(!td) return //шапка
				var row = this
				//if(row.childNodes[0] == td) return
				var ss = row.querySelector('.span-helper')
				doc_id = ss.dataset.doc_id
				DOC_ID_SELECTED = doc_id
				showDocPp(doc_id)
			});
		})
	}
	$('#doc_delete_button').on('click', function(){
		$('.docs.modal-controls--default').hide()
		$('.docs.modal-controls--confirm').show()
	})

	$('#doc_delete_cancel_action_button').on('click', function(){
		$('.docs.modal-controls--default').show()
		$('.docs.modal-controls--confirm').hide()
	})

	$('#doc_delete_submit_action_button').on('click', function(){
		removeDocFromPp(doc_id)
	})

}

// таблица клиенты
function init_organizations_datatable(){
	organizations_datatable = $('#organizations_datatable_table').mDatatable({
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
					url: '/api-org-histories/?format=json',
					params: {
						csrfmiddlewaretoken: csrf_token,
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						agency_employee_id: employee_id,
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						ORGANIZATIONS = dataSet;
						return dataSet;
					},
				},
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: false,
			serverSorting: false,
		},
		layout: {
			scroll: false,
			footer: false
		},
		sortable: false,
		pagination: true,
		toolbar: {
			items: {
				pagination: {
					pageSizeSelect: [10, 20, 30, 50, 100],
				},
			},
		},
		columns: [
			{
				field: 'organization',
				title: 'Организация',
				filterable: false,
				template:function(row){
					return valueToCell(row, {type: 'organization_full'})
				}
			}, {
				field: 'number',
				title: 'Табельный номер',
				filterable: false,
				template:function(row){
					return valueToCell(row, {type: 'tnumber-short'})
				}
			}, {
				field: 'start',
				title: 'Прикреплен с',
				filterable: false,
				template: function(row){
					return valueToCell(row, {type: 'start'})
				}
			}, {
				field: 'end',
				title: 'Прикреплен до',
				filterable: false,
				template: function(row){
					return valueToCell(row, {type: 'end'})
				}
			}, {
				field: 'is_inactive',
				title: 'Состояние',
				filterable: false,
				template: function(row){
					if(row.is_inactive == false) {
						return 'Активен'
					} else {
						return 'Неактивен'
					}
				}
			},
		],
	});
}

// таблица переводов
function init_transitions_datatable(){
	var columns = [{
			field: 'agency',
			title: 'Агентсво',
			filterable: false,
			width: 200,
			template: function(row){
				return row.agency
			}
		}, {
			field: 'start',
			title: 'Действовало с',
			filterable: false,
			width: 160,
			template: function(row){
				return valueToCell(row, {type: 'start'})
			}
		}, {
			field: 'end',
			title: 'Действовало до',
			filterable: false,
			width: 160,
			template: function(row){
				return valueToCell(row, {type: 'end'})
			}
		}
	]
	transitions_datatable = $('#transitions_datatable_table').mDatatable({
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
					url: '/api-agency-employee-history/?format=json',
					params: {
						csrfmiddlewaretoken: csrf_token,
						agency_employee_id: employee_id,
						'_': function(){return new Date().getTime()}
					},
					map: function (raw) {
						var dataSet = raw;
						if (typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						return dataSet;
					},
				},
			},
			pageSize: 10,
			serverPaging: true,
			serverFiltering: false,
			serverSorting: false,
		},
		layout: {
			scroll: false,
			footer: false
		},
		sortable: false,
		pagination: true,
		toolbar: {
			items: {
				pagination: {
					pageSizeSelect: [10, 20, 30, 50, 100],
				},
			},
		},
		columns: columns
	})
}