// Инициализация таблицы подтвердженных смен
function init_confirmed_shifts_table(response) {
	SHIFTS_JOBS = response.jobs; // Функции в ответе запроса jquery
	SHIFTS_WORKLOAD = response.shifts; // Вокрлоады в ответе запроса jquery
	// Возвращает индекс функции по значению функции
	function find_by_value(value) {
		for(var i = 0; i != SHIFTS_JOBS.length; i++) {
			if(SHIFTS_JOBS[i] === value) {
				return i;
			}
		}
	};
	// Предоставление ворклдоадам информации о job_id для работы с таблицей
	for(var shift_idx = 0; shift_idx != SHIFTS_WORKLOAD.length; shift_idx++) {
		for(var wl_idx = 0; wl_idx != SHIFTS_WORKLOAD[shift_idx].workload.length; wl_idx++) {
			SHIFTS_WORKLOAD[shift_idx].workload[wl_idx]['job_id'] = find_by_value(SHIFTS_WORKLOAD[shift_idx].workload[wl_idx]['job__name']);
		}
	}

	var cols_size = getDaysInPeriod(SC_NEWER_DATE, SC_OLDER_DATE);
	var rows_size = SHIFTS_JOBS.length;


	var table = $('#confirmed_shifts_table');
	table.html('');
	/// РЕФАКТОРИНГ
	// Проход по строкам - количество ворклоадов
	for(var row_id = 0; row_id < rows_size + 1; row_id++) {
		var row = null;
		// Если первая строка, добавляем только шапку
		if(row_id == 0) {
			table.append('<thead></thead>');
			table.find('thead').append('<tr id="ctr' + row_id + '"></tr>');
			row = table.find('thead tr').last();
		}
		// Если не первая, то добавляем остальную часть тела
		else {
			// При первой строке вне шапки создаем "тело"
			if(row_id == 1)
				table.append('<tbody></tbody>');
			var row_to_append = '<tr id="ctr' + row_id + '"></tr>';
			table.find('tbody').append(row_to_append);
			row = table.find('tbody tr').last();
		}
		// Заполнение тела таблиц
		for(var col_id = 0; col_id < cols_size + 2; col_id++) {
			if(row_id == 0)
				if(col_id == 0)
					row.append('<th id="cr' + row_id + 'd' + col_id + '"></th>');
				else {
					var date = new Date(SC_OLDER_DATE);
					date.setDate(date.getDate() + col_id - 1);
					var dd = date.getDate();
					if(dd < 10)
						dd = '0' + dd;
					var mm = date.getMonth() + 1;
					if(mm < 10)
						mm = '0' + mm;

					row.append('<th id="cr' + row_id + 'd' + dd + 'm' + mm + '"></th>');
				}
			else {
				if(col_id == 0)
					var cell = row.append('<td id="cr' + row_id + 'd' + col_id + '"></td>');
				else {
					var date = new Date(SC_OLDER_DATE);
					date.setDate(date.getDate() + col_id - 1);
					var dd = date.getDate();
					if(dd < 10)
						dd = '0' + dd;
					var mm = date.getMonth() + 1;
					if(mm < 10)
						mm = '0' + mm;

					row.append('<td id="cr' + row_id + 'd' + dd + 'm' + mm + '"></td>');
				}
			}
			if(row_id == 0 && col_id > 0) {
				var date = new Date(SC_OLDER_DATE);
				date.setDate(date.getDate() + col_id - 1);
				var dd = date.getDate();
				var str = dd;
				table.find('th').last().append(str);
			}
		}
	}

	for(var i = 0; i != SHIFTS_JOBS.length; i++) {
		var job_name = SHIFTS_JOBS[i];
		table.find('td:first-child').eq(i).html(job_name);
	}

	for(var shift_idx = 0; shift_idx != SHIFTS_WORKLOAD.length; shift_idx++) {
		var date_splitted = SHIFTS_WORKLOAD[shift_idx].start_date.split('-');
		var day = date_splitted[2];
		if(day < 0)
			day = '0' + day;
		var month = date_splitted[1];
		for(var wl_idx = 0; wl_idx != SHIFTS_WORKLOAD[shift_idx].workload.length; wl_idx++) {
			var the_shift = SHIFTS_WORKLOAD[shift_idx].workload[wl_idx];
			var row_id = 1 + the_shift['job_id'];
			var cell = $('#cr' + row_id + 'd' + day + 'm' + month);
			shifts_in_day = 0;
			if(cell.text() != '')
				shifts_in_day = parseInt(cell.text());
			console.log(shifts_in_day);
			cell.text(shifts_in_day + the_shift.total);
		}
	}
	$('table th:first-child').addClass('first-col');
	$('table td:first-child').addClass('first-col');
}

OutRequests['shifts-workload']({
	data: {
		"request_id": request_id,
	},
	success: function (result) {
		init_confirmed_shifts_table(result);
	},
	error: function (result) {}
});