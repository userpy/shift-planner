// Пользовательские функции

// Количество дней за период
var getDaysInPeriod = function(start, end) {
	var oneDay = 24*60*60*1000;
	var diffDays = Math.round(Math.abs((start.getTime() - end.getTime())/(oneDay)));
	return diffDays;
};


function Switch(id) {
	if (outsourcing_request_state != 'accepted') return
	var div = document.getElementById(id);
	var shift_index = div.getAttribute("shift_index");
	if (shifts[shift_index].state != 'reject') {
		div.setAttribute("style", "background-color: lightcoral;");
		shifts[shift_index].state = 'reject';
	} else {
		div.setAttribute("style", "background-color: lightgreen;");
		shifts[shift_index].state = 'accept';
	}
}

