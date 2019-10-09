// Нажатие dropdown-кнопки "Действие" - выпадающего списка действий
$('#action_button').on('click', function(){
	if(datatable.getSelectedRecords().length == 0){ 
		$('.mass_action').hide();
	} else {
		$('.mass_action').show();
	}
})
