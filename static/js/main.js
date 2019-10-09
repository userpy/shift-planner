//utils
$.fn.select2.defaults.set('language', {
	noResults: function(){return "Совпадений не найдено"},
})
$.fn.select2.defaults.set('minimumResultsForSearch', 16)
$.fn.select2.defaults.set('width', '100%')


Number.prototype.toLen = function(len) {
	var res = ''+this
	while (res.length < len) res = '0'+ res
	return res
}

//временное решение для блокирования форм в попапах
NodeList.prototype.forEach = Array.prototype.forEach
NodeList.prototype.indexOf = Array.prototype.indexOf
NodeList.prototype.filter = Array.prototype.filter
NodeList.prototype.map = Array.prototype.map
NodeList.prototype.reduce = Array.prototype.reduce
function blockModalForm(el){
	var el = document.querySelector('.modal.show .modal-footer')
	if(!el) return
	el.querySelectorAll('.btn').forEach(function(b){b.setAttribute('disabled', true)})
	blockModalBody()
}
function unblockModalForm(el){
	var el = document.querySelector('.modal.show .modal-footer')
	if(!el) return
	el.querySelectorAll('.btn').forEach(function(b){b.removeAttribute('disabled')})
	unBlockModalBody()
}
function blockModalBody(){
	var el = document.querySelector('.modal.show .modal-body')
	if(!el) return
	el.style.pointerEvents = 'none'
	//console.error('modal body BLOCKED')
}
function unBlockModalBody(){
	var el = document.querySelector('.modal.show .modal-body')
	if(!el) return
	el.style.pointerEvents = ''
	//console.info('modal body unblocked')
}
function blockForm(el){
	var el = el[0].querySelector('.m-portlet__foot')
	if(!el) return
	el.querySelectorAll('.btn').forEach(function(b){b.setAttribute('disabled', true)})
}
function unblockForm(el){
	var el = el[0].querySelector('.m-portlet__foot')
	if(!el) return
	el.querySelectorAll('.btn').forEach(function(b){b.removeAttribute('disabled')})
}

function toggleModalControls(state){
	ae$$('.modal-controls').forEach(function(el){ el.style.display = 'none'})
	ae$$('.modal-controls.modal-controls--'+state).forEach(function(el){ el.style.display = 'block'})
}
var modalServerErrorLabelTimeout
function handleNonServerErrorInModal(message){ //todo найти вызовы и заменить на handleServerErrorInModal
	handleServerErrorInModal({responseJSON:{
		'error': message
	}})
}
function parseErrorFromServer(r){
	var errors = Object.keys(r).map(function(ok){
		return r[ok]
	}).join('; ') || null
	return r.message || errors || 'Произошла неизвестная ошибка'
}
function handleServerErrorInModal(r){
	var modalBody = document.querySelector('.modal.show .modal-body')
	clearTimeout(modalServerErrorLabelTimeout)
	var alertEl = modalBody.querySelector('.alert')
	
	var errorData = r.responseJSON || {}
	var nonFieldErrorStr = ''
	Object.keys(errorData).forEach(function(k){
		var text = errorData[k]
		var helpEl = modalBody.querySelector('#'+ k +'-help')
		if(!helpEl){
			nonFieldErrorStr+= ' '+ text
			return
		}
		helpEl.style.display = ''
		helpEl.textContent = text
	})
	if(nonFieldErrorStr){
		if(!alertEl){
			alertEl = document.createElement('div')
			alertEl.className = 'alert alert-danger'
			modalBody.insertBefore(alertEl, modalBody.childNodes[0])
		}
		alertEl.textContent = nonFieldErrorStr
		alertEl.style.display = 'block'
	}
	modalServerErrorLabelTimeout = setTimeout(function(){
		Object.keys(errorData).forEach(function(k){
			var helpEl = modalBody.querySelector('#'+ k +'-help')
			if(helpEl) helpEl.style.display = 'none'
			if(alertEl) alertEl.style.display = 'none'
		})
		clearTimeout(modalServerErrorLabelTimeout)
	}, 3000)
}
function handleWarningInModal(message){
	var modalBody = document.querySelector('.modal.show .modal-body')
	var alertEl = modalBody.querySelector('.alert-warning')
	if(!alertEl){
		alertEl = document.createElement('div')
		alertEl.className = 'alert alert-warning'
		modalBody.insertBefore(alertEl, modalBody.childNodes[0])
	}
	alertEl.style.display = 'block'
	alertEl.innerHTML = message
}
function hideWarningInModal(){
	var alerts = document.querySelectorAll('.modal .alert-warning')
	alerts.forEach(function(a){a.style.display = 'none'})
}
function toggleButtonLoadingState(butt, isLoading){
	var loadigClasses = 'm-loader m-loader--right m-loader--light'.split(' ')
	loadigClasses.forEach(function(cl){
		butt.classList.toggle(cl, isLoading)
	})
}
function prepareButtForLoadingState(butt){
	butt.style.width = '128px'
}


Date.prototype.dmy = function() {
	return this.getDate().toLen(2) +'.'+ (this.getMonth()+1).toLen(2) +'.'+ this.getFullYear()
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
function checkFormRequirments(wrap){
	var isValid = true
	var inputs = wrap.querySelectorAll('[data-required]')
	inputs.forEach(function(input){
		var help = wrap.querySelector('#'+input.id+'-help')
		if(!help) help = wrap.querySelector('#'+input.getAttribute('name')+'-help')
		help.style.display = 'none'
		help.textContent = ''
		if(input.value) return
		isValid = false
		help.textContent = l10n.required
		help.style.display = ''
	})
	return isValid
}
blockUILoading = function(){
	$.blockUI({ message: '<h2>Загрузка</h2>' })
}
unBlockUILoading = function(){
	$.unblockUI()
}
hideElViaCSS = function($el){
	$el.css({visibility: 'hidden', height: 0, padding: 0})
}
showElViaCSS = function($el){
	$el.css({visibility: 'visible', height: '', padding: ''})
}
getStartDateFromDatachanger = function(){
	var date = ''
	try{
		date = new Date(topDateChanger.interval.selected_start_dtime).toISODateString()
	} catch(e){}
	return date
}
getEndDateFromDatachanger = function(){
	var date = ''
	try{
		date = Date(topDateChanger.interval.selected_start_dtime)
		date = new Date(date.setMonth(date.getMonth() +1)).toISODateString()
	} catch(e){}
	return date
}

// кнопка вернуться назад
$('#history_back').click(function(el){

	var rpp = el.target.dataset.rpp;
	
	switch(rpp) {
		case 'agency':
			window.location.assign('/employees-list')
			break;
		case 'promo':
		case 'broker':
			window.location.assign('/'+rpp+'-employees-list')
			break;
		case 'client':
			window.location.assign('/hq-employees-list')
			break;
		default:
			history.back()
	}
});