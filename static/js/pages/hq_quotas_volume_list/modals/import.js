$('#import_quotas_button').on('click', function(){
	$('#modal_import_quota').modal({backdrop: true})
	$('#file_to_import').val('')
	$('#file_to_import').trigger('change')
})
$('#import_submit_button').on('click', function(){
	blockModalForm()
	var formData = new FormData()
	formData.append('csrfmiddlewaretoken', csrf_token)
	formData.append('xls_file', $('#file_to_import')[0].files[0], 'xls.xls')
	$.ajax({
		type: 'POST',
		url: '/hq-import-quotas-volume/',
		data: formData,
		processData: false,
		contentType: false,
		success: function (data) {
			unblockModalForm()
			tableReloader.reload()
			$('#modal_import_quota').modal('hide')
		},
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
})