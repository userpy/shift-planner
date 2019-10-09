// массовое удаление

var geEditeWarning = function(count, mode){
	return mode == 'delete' ? 
				 'От удаления выбранных ограничений квот зависит '+ count +' квот.' :
				 'От изменяемого ограничения квоты зависит ' + count + ' квот.'
}

$('#delete_quotas_button').on('click', function(){
	$('#modal_mass_delete_quota').modal({backdrop: true})
	var deleteButt = ae$('#mass_delete_quota_button')
	prepareButtForLoadingState(deleteButt)
	toggleButtonLoadingState(deleteButt, true)
	ae$('#modal_mass_delete_body').innerHTML = '<span class="m--font-bolder">Подождите…</span> Выполняется проверка возможности удаления выбранных ограничений квот.'
	var data = {
		quota_ids: JSON.stringify(datatable.getSelectedRecords().toArray().map(function(r){
			return r.querySelector('.span-helper').dataset.quota_id
		})),
		mode: 'check'
	}
	blockModalForm()
	OutRequests['delete-quota-volume']({
		data: data,
		success: function(resp){
			unblockModalForm()
			toggleButtonLoadingState(deleteButt, false)
			if(resp.result) 
				ae$('#modal_mass_delete_body').innerHTML = '<span class="m--font-danger">Внимание!</span> Удаление выбранных ограничений квот приведет к удалению '+ resp.result +' квот.'
				else
				ae$('#modal_mass_delete_body').innerHTML = '<span class="m--font-success">Проверка завершена!</span> Выбранные ограничения квот могут быть безопасно удалены, так как квоты по ним отсутствуют.'
		}, 
		error: function(response){
			unblockModalForm()
			toggleButtonLoadingState(deleteButt, false)
			handleServerErrorInModal(response)
			ae$('#modal_mass_delete_body').textContent = 'Возникла ошибка при выполнении запроса, попробуйте еще раз.'
		}
	})


})
$('#mass_delete_quota_cancel_button').on('click', function(){
	$('#modal_mass_delete_quota').modal('hide')
})
$('#mass_delete_quota_button').on('click', function(){
	var data = {
		mode: 'apply',
		quota_volume_ids: JSON.stringify(datatable.getSelectedRecords().toArray().map(function(r){
			return r.querySelector('.span-helper').dataset.quota_id
		})),
	}
	blockModalForm()
	OutRequests['delete-quota-volume']({
		data: data,
		success: function(resp){
			unblockModalForm()
			$('#modal_mass_delete_quota').modal('hide')
			tableReloader.reload()
		}, 
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
})


// удаление из попапа редактирования
var deleteQuotaFromEdit = function(){
	blockModalForm()
	var data = {
		quota_volume_ids: JSON.stringify([QUOTA_ID]),
		mode: 'apply',
	}
	OutRequests['delete-quota-volume']({
		data: data,
		success: function(resp){
			unblockModalForm()
			$('#modal_edit_quota').modal('hide')
			tableReloader.reload()
		}, 
		error: function(response){
			unblockModalForm()
			handleServerErrorInModal(response)
		}
	})
}