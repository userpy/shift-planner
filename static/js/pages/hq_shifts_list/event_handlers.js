// Обработчик смены клиента вверху
$('#top_org_select_control').on('change', function() {
	tableReloader.reload();
});

$('#generalSearch').on('keyup', function(e) {
	if(e.keyCode == 13) {
		if($(this).val().length >= 3)
			tableReloader.reload();
	}
	if($(this).val().length == 0)
		tableReloader.reload();
});
