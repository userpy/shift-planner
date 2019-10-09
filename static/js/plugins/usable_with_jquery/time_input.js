aeTimeInput = function(time, elem) {
	elem = createOrCheckTag(elem, 'input', 'TimeInput: ')
	elem.classList.add('time-input')
	elem.placeholder = 'чч:мм'
	elem.addEventListener('change', aeTimeInput.onChange)

	for (var attr in aeTimeInput.ext) elem[attr] = aeTimeInput.ext[attr]
	elem._time = elem.fixTime(time||0)
	elem._isValid = true
	elem.value = elem.stringifyTime(elem._time)
	return elem
}

aeTimeInput.ext = {
	isTimeValid: function(str) {
		return /^\d\d?(:\d\d?)?$/.test(str)
	},
	stringifyTime: function(time) {
		return (time/Date.hour|0).toLen(2) +':'+ ((time/Date.minute)%60).toLen(2)
	},
	parseTime: function(str) {
		if (/^\d\d?$/.test(str)) str+=':00'
		return Date.delta.fromHM(str)
	},
	fixTime: function(time) {
		return ((time + Date.day) % Date.day).floor(15*Date.minute)
	},

	isValid: function(){
		return this._isValid
	},
	getHours: function(){
		return this._time/Date.hour|0
	},
	getMinutes: function(){
		return (this._time/Date.minute)%60
	},
	getTime: function(){
		return this._time
	},
	setTime: function(time, silent, extra_data) {
		time = this.fixTime(time)
		this.value = this.stringifyTime(time)
		if (this._time == time) return
		this._time = time
		this.classList.remove('validation-error')
		if (!silent) {
			var detail = extra_data || {}
			detail.type = 'custom'
			this.throwEvent('change', detail, true)
		}
	}
}

aeTimeInput.onChange = function(e) {
	if (e.detail && e.detail.type == 'custom') return //it's our re-thrown event, do nothing
	e.stopImmediatePropagation()

	var wasValid = this._isValid
	this._isValid = this.isTimeValid(this.value)
	this.classList.toggle('validation-error', !this._isValid)
	if (this._isValid) this.setTime(this.parseTime(this.value), false)
	if (this._isValid != wasValid) this.throwEvent('validation', {type:'custom'}, true)
}


/*
var input = aeTimeInputWithDropdown(12..hours + 30..minutes)
input.addEventListener('change', function(){ console.log(this.getHours(), this.getMinutes()) })
ae$('.smth').appendChild(input)
*/
aeTimeInputWithDropdown = function(time, wrap) {
	wrap = createOrCheckTag(wrap, 'div', 'TimeInputWithDropdown: ')
	wrap.classList.add('time-input-with-dropdown')
	wrap.classList.add('buttons-group')

	wrap._timeInput = aeTimeInput(time)
	wrap._popup = null

	wrap._timeInput.addEventListener('change', aeTimeInputWithDropdown.onChange.bind(wrap))
	wrap._timeInput.addEventListener('validation', aeTimeInputWithDropdown.onValidation.bind(wrap))
	wrap.appendChild(wrap._timeInput)

	var dropdown = document.createElement('div')
	dropdown.className = 'button dropdown fa fa-caret-down'
	dropdown.addEventListener('click', aeTimeInputWithDropdown.showPopup.bind(wrap))
	wrap.appendChild(dropdown)

	for (var attr in aeTimeInputWithDropdown.ext) wrap[attr] = aeTimeInputWithDropdown.ext[attr]

	Object.defineProperty(wrap, 'disabled', {
		get: function(v){
			return this._timeInput.disabled
		},
		set: function(v){
			this._timeInput.disabled = !!v
			v ? this.setAttribute('disabled', '') : this.removeAttribute('disabled')
			this.ae$('.dropdown').classList.toggle('disabled', v)
		}
	})
	if (wrap.getAttribute('disabled') != null) wrap.disabled = true

	return wrap
}

aeTimeInputWithDropdown.ext = {}

aeTimeInputWithDropdown.ext.isValid = function() {
	return this._timeInput.isValid()
}
aeTimeInputWithDropdown.ext.getHours = function() {
	return this._timeInput.getHours()
}
aeTimeInputWithDropdown.ext.getMinutes = function() {
	return this._timeInput.getMinutes()
}
aeTimeInputWithDropdown.ext.getTime = function() {
	return this._timeInput.getTime()
}
aeTimeInputWithDropdown.ext.setTime = function(time, silent) {
	this._timeInput.setTime(time, false, {silent_dropdown: silent})
}
aeTimeInputWithDropdown.ext.closePopup = function() {
  this._popup && this._popup.close()
}
aeTimeInputWithDropdown.showPopup = function() {
	if (this._popup) return //already shown
	if (this.ae$('.dropdown').classList.contains('disabled')) return
	setTimeout(function(){
		this._popup = aeButtonTimeInput.showAsPopup(this._timeInput, this.getTime())
		this._popup.wrap.addEventListener('change', aeTimeInputWithDropdown.onPopupChange.bind(this))
		this._popup.wrap.addEventListener('close', aeTimeInputWithDropdown.onPopupClose.bind(this))
	}.bind(this), 1)
}
aeTimeInputWithDropdown.onPopupChange = function(e) {
	e.stopPropagation()
	this._timeInput.setTime(this._popup.ti.getTime(), false, {day_delta: e.detail.day_delta})
}
aeTimeInputWithDropdown.onPopupClose = function(e) {
	this._popup = null
}

aeTimeInputWithDropdown.onChange = function(e) {
	if (e.detail.silent_dropdown) e.stopPropagation()
	if (this._popup) this._popup.ti.setTime(this.getTime())
}
aeTimeInputWithDropdown.onValidation = function(e) {
	this.classList.toggle('validation-error', !this.isValid())
}
