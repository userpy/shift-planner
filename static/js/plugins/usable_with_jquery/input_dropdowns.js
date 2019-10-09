/*
var input = ae$('.small-time-input')
vat popup = aeButtonTimeInput.showAsPopup(input, 12*Date.hour + 30*Date.minute)
popup.wrap.addEventListener('change', function(){ console.log(popup.ti.hour()) })
popup.wrap.addEventListener('close', ...)
*/
aeButtonTimeInput.showAsPopup = function(elem, time) {
	var res = {}
	showPopupUnder(elem, function(wrap, close){
		res.wrap = wrap
		res.ti = new aeButtonTimeInput(wrap, time)
		res.close = close
	})
	return res
}


/*
var input = ae$('.small-range-input')
vat popup = aeButtonTimeInput.showAsRangePopup(input, 12*Date.hour + 30*Date.minute, 15*Date.hour)
popup.wrap.addEventListener('change', function(){ console.log(popup.tis[1].hour()) })
popup.wrap.addEventListener('close', ...)
*/
aeButtonTimeInput.showAsRangePopup = function(elem, start_time, end_time) {
	var res = {wrap:null, tis:[null,null]}

	showPopupUnder(elem, function(wrap){
		res.wrap = wrap
		wrap.classList.add('button-time-interval-input')
		wrap.innerHTML = aeButtonTimeInput.showAsRangePopup.template
		res.tis[0] = new aeButtonTimeInput(wrap.ae$('.start-time'), start_time)
		res.tis[1] = new aeButtonTimeInput(wrap.ae$('.end-time'),   end_time)
	})

	function onChange(){ res.wrap.throwEvent('change') }
	res.tis[0].wrap.addEventListener('change', onChange)
	res.tis[1].wrap.addEventListener('change', onChange)

	return res
}
aeButtonTimeInput.showAsRangePopup.template = '\
<div class="start-time"></div>\
<div class="interval-separator">—</div>\
<div class="end-time"></div>'
