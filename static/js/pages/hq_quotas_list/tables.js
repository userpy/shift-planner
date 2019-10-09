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
					url: '/api-quotas-list/',
					params: {
						violation_ids: function() {
							return filters.violation_select.getValueAsFixedArrStr()
						},
						orgunit: function(){return orgSelect.selectedUnit ? orgSelect.selectedUnit.code : null},
						promo_id: function () {
							return filters.promo_select.getValue();
						},
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
						var promos = raw['promo_list'];
						var areas = raw['area_list']
						var stores = raw['organization_list']
						var violations = raw['violations_list']
						setOrUpdateViolationSelect(violations);
						setOrUpdatePromoSelect(promos);
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
					var style = ''
					if (!row.is_active) {
						style = 'text-decoration:line-through'
					}
					return '<span style="'+ style + '">' + valueToCell(row, {type: 'store_parent_name'}) + '</span>'
				}
			}, {
				field: 'store__name',
				title: 'Магазин',
				sortable: true,
				filterable: false, // disable or enable filtering
				template: function(row){
					var style = ''
					if (!row.is_active) {
						style = 'text-decoration:line-through'
					}
					return '<span style="'+ style + '">' + row.store.name + '</span>'
				}
			},  {
				field: 'area__name',
				title: 'Зона',
				sortable: true,
				width: 80,
				template: function (row) {
					var style = ''
					if (!row.is_active) {
						style = 'text-decoration:line-through'
					}
					return '<span style="'+ style + '">' + row.area.name + '</span>'
				},
			},  {
				field: 'promo',
				title: 'Вендор',
				sortable: false,
				width: 220,
				template: function (row) {
					var style = ''
					if (!row.is_active) {
						style = 'text-decoration:line-through'
					}
					return '<span style="'+ style + '">' + row.promo.name + '</span>'
				},
			}, {
				field: 'value',
				title: 'Стендовые квоты',
				sortable: true,
				width: 150,
				template: function (row) {
					var style = ''
					if (!row.is_active) {
						style = 'text-decoration:line-through'
					}
					return '<span style="'+ style + '">' + row.value + '</span>'
				},
			}, {
				field: 'value_ext',
				title: 'Согласованные квоты',
				sortable: true,
				width: 150,
				template: function (row) {
					var style = ''
					if (!row.is_active) {
						style = 'text-decoration:line-through'
					}
					return '<span style="'+ style + '">' + row.value_ext + '</span>'
				},
			}, {
				field: 'max_quota',
				title: 'Максимум',
				sortable: false,
				width: 80,
				template: function (row) {
					var style = ''
					if (!row.is_active) {
						style = 'text-decoration:line-through'
					}
					return '<span style="'+ style + '">' + row.max_value + '</span>'
				},
			}, {
				field: 'free_quota',
				title: 'Свободно',
				sortable: false,
				width: 80,
				template: function (row) {
					var style = ''
					if (row.free_value > 0) {
						style = '-success'
					}
					if (row.free_value < 0){
						style = '-danger'
					}
					if (!row.is_active) {
						style += ' text-decoration:line-through'
					}
					return '<span class="m--font'+ style + '">'+ row.free_value + '</span>' + '<span class="span-helper"'+// потому что ни один пример апи таблицы не заработал
							'data-area_id="' + row.area.id +
						'" data-promo_id="'+ row.promo.id +
						'" data-store_id="'+ row.store.id +
						'" data-quota_id="'+ row.id +
						'" data-value="'   + row.value +
						'" data-value_ext="'   + row.value_ext +
						'" data-value_max="'   + row.max_value +
						'" data-value_free="'  + row.free_value +
						'" data-start="'   + row.start +
						'" data-end="'     + row.end +
						'" ></span>'
				},
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
			promo_id: ss.dataset.promo_id,
			store_id: ss.dataset.store_id,
			value: ss.dataset.value,
			value_ext: ss.dataset.value_ext,
			start: ss.dataset.start,
			end: ss.dataset.end
		})
	});
});
