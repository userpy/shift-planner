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
					url: '/api-get-claims/',
					params: {
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						agency_id: function() {
							return filters.agency_select.getValue()
						},
						status_code: function() {
							return filters.status_select.getValue()
						},
						date: function() {
							return filters.date_select.getValueAsDate()
						},
						'_': function(){return new Date().getTime()}
					},
					map: function(raw) {
						var dataSet = raw;
						if(typeof raw.data !== 'undefined') {
							dataSet = raw.data;
						}
						setOrUpdateAgencySelect(raw['agency_list']);

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
		search: {
			input: $('#generalSearch')
		},
		columns: [{
				field: 'number',
				title: '#',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 100,
				template: function(row) {
					return valueToCell(row, {type: 'tnumber'})
				}
			},
			{
				field: 'organization__parent__name',
				title: 'Город',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 100,
				template: function(row) {
					return valueToCell(row, {type: 'organization_parent'})
				}
			}, {
				field: 'organization__name',
				title: 'Магазин',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 120,
				template: function(row) {
					return valueToCell(row, {type: 'organization'})
				}
			}, {
				field: 'agency__name',
				title: 'Агентство',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 220,
				template: function(row) {
					return valueToCell(row, {type: 'agency'})
				}
			}, {
				field: 'claim_type',
				title: 'Вид',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 80,
				template: function(row) {
					return valueToCell(row, {type: 'claim_type'})
				}
			}, {
				field: 'status__name',
				title: 'Статус',
				sortable: true,
				filterable: false, // disable or enable filtering
				width: 120,
				template: function(row) {
					return valueToCell(row, {type: 'status_name'})
				}
			}, {
				field: 'dt_updated',
				title: 'Обновлена',
				sortable: true,
				filterable: false, // disable or enable filtering
				//width: 180
				template: function(row) {
					return valueToCell(row, {type: 'dt_updated'})
				}
			}, {
				field: 'text',
				title: 'Текст',
				sortable: false,
				filterable: false, // disable or enable filtering
				width: 300,
				template: function(row) {
					return valueToCell(row, {type: 'text'})
				}
			}
		]
	}).css('cursor','pointer');
	tableReloader = new TableReloader(datatable)
})