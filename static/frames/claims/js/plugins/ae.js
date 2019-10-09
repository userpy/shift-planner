/*
* 
* https://github.com/LookNya/aejs
* Набор полезных функция для работы с ДОМом и объектом даты
*/

$ = document.querySelector.bind(document)
$$ = document.querySelectorAll.bind(document)
Element.prototype.$ = Element.prototype.querySelector
Element.prototype.$$ = Element.prototype.querySelectorAll
Element.prototype.remove = function() {
	this.parentElement.removeChild(this)
}
Element.prototype.offsetFrom = function(elem) {
	var me = this.getBoundingClientRect()
	var other = elem.getBoundingClientRect()
	return {left: me.left-other.left, top: me.top-other.top}
}
Element.prototype.findElemByClass = function(targetClass){
	var elem = this
	while(elem && elem.classList){
		if (elem.classList.contains(targetClass)) return elem
		elem = elem.parentElement
	}
	return null
}
Element.prototype.findElemByTag = function(tagName){
	var elem = this
	while(elem && elem.classList){
		if (elem.tagName.toLowerCase() == tagName.toLowerCase()) return elem
		elem = elem.parentElement
	}
	return null
}
// Просто ищет элемент по цепочке родителей (начиная с самого элемента)
// true, если находит, false в противном случае
Element.prototype.findElem = function(elem){
	var cur = this
	while(cur){
		if (cur === elem) return true
		cur = cur.parentElement
	}
	return false
}
Element.prototype.getRuDate = function(){
	var elem = this
	var text = elem.textContent
	if(this.tagName.toLowerCase() == 'input') text = elem.value
	var date = new Date.fromDMY(text)
	if(date == 'Invalid Date') throw new Error(text +' is not a valid Date')
	return date
}
Element.prototype.highlight = function(delay){
	var delay = delay || 700
	var elem = this
	if(!elem.classList.contains('highlighted')){
		elem.classList.add('highlighted')
		setTimeout(function(){
			elem.classList.remove('highlighted')
		}, delay)
	}
}
Element.prototype.scrollTo = function(target){//нет проверки, является ли таргет дочкой ноды
	console.warn('scrollTo is depricated, use element.scrollIntoView() instead')
	var parent = this
	var parentTop = parent.getBoundingClientRect().top
	var targetTop = target.getBoundingClientRect().top
	//console.log(targetTop - parentTop  - parent.scrollTop)
	parent.scrollTop = (targetTop - parentTop + parent.scrollTop)
}
Element.prototype.empty = function(){// тоже самое, что иннерХТМЛ = ""
	if(!this.firstChild) return this// alreadt empty
	var range = document.createRange()
	range.setStartBefore(this.firstChild)
	range.setEndAfter(this.lastChild)
	range.deleteContents()
	return this
}
Object.defineProperty(NodeList.prototype, 'classList', { get: function(){
	return {
		_elems: this,
		add: function(){
			for (var i=0; i<this._elems.length; i++) {
				var l = this._elems[i].classList
				l.add.apply(l, arguments)
			}
		},
		remove: function(){
			for (var i=0; i<this._elems.length; i++) {
				var l = this._elems[i].classList
				l.remove.apply(l, arguments)
			}
		},
		toggle: function(){
			for (var i=0; i<this._elems.length; i++) {
				var l = this._elems[i].classList
				l.toggle.apply(l, arguments)
			}
		}
	}
} })
NodeList.prototype.forEach = Array.prototype.forEach
NodeList.prototype.indexOf = Array.prototype.indexOf
NodeList.prototype.filter = Array.prototype.filter
NodeList.prototype.map = Array.prototype.map
NodeList.prototype.reduce = Array.prototype.reduce

FileList.prototype.forEach = Array.prototype.forEach
FileList.prototype.indexOf = Array.prototype.indexOf
FileList.prototype.filter = Array.prototype.filter
FileList.prototype.map = Array.prototype.map
FileList.prototype.reduce = Array.prototype.reduce

Object.defineProperty(NodeList.prototype, 'first', { get: function(){ return this[0] } })
Object.defineProperty(NodeList.prototype, 'last', { get: function(){ return this[this.length-1] } })
createEl = function(params){
	return  document.createElement(params)
}
//ИЕ11 передаёт привет
;(function () {
	try {
		new window.CustomEvent('test', {detail: 0}) // в ИЕ11 это вызовет ошибку
		return
	} catch(e) {}

	function CustomEvent(e, params) {
		params = params || { bubbles: false, cancelable: false, detail: undefined }
		var evt = document.createEvent('CustomEvent')
		evt.initCustomEvent(e, params.bubbles, params.cancelable, params.detail)
		return evt
	}

	CustomEvent.prototype = window.Event.prototype
	window.CustomEvent = CustomEvent
})()

function onceOnEvent(name, func){
	function handler(e){
		this.removeEventListener(name, handler)
		func.call(this, e)
	}
	this.addEventListener(name, handler)
}


// EventTarget есть не везде, так что...
window.constructor.prototype.throwEvent = function(name, data, bubbles){
	if(!data) data = {}
	var myEvent = new CustomEvent(name, {
		detail: data,
		bubbles: !!bubbles,
	})
	this.dispatchEvent(myEvent)
}
Element.prototype.throwEvent = window.constructor.prototype.throwEvent

/*Array.prototype.sum = function(f) {
	var sum = 0
	for (var i=0; i<this.length; i++) sum += f(this[i], i, this)
	return sum
}*/
if (!Array.prototype.find) {
	Object.defineProperty(Array.prototype, 'find', {
		value: function(predicate) {
			var thisArg = arguments[1]
			for (var i = 0; i < this.length; i++) {
				if (predicate.call(thisArg, this[i], i, this))
					return this[i]
			}
			return undefined;
		}
	})
}
Object.defineProperty(Array.prototype, 'simpleIniq', {
  value: function() {
		return this.filter(function(value, index, array){ 
			return array.indexOf(value) == index;
		})
  }
})

Object.defineProperty(Array.prototype, 'remove', {
	value: function(elem) {
		var ind = this.indexOf(elem)
		if (ind == -1) return false
		this.splice(ind, 1)
		return true
	}
})
Object.defineProperty(Array.prototype, 'pushIfNotContains', {
	value: function(elem) {
		for(i=0; i<this.length; i++){
			if(this[i]==elem) return false
		}
		this.push(elem)
		return true
	}
})
Object.defineProperty(Array.prototype, 'identicalTo', {
	value: function(newArr) {
		if( newArr.length != this.length) return false
		for(i=0; i<this.length; i++){
			if(this[i] != newArr[i]) return false
		}
		return true
	}
})
Object.defineProperty(Array.prototype, 'first', { get: function(){ return this[0] } })
Object.defineProperty(Array.prototype, 'last', { get: function(){ return this[this.length-1] } })

;[Array, Int8Array, Int32Array, Float64Array].forEach(function(TypedArr){
	if (!('fill' in TypedArr.prototype)) TypedArr.prototype.fill = function(value) {
		for (var i=0; i<this.length; i++) this[i] = value
	}

	if (!('lastIndexOf' in TypedArr.prototype)) TypedArr.prototype.lastIndexOf = function(value /*, fromIndex*/) {
		'use strict'
		if (this === undefined || this === null)
			throw new TypeError('"this" is null or not defined')

		var arr = Object(this)
		var len = arr.length|0
		if (len === 0)
			return -1

		var n = len - 1
		if (arguments.length > 1) {
			n = Number(arguments[1])
			if (n != n) {
				n = 0
			} else if (n != 0 && n != (1 / 0) && n != -(1 / 0)) {
				n = (n > 0 || -1) * Math.floor(Math.abs(n))
			}
		}

		var k = n>=0 ? Math.min(n, len-1) : Math.max(len-Math.abs(n), 0)
		for (; k >= 0; k--)
			if (k in arr && arr[k] === value)
				return k
		return -1
	}

	if (!('indexOf' in TypedArr.prototype)) TypedArr.prototype.indexOf = function(value /*, fromIndex*/) {
		if (this == null)
			throw new TypeError('"this" is null or not defined');

		var arr = Object(this)
		var len = arr.length | 0;

		if (len === 0)
			return -1

		var n = 0
		if (arguments.length > 1) {
			n = Number(arguments[1])
			if (n != n) {
				n = 0
			} else if (n != 0 && n != (1 / 0) && n != -(1 / 0)) {
				n = (n > 0 || -1) * Math.floor(Math.abs(n))
			}
		}

		if (n >= len)
			return -1

		var k = Math.max(n>=0 ? n : len-Math.abs(n), 0)
		for (; k < len; k++)
			if (k in arr && arr[k] === value)
				return k
		return -1
	}
})

String.prototype.capitalizeFirstLetter = function() {
	return this.charAt(0).toUpperCase() + this.slice(1);
}
String.prototype.splice = function(index, howManyToDelete, stringToInsert){
	var characterArray = this.split('')
	Array.prototype.splice.apply(characterArray, arguments)
	return (characterArray.join(''))
}
if (!String.prototype.repeat) {
	String.prototype.repeat = function(count) {
		if (count < 0) throw new RangeError('repeat count must be non-negative')
		if (count == Infinity) throw new RangeError('repeat count must be less than infinity')
		count = Math.floor(count)
		if (this.length == 0 || count == 0) return ''
		var str = this
		var res = ''
		for (;;) {
			if ((count & 1) == 1) res += str
			count >>>= 1
			if (count == 0) break
			str += str
		}
		return res
	}
}
isIntersects = function(start1, end1, start2, end2){
	if (start1 < end2 && end1 > start2) return true
	return false
}
Date.prototype.startOfDay = function() {
	var new_date = new Date(this)
	new_date.setHours(0, 0, 0, 0)
	return new_date
}
Date.prototype.startOfWeek = function() {
	var new_date = new Date(this)
	new_date.setHours(0, 0, 0, 0)
	var weekday = new_date.getDay()
	new_date.setDate(new_date.getDate() - (weekday==0 ? 6 : weekday-1))
	return new_date
}
Date.prototype.endOfWeek = function() {
	var new_date = new Date(this)
	new_date.setHours(0, 0, 0, 0)
	var weekday = new_date.getDay()
	new_date.setDate(new_date.getDate() + (weekday==0 ? 0 : 7-weekday))
	return new_date
}
Date.prototype.startOfMonth = function() {
	var new_date = new Date(this)
	new_date.setHours(0, 0, 0, 0)
	new_date.setDate(1)
	return new_date
}
Date.prototype.endOfMonth = function() {
	var date = this.startOfMonth()
	return new Date(date.getFullYear(), date.getMonth()+1, 0)
}
/*Date.prototype.startOfYear = function() {
	var new_date = this.startOfMonth()
	new_date.setMonth(0)
	return new_date
}*/
Date.prototype.offsetFrom = function(date) {
	// без информации о таймзоне
	var utc0 = Date.UTC(this.getFullYear(), this.getMonth(), this.getDate());
	var utc1 = Date.UTC(date.getFullYear(), date.getMonth(), date.getDate());
	return utc0 - utc1
}
Date.prototype.daysOffsetFrom = function(date) {
	return Math.floor(this.offsetFrom(date) / Date.day)
}
Date.prototype.weeksOffsetFrom = function(date) {
	return Math.floor(this.offsetFrom(date) / Date.week)
}
Date.prototype.monthsOffsetFrom = function(date) {
	return (this.getFullYear() - date.getFullYear())*12 + (this.getMonth() - date.getMonth())
}
Date.prototype.hms = function() {
	var hours = this.getHours()
	var minutes = "0" + this.getMinutes()
	var seconds = "0" + this.getSeconds()
	return hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2)
}
Date.prototype.hm = function() {
	var hours = this.getHours()
	var minutes = "0" + this.getMinutes()
	return hours + ':' + minutes.substr(-2)
}
Date.prototype.hmWords = function() {
	var hours = this.getHours()
	var separator = ''
	var minutes = '' + this.getMinutes()
	if(hours == 0 && minutes == 0) return '0 ч.'
	if(hours != 0 && minutes != 0) separator = ' '
	return (hours!=0 ? hours + ' ч.' : '') +separator+ (minutes!=0 ? minutes.substr(-2) + ' м.' : '')
}
Date.prototype.dayWords = function(isShort){
	var day = this.getDay()
	var dayNames = isShort ?  Date.dayNamesShortUTC : Date.dayNamesUTC
	return dayNames[day]
}
Date.prototype.monthWords = function(params){
	var params = params || {}
	var monthNames = Date.monthNames
	if(params.genetive) monthNames = Date.monthNamesGenitive
	var month = this.getMonth()
	return monthNames[month]
}
Date.prototype.dayAndHours = function(isShort){
	var day = this.dayWords(isShort)
	var time = this.hm()
	return day +' '+ time
}
Date.prototype.h = function() {
	var hours = "0" + this.getHours()
	return hours.substr(-2)
}
Date.prototype.m = function() {
	var minutes = "0" + this.getMinutes()
	return minutes.substr(-2)
}
Date.prototype.to15minutes = function(){
	return this.getHours() * 4 + this.getMinutes() / 15
}

Date.prototype.dmy = function() {
	return this.getDate().toLen(2) +'.'+ (this.getMonth()+1).toLen(2) +'.'+ this.getFullYear()
}
Date.prototype.dm = function() {
	return this.getDate().toLen(2) +'.'+ (this.getMonth()+1).toLen(2)
}
Date.prototype.dmWords = function() {
	return ''+this.getDate() +' '+ this.monthWords({'genetive':true})
}
Date.prototype.toISODateString = function() {
	return this.getFullYear() +'-'+ (this.getMonth()+1).toLen(2) +'-'+ this.getDate().toLen(2)
}
Date.prototype.isDayStart = function() {
	return this.getHours()==0 && this.getMinutes()==0 && this.getSeconds()==0 && this.getMilliseconds()==0
}
Date.prototype.isWeekStart = function() {
	return this.getDay()==1 && this.isDayStart()
}
// Возвращает номер дня недели по ISO 86001 (1 - понедельник, 7 - воскресенье)
Date.prototype.getISODay = function() {
	var day = this.getDay()
	return day==0 ? 7 : day
}
// Возвращает кол-во минут с начала суток
Date.prototype.getDayMinues = function (){
	return this.getHours() * 60 + this.getMinutes()
}
// Возвращает кол-во миллисекунд с начала суток
Date.prototype.getDayTime = function() {
	return this.getHours()*Date.hour +
		this.getMinutes()*Date.minute +
		this.getSeconds()*Date.second +
		this.getMilliseconds()
}
// Возвращает номер текущей недели по ISO 86001
Date.prototype.getISOWeekNumber = function() {
	var date = new Date(this)
	var day = (this.getDay()+6) % 7
	date.setDate(date.getDate()-day + 3)
	var cur_thursday = date.getTime() //четверг в текущей неделе

	date.setMonth(0, 1) //первое января
	date.setMonth(0, 1 + ((4 - date.getDay()) + 7) % 7) //четверг той недели, на которой первое января
	var first_thursday = date.getTime() //четверг в первой неделе года

	return 1 + Math.ceil((cur_thursday - first_thursday) / Date.week)
}
// Возвращает год, к которому относится текущая неделя по ISO 86001
Date.prototype.getISOWeekYear = function() {
	var date = new Date(this)
	var day = (this.getDay()+6) % 7
	date.setDate(date.getDate()-day + 3)
	return date.getFullYear()
}

Date.monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
Date.monthNamesGenitive = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря']
Date.dayNames = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб']
Date.dayNamesShortUTC = ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб']
Date.dayNamesUTC = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
Date.daysInMonth = function(year, month){ return new Date(year, month+1, 0).getDate() }
Date.fixDay = function(day) {
	return day==0 ? 6 : day-1
}
Date.fromDMY = function(str) {
	var dmy = str.split(/\D/)
	return new Date(+dmy[2], +dmy[1]-1, +dmy[0])
}
Date.fromYMD8601 = function(str) {
	var ymd = str.split('-')
	return new Date(+ymd[0], +ymd[1]-1, +ymd[2])
}
Date.mustBeMonth = function(start_dtime, end_dtime) {
	var start = new Date(start_dtime), end = new Date(end_dtime)
	if (start.startOfMonth().getTime() != start_dtime || start.endOfMonth().getTime()+Date.day != end_dtime)
		throw new Error('expected monthly interval, got: '+ Date.dtimeDebug(start) +' - '+ Date.dtimeDebug(end))
}
Date.dtimeDebug = function(dtime) {
	var d = new Date(dtime)
	return d.dmy() +' '+ d.hms() +' ('+ d.getTime() +')'
}
Date.delta = {
	h: function(timedelta){
		if (timedelta < 0) timedelta*=-1
		return timedelta/60/60/1000|0
	},
	m: function(timedelta){
		if (timedelta < 0) timedelta*=-1
		return (timedelta/60/1000|0)%60
	},
	hmFloat: function(timedelta){
		var value = timedelta / Date.hour
		var floatValue = (value ^ 0) === value ? value : value.toFixed(2)
		return floatValue
	},
	hm: function(timedelta){
		var prefix = ''
		if (timedelta < 0){ timedelta*=-1; prefix='-' }
		return prefix+(timedelta/60/60/1000|0).toLen(2) + ':' + ((timedelta/60/1000|0)%60).toLen(2)
	},
	fromHM: function(str){
		var hm = str.split(':')
		return (+hm[0]).hours + (+hm[1]).minutes
	},
	hmWords: function(timedelta) {
		var hours = Date.delta.h(timedelta)
		var minutes = Date.delta.m(timedelta)
		var separator = ''
		if(hours == 0 && minutes == 0) return '0 ч.'
		if(hours != 0 && minutes != 0) separator = ' '
		return (hours!=0 ? hours + ' ч.' : '') +separator+ (minutes!=0 ? minutes +' м.' : '')
	},
	dayWords: function(timedelta){
		var dNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
		var dayIndex = Math.floor(timedelta / Date.day) %7
		return dNames[dayIndex]
	},
	dayAndHours: function(timedelta) {
		var day = Date.delta.dayWords(timedelta)
		var hm = Date.delta.hm(timedelta % Date.day)
		return day + ' ' + hm
	}
}
Date.second = 1000
Date.minute = Date.second * 60
Date.hour = Date.minute * 60
Date.day = Date.hour * 24
Date.week = Date.day * 7
/*Date.interval = {
	isInsideOf: function(start_dtime, end_dtime, obj) {
		return start_dtime >= obj.start_dtime && end_dtime <= obj.end_dtime
	}
}*/
Date.splitMonthIntoWeeks = function(month_start_dtime) {
	var start_dtime = month_start_dtime
	var end_dtime = new Date(start_dtime).endOfMonth().getTime()
	var daysInMonth = (end_dtime - start_dtime) / 1..day
	var weekData = []
	var count = 0
	for(var i = start_dtime; i<=end_dtime; start_dtime += 7..day){
		var startDay = Date.fixDay(new Date(i).getDay())
		var endDate = i + (7-startDay-1)*1..day
		if(endDate > end_dtime) endDate = end_dtime
		weekData.push(genWeekItem(i, endDate, count))
		i = endDate + 1..day
		count++
	}
	return weekData
	function genWeekItem(wStartDate, wEndDate, number){
		return {
			ISOWeekNumber: new Date(wStartDate).getISOWeekNumber(), 
			start_dtime: wStartDate,
			end_dtime: wEndDate + 1..day, //начало последнего дня недели + день
			length: (wEndDate - wStartDate) / 1..day + 1,
			number: number,
		}
	}
}
Number.prototype.round = function(base) {
	return Math.round(this/base)*base
}
Number.prototype.ceil = function(base) {
	return Math.ceil(this/base)*base
}
Number.prototype.floor = function(base) {
	return Math.floor(this/base)*base
}
Number.prototype.toLen = function(len) {
	var res = ''+this
	while (res.length < len) res = '0'+ res
	return res
}
Number.isInteger = Number.isInteger || function(value) {
	return typeof value === "number" &&
		isFinite(value) &&
		Math.floor(value) === value
}

Object.defineProperties(Number.prototype, {
	'second':  { get: function(){ return this*Date.second } },
	'seconds': { get: function(){ return this*Date.second } },
	'minute':  { get: function(){ return this*Date.minute } },
	'minutes': { get: function(){ return this*Date.minute } },
	'hour':  { get: function(){ return this*Date.hour } },
	'hours': { get: function(){ return this*Date.hour } },
	'day':  { get: function(){ return this*Date.day } },
	'days': { get: function(){ return this*Date.day } },
	'week':  { get: function(){ return this*Date.week } },
	'weeks': { get: function(){ return this*Date.week } },
})

Node.prototype.insertAfter = function(newNode, referenceNode) {
	return referenceNode.parentNode.insertBefore(
		newNode, referenceNode.nextSibling)
}

Object.clear = function(obj) {
	for (var i in obj) delete obj[i]
}
Object.extend = function(oldObj, data) {
	for (var i in data) oldObj[i] = data[i]
}
Object.lazyAttr = function(obj, attrName, func) {
	Object.defineProperty(obj, attrName, {get: function wrap(){
		if (wrap.hasOwnProperty('value'))
			return wrap.value
		wrap.value = func.call(obj)
		return wrap.value
	}})
}
function rd(min, max) {
	var rand = min + Math.random() * (max + 1 - min);
	rand = Math.floor(rand);
	return rand;
}

function download(string, fileName, mimeType) {
	if (navigator.msSaveOrOpenBlob) {
		// ИЕ10+ и Edge (в последнем должен работать a[download], но не работает)
		navigator.msSaveOrOpenBlob(new Blob([string], {type: mimeType}), fileName)
	} else if (/Version\/[\d\.]+.*Safari/.test(navigator.userAgent)) {
		// Safari
		location.href = 'data:'+ mimeType +';charset=utf-8,'+ encodeURIComponent(string) //URL.createObjectURL(blob)
	} else {
		// FF, Chrome, Opera
		var blob = new Blob([string], {type: mimeType})
		var blobURL = URL.createObjectURL(blob)

		var a = document.createElement('a')
		a.href = blobURL
		a.target = '_blank'
		a.setAttribute('download', fileName)
		document.body.appendChild(a)
		a.click()

		setTimeout(function(){
			a.remove()
			URL.revokeObjectURL(blobURL)
		}, 100)
	}
	//window.open('data:attachment/csv;charset=utf-8,' + encodeURIComponent(string))
	//https://github.com/eligrey/FileSaver.js/blob/master/FileSaver.js
	//https://github.com/rndme/download/blob/master/download.js
}

function downloadViaIFrame(iframe, path) {
	if ('src' in iframe) {
		iframe.src = path
	} else { //ИЕ передаёт привет
		iframe.location.href = path
	}
}

function openTabWithGET(path) {
	var a = document.createElement('a')
	a.href = path
	a.target = '_blank'
	document.body.appendChild(a)

	a.click()
	setTimeout(function(){
		a.remove()
	}, 100)
}

// Создаёт и сабмитит POST-форму с target="_blank",
// принимает параметры вида {"ключ": "значение", ...}
function openTabWithPOST(path, params) {
	var form = document.createElement('form')
	form.style.display = 'none'
	form.enctype = 'application/x-www-form-urlencoded'
	form.method = 'POST'
	document.body.appendChild(form)

	form.action = path
	form.target = '_blank'
	//form.setAttribute('target', '_blank')

	for (var key in params) {
		var input = document.createElement('input')
		input.type = 'hidden'
		input.name = key
		input.value = params[key]
		form.appendChild(input)
	}

	form.submit()
	setTimeout(function(){
		form.remove()
	}, 100)
}


// ref: http://stackoverflow.com/a/1293163/2343
// This will parse a delimited string into an array of arrays. The default
// delimiter is the comma, but this can be overriden in the second argument.
// Example:
//   CSVToArray('A;B\n1;2', ';') //[['A', 'B'], ['1', '2']]
function CSVToArray(strData, strDelimiter) {
	strDelimiter = strDelimiter || ','

	// Stor on empty CSV otherwise exec() later will loop on this string.
	if (strData == '') return [['']]

	// Create a regular expression to parse the CSV values.
	var objPattern = new RegExp(
		(
			// Delimiters.
			'(\\' + strDelimiter + '|\\r?\\n|\\r|^)' +
			// Quoted fields.
			'(?:"([^"]*(?:""[^"]*)*)"|' +
			// Standard fields.
			'([^"\\' + strDelimiter + '\\r\\n]*))'
		),
		'gi'
	)

	// Create an array to hold our data. Give the array a default empty first row.
	var arrData = [[]]

	// Create an array to hold our individual pattern matching groups.
	var arrMatches = null

	// If data starts with delimeter like ",smth,other" first match
	// will contain ",smth" without first empty value. Fixing it.
	if (strData[0] === strDelimiter) arrData[0].push('')

	// Keep looping over the regular expression matches until we can no longer find a match.
	while (arrMatches = objPattern.exec(strData)){
		// Get the delimiter that was found.
		var strMatchedDelimiter = arrMatches[1]

		// Check to see if the given delimiter has a length
		// (is not the start of string) and if it matches
		// field delimiter. If id does not, then we know
		// that this delimiter is a row delimiter.
		if (strMatchedDelimiter.length && strMatchedDelimiter !== strDelimiter) {
			// Since we have reached a new row of data, add an empty row to our data array.
			arrData.push([])
		}

		var strMatchedValue
		// Now that we have our delimiter out of the way, let's check to see
		// which kind of value we captured (quoted or unquoted).
		if (arrMatches[2] !== undefined) {
			// We found a quoted value. When we capture this value, unescape any double quotes.
			strMatchedValue = arrMatches[2].replace(/""/g, '"')
		} else {
			// We found a non-quoted value.
			strMatchedValue = arrMatches[3]
		}

		// Now that we have our value string, let's add it to the data array.
		arrData[arrData.length - 1].push(strMatchedValue)
	}

	// Return the parsed data.
	return arrData
}

// Парсит CSV аналогично CSVToArray, но возвращает массив объектов.
// Названия колонок берутся из первой строки.
function CSVToObjArray(strData, strDelimiter) {
	var arrRows = CSVToArray(strData, strDelimiter)
	var headRow = arrRows.shift()
	var objRows = new Array(arrRows.length)
	for (var i=0; i<arrRows.length; i++) {
		var obj = {}
		for (var j=0; j<headRow.length; j++)
			obj[headRow[j]] = arrRows[i][j] || ''
		objRows[i] = obj
	}
	return objRows
}


// IE костыль
!function(){ // костыль для тех, кто не умеет во второй агрумент classList.toggle
	document.head.classList.toggle("toggle-test-class", false)
	if (!document.head.classList.contains("toggle-test-class")) return
	document.head.classList.remove("toggle-test-class")

	var toggle = DOMTokenList.prototype.toggle
	DOMTokenList.prototype.toggle = function(cls/*, on/off*/) {
		if (arguments.length == 1) {
			return toggle.call(this, cls)
		} else {
			var on = !!arguments[1]
			this[on?'add':'remove'](cls)
			return on
		}
	}
}()
// Ещё один
!function(){
	if (Object.values) return
	Object.values = function(obj) {
		var res = []
		for (var k in obj) {
			if (typeof k === 'string' && obj.propertyIsEnumerable(k))
				res.push(obj[k])
		}
		return res
	}
}()
if (!Object.assign) {
  Object.defineProperty(Object, 'assign', {
    enumerable: false,
    configurable: true,
    writable: true,
    value: function(target) {
      'use strict';
      if (target === undefined || target === null) {
        throw new TypeError('Cannot convert first argument to object');
      }

      var to = Object(target);
      for (var i = 1; i < arguments.length; i++) {
        var nextSource = arguments[i];
        if (nextSource === undefined || nextSource === null) {
          continue;
        }
        nextSource = Object(nextSource);

        var keysArray = Object.keys(nextSource);
        for (var nextIndex = 0, len = keysArray.length; nextIndex < len; nextIndex++) {
          var nextKey = keysArray[nextIndex];
          var desc = Object.getOwnPropertyDescriptor(nextSource, nextKey);
          if (desc !== undefined && desc.enumerable) {
            to[nextKey] = nextSource[nextKey];
          }
        }
      }
      return to;
    }
  });
}

function afterAll(f){
	setTimeout(f, 50)
}

function getRelativeWeekNumByDayNum(month_start_dtime, day_num){
	var firstWeekNumber = new Date(month_start_dtime).getISOWeekNumber()
	var dayWeekNumber = new Date(month_start_dtime + Date.day*day_num).getISOWeekNumber()
	return dayWeekNumber - firstWeekNumber
}
function simpleEqual(a,b){
	return JSON.stringify(a) == JSON.stringify(b)
}

function calcPosForDropDown(params, ddWidth, ddHeight, margin){
	//params: ClientRect
	var tWidth = document.body.clientWidth
	var tHeight = document.body.clientHeight
	var margin = margin || 0
	var x = 0
	var y = 0
	//если дропдаун можно показать вниз
	if(params.bottom + ddHeight < tHeight){
		//если он влезает по ширине
		if(params.left + ddWidth < tWidth){
			x = params.left
			y = params.bottom
		} else {
			x = params.right - ddWidth
			y = params.bottom
		}
	} else {
		if(params.left + ddWidth < tWidth){
			x = params.left
			y = params.top - ddHeight - margin
		} else {
			x = params.right - ddWidth
			y = params.top - ddHeight - margin
		}
	}
	return {x:x, y:y}
}
if (!Object.assign) {
	Object.defineProperty(Object, 'assign', {
		enumerable: false,
		configurable: true,
		writable: true,
		value: function(target, firstSource) {
			'use strict';
			if (target === undefined || target === null) {
				throw new TypeError('Cannot convert first argument to object');
			}

			var to = Object(target);
			for (var i = 1; i < arguments.length; i++) {
				var nextSource = arguments[i];
				if (nextSource === undefined || nextSource === null) {
					continue;
				}

				var keysArray = Object.keys(Object(nextSource));
				for (var nextIndex = 0, len = keysArray.length; nextIndex < len; nextIndex++) {
					var nextKey = keysArray[nextIndex];
					var desc = Object.getOwnPropertyDescriptor(nextSource, nextKey);
					if (desc !== undefined && desc.enumerable) {
						to[nextKey] = nextSource[nextKey];
					}
				}
			}
			return to;
		}
	});
}
function rd(min, max) {
	var rand = min + Math.random() * (max + 1 - min);
	rand = Math.floor(rand);
	return rand;
}