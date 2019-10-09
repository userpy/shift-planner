
//Создание таблицы
function SetTableValues() {
	var daysInPeriod = getDaysInPeriod(SC_NEWER_DATE, SC_OLDER_DATE);
	var sizeRows = jobs.length;

	var table_ordinary = $('#tab');
	var all_tables = $('#tab, #confirmed_shifts_table');
	var bodyAppended = false;
	/// РЕФАКТОРИНГ
	// Проход по строкам - количество функций (должностей)
	for(var row_id = 0; row_id < sizeRows + 2; row_id++) {
		var row = null;
		// Если первая строка, добавляем только шапку
		if(row_id == 0) {
			all_tables.append('<thead></thead>');
			all_tables.find('thead').append('<tr id="tr' + row_id + '"></tr>');
			row = $('#tab thead tr').last();
		}
		// Если не первая, то добавляем остальную часть тела
		else {
			if(row_id == 1)
				all_tables.append('<tbody></tbody>');
			var row_to_append = '<tr id="tr' + row_id + '"></tr>';
			all_tables.find('tbody').append(row_to_append);
			row = $('#tab tbody tr').last();
		}
		// Заполнение тела таблиц
		for(var col_id = 0; col_id < daysInPeriod + 2; col_id++) {
			if(row_id == 0)
				if(col_id == 0)
					var cell = row.append('<th id="r' + row_id + 'd' + col_id + '"></th>');
				else {
					var date = new Date(SC_OLDER_DATE);
					date.setDate(date.getDate() + col_id - 1);
					var dd = date.getDate();
					if(dd < 10)
						dd = '0' + dd;
					var mm = date.getMonth() + 1;
					if(mm < 10)
						mm = '0' + mm;
					var cell = row.append('<th id="r' + row_id + 'd' + dd + 'm' + mm + '"></th>');
				}
			else {
				if(col_id == 0)
					var cell = row.append('<td id="r' + row_id + 'd' + col_id + '"></td>');
				else {
					var date = new Date(SC_OLDER_DATE);
					date.setDate(date.getDate() + col_id - 1);
					var dd = date.getDate();
					if(dd < 10)
						dd = '0' + dd;
					var mm = date.getMonth() + 1;
					if(mm < 10)
						mm = '0' + mm;
					var cell = row.append('<td id="r' + row_id + 'd' + dd + 'm' + mm + '"></td>');
				}
			}
			if(row_id == 0 && col_id > 0) {
				var date = new Date(SC_OLDER_DATE);
				date.setDate(date.getDate() + col_id - 1);
				var dd = date.getDate();
				var mm = date.getMonth();
				if(mm < 10)
					mm = '0' + mm + 1;
				var str = dd;
				$('#tab th').last().append(str);
			}
		}
	}
	// Длительность смен за день
	for (var x=0; x < days.length; x++){
		days[x]['total_minutes']=0;
		for (var y=0; y < shifts.length; y++){
			if(shifts[y]['start']==days[x]['start'] && shifts[y]['state'] != 'delete'){
				days[x]['total_minutes'] += shifts[y]['worktime']
			}
		}
		mins = days[x]['total_minutes'] % 60;
		hours = (days[x]['total_minutes'] - mins) / 60;
		if (mins < 10) mins = '0' + mins;
		if (hours < 10) hours = '0' + hours;
		days[x]['total_time'] = hours + ':' + mins;
	}
	// Длительность смен по должности
	for(var x = 0; x < jobs.length; x++) {
		jobs[x]['total_minutes'] = 0;
		for(var y = 0; y < shifts.length; y++) {
			if(shifts[y]['job_id'] == jobs[x]['job_id'] && shifts[y]['state'] != 'delete') {
				jobs[x]['total_minutes'] += shifts[y]['worktime']
			}
		}
		mins = jobs[x]['total_minutes'] % 60;
		hours = (jobs[x]['total_minutes'] - mins) / 60;
		if(mins < 10) mins = '0' + mins;
		if(hours < 10) hours = '0' + hours;
		jobs[x]['total_time'] = hours + ':' + mins;
	}

	var total_time = 0;
	for(var x = 0; x < days.length; x++)
		total_time += days[x]['total_minutes'];
	$('#r' + (sizeRows + 1) + 'd0').text(total_time / 60);

	//Заголовки специальностей
	for(var row_id = 0; row_id < sizeRows; row_id++) {
		si = row_id + 1;
		$('#r' + [si] + 'd0').html(jobs[row_id]['job_name'] + "<br/>" + jobs[row_id]['total_time']);
	}
	for(var col_id = 0; col_id != days.length; col_id++) {
		si = col_id + 1;
		st = sizeRows + 1; // Строка количества часов на день

		day_date = days[col_id]['start'];

		var splitted = day_date.split('.');
		day_idx = splitted[0];
		month_idx = splitted[1];

		var value = parseInt(days[col_id]['total_time'].split(':')[0]);
		if(value == 0)
			value = '';
		$('#r' + st + "d" + day_idx + 'm' + month_idx).html(value);

		for(var row_id = 0; row_id < jobs.length; row_id++) {
			sj = row_id + 1;
			//Интервалы по специальности
			for(var x = 0; x < shifts.length; x++) {
				if(shifts[x]['job_id'] == jobs[row_id]['job_id'] && shifts[x]['start'] == days[col_id]['start']) {
					var td_id = $('#r' + sj + "d" + day_idx + 'm' + month_idx);

					var div = $('<div></div>');
					div.attr('id', si + "" + +"_" + shifts[x]['id']);
					div.addClass('shift-cell tooltip-cell');

					var state = shifts[x]['state'];
					if(state == 'wait' || state == 'accept') {
						div.attr('style', 'background-color: lightgreen;');
					} else if(state == 'reject') {
						div.attr('style', 'background-color: lightcoral;');
					} else if(state == 'delete') {
						div.attr('style', 'background-color: #eaeaea;');
					}
					div.attr("shift", shifts[x]['id']);
					div.attr("shift_index", x);


					var another_period = '';
					var start_full = shifts[x]['period'].split(' - ')[0];
					var end_full = shifts[x]['period'].split(' - ')[1];
					start = '<p class="date">' + start_full.split(':')[0] + '</p>';
					end = '<p class="date">' + end_full.split(':')[0] + '</p>';

					div.html(start + end);
					var tooltip = "";
					if(state == 'delete') {
						tooltip += '<span class="tooltip-for-cell">Удалено клиентом<br/>' + start_full + ' — ' + end_full + '</span>';
					} else
						tooltip += '<span class="tooltip-for-cell">' + start_full + ' — ' + end_full + '</span>';
					div.append(tooltip);

					if( outsourcing_request_state == 'accepted' && outsource_enable){
						if(state != 'delete'){
							div.on("click", function() {
								Switch(this.getAttribute('id'))
							})
						}
					}
					td_id.append(div);
				}
			}
		}
	}
}

window.onload(SetTableValues());
$('table th:first-child').addClass('first-col');
$('table td:first-child').addClass('first-col');