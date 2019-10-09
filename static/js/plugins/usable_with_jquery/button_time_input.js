/*
var wrap = ae$('.here-time-input-with-buttons-will-be')
var ti = new aeButtonTimeInput(wrap, 12*Date.hour + 30*Date.minute)
wrap.addEventListener('change', function(){ console.log(ti.hours(), ti.minutes()) })
*/
aeButtonTimeInput = function ButtonTimeInput(wrap, time) {
	this.wrap = wrap
	this.time = time
	this.minute_step = 15

	this.time = this.time.round(this.minute_step * Date.minute)

	this.wrap.classList.add('button-time-input')
	this.wrap.innerHTML = aeButtonTimeInput.template

	this.wrap.ae$('.minutes-wrap .button.inc').onclick = this.incMinutes.bind(this)
	this.wrap.ae$('.minutes-wrap .button.dec').onclick = this.decMinutes.bind(this)
	this.wrap.ae$('.hours-wrap .button.inc').onclick = this.incHours.bind(this)
	this.wrap.ae$('.hours-wrap .button.dec').onclick = this.decHours.bind(this)

	this.update()
}

aeButtonTimeInput.template = '\
<div class="hours-wrap">\
	<button class="button inc fa fa-caret-up"></button>\
	<div class="value">0</div>\
	<button class="button dec fa fa-caret-down"></button>\
</div>\
<div class="separator">:</div>\
<div class="minutes-wrap">\
	<button class="button inc fa fa-caret-up"></button>\
	<div class="value">00</div>\
	<button class="button dec fa fa-caret-down"></button>\
</div>'

aeButtonTimeInput.prototype.getHours = function() {
	return this.time / Date.hour |0
}

aeButtonTimeInput.prototype.getMinutes = function() {
	return (this.time/Date.minute|0) % 60
}

aeButtonTimeInput.prototype.getTime = function(time) {
	return this.time
}

aeButtonTimeInput.prototype.setTime = function(time) {
	this.update(time - this.time)
}

aeButtonTimeInput.prototype.updateUI = function() {
	this.wrap.ae$('.hours-wrap .value').textContent = this.getHours()
	this.wrap.ae$('.minutes-wrap .value').textContent = this.getMinutes().toLen(2)
}

aeButtonTimeInput.prototype.fixTime = function() {
	this.time = (this.time + Date.day) % Date.day
}

aeButtonTimeInput.prototype.update = function(timedelta, is_manual) {
	timedelta = timedelta || 0
	this.time += timedelta
	var day_delta = 0
	if (is_manual) {
		if (timedelta < 0 && this.time < 0) day_delta = -1
		if (timedelta > 0 && this.time >= Date.day) day_delta = 1
	}
	this.fixTime()
	this.updateUI()
	if (timedelta != 0) this.wrap.throwEvent('change', {day_delta: day_delta})
}

aeButtonTimeInput.prototype.incMinutes = function(){ this.update( this.minute_step * Date.minute, true) }
aeButtonTimeInput.prototype.decMinutes = function(){ this.update(-this.minute_step * Date.minute, true) }
aeButtonTimeInput.prototype.incHours = function(){ this.update( Date.hour, true) }
aeButtonTimeInput.prototype.decHours = function(){ this.update(-Date.hour, true) }