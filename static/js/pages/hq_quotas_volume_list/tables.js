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
					url: '/api-quotas-volume-list/',
					params: {
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						area_id: function(){
							return filters.area_select.getValue();
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
						var areas = raw['area_list']
						var stores = raw['organization_list']
						setOrUpdateAreaSelect(areas);
						updatePpStoreSelect(stores)
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
				field: 'store__parent__name',
				title: 'Город',
				width: 100,
				sortable: true,
				filterable: false, // disable or enable filtering
				template: function(row){
					return valueToCell(row, {type: 'store_parent_name'})
				}
			}, {
				field: 'store__name',
				title: 'Магазин',
				sortable: true,
				filterable: false, // disable or enable filtering
				template: function(row){
					return row.store.name
				}
			},  {
				field: 'area__name',
				title: 'Зона',
				sortable: true,
				width: 150,
				template: function (row) {
					return row.area.name
				},
			}, {
				field: 'value',
				title: 'Максимум',
				sortable: true,
				width: 150,
				template: function (row) {
					return row.value + '<span class="span-helper"'+// потому что ни один пример апи таблицы не заработал
						  'data-area_id="' + row.area.id +
						'" data-store_id="'+ row.store.id +
						'" data-quota_id="'+ row.id +
						'" data-value="'   + row.value +
						'" data-start="'   + row.start +
						'" data-end="'   + row.end +
						'" ></span>'
				},
			}, {
				field: 'start',
				title: 'Действует с',
				sortable: false,
				filterable: false,
				width: 160,
				template: function(row){
					return valueToCell(row, {type: 'start'})
				}
			},  {
				field: 'end',
				title: 'Действует по',
				sortable: false,
				filterable: false,
				width: 160,
				template: function(row){
					return valueToCell(row, {type: 'end'})
				}
			}
		],
	})
	.css('cursor','pointer');
	tableReloader = new TableReloader(datatable)
})
$('.m_datatable').on('m-datatable--on-layout-updated', function () {
	$('.m_datatable tr').on('click', function(e){
		var td = e.target.findElemByTag('td')
		if(!td) return //шапка
		var row = this
		if(row.childNodes[0] == td) return
		var ss = row.querySelector('.span-helper')
		QUOTA_ID = ss.dataset.quota_id
		showEditQuotaPp({
			area_id: ss.dataset.area_id,
			store_id: ss.dataset.store_id,
			value: ss.dataset.value,
			start: ss.dataset.start,
			end: ss.dataset.end
		})
	});
});