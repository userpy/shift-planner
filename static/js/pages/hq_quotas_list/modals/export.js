$('#export_quotas_button').on('click', function(){
	var data = {
		'orgunit': orgSelect.selectedUnit.code,
		'promo_id': filters.promo_select.getValue() || '',
		'area_id': filters.area_select.getValue() || '',
		'pagination[page]': function() {
			return $("#ajax_data").mDatatable().getDataSourceParam('pagination')['page'];
		}() || '',
		'pagination[perpage]': function() {
			return $("#ajax_data").mDatatable().getDataSourceParam('pagination')['perpage'];
		}() || '',
		'datatable[sort][field]': function() {
			if('sort' in $("#ajax_data").mDatatable().getDataSourceParam()) {
				return $("#ajax_data").mDatatable().getDataSourceParam('sort')['field'];
			}
		}() || '',
		'datatable[sort][sort]': function() {
			if('sort' in $("#ajax_data").mDatatable().getDataSourceParam()) {
				return $("#ajax_data").mDatatable().getDataSourceParam('sort')['sort'];
			}
		}() || '',
		xlsexport: true,
		format: 'json',
		_: new Date().getTime()
	}
	blobXHR({
		url:'/api-quotas-list',
		data: data,
	})
})
