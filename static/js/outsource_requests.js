/*
Copyright 2018 ООО «Верме»
JS-сниппеты для портала аутсорсинга
Цель - вынести все запросы к серверу в отдельный файл
*/
var OutRequests = new function(){
	// Список должностей
	this['get-jobs'] = function(params){
		params.type = 'GET'
		params.url = '/api-jobs/?format=json'
		params.cache = false
		$.ajax(params)
	}
	// Список видов документов
	this['get-doc-types'] = function(params){
		params.type = 'GET'
		params.url = '/api-doc-types/?format=json'
		params.cache = false
		$.ajax(params)
	}

	// Карточка сотрудника - получение данных о сотруднике
	this['get-employee'] = function(params){
		params.type = 'GET'
		params.url = '/api-employee/'
		params.cache = false
		$.ajax(params)
	}
	// Карточка сотрудника - сохранение данных о сотруднике
	this['set-employee'] = function(params){
		params.type = 'POST'
		params.url = '/api-employee/?format=json'
		params.cache = false
		$.ajax(params)
	}
	// Карточка сотрудника - запрос на прикрепление к клиенту
	this['set-employee-recruitment-event'] = function(params){
		params.type = 'POST'
		params.datatype = 'json'
		params.url = '/api-set-employee-recruitment-event/?format=json'
		$.ajax(params)
	}
	// Карточка сотрудника - запрос на открепление от клиента
	this['set-employee-dismissal-event'] = function(params){
		params.type = 'POST'
		params.datatype = 'json'
		params.url = '/api-set-employee-dismissal-event/?format=json'
		$.ajax(params)
	}
	// Карточка сотрудника - запрос на увольнение сотрудника
	this['dismiss-employee'] = function(params){
		params.type = 'POST'
		params.datatype = 'json'
		params.url = '/api-dismiss-employee/?format=json'
		$.ajax(params)
	}
	// Карточка сотрудника - запрос на перевод
	this['transition-agency-employee'] = function(params){
		params.datatype = 'json'
		params.url = '/api-transition-agency-employee/?format=json'
		$.ajax(params)
	}
	// Карточка сотрудника - скачать график смен
	this['get_employee_schedule'] = function(params){
		params.type = 'GET'
		params.datatype = 'json'
		params.url = '/api-export-employee-shifts/?format=json'
		$.ajax(params)
	}

	// Должность сотрудника - редактирование и добавление
	this['set-job-history'] = function(params){
		params.type = 'POST'
		params.url = '/api-job-history/?format=json'
		$.ajax(params)
	}
	// Должность сотрдника - удаление записи
	this['delete-job-history'] = function(params){
		params.type = 'DELETE'
		params.url = '/api-job-history/?format=json'
		params.headers = {
			'X-CSRFToken': csrf_token,
		},
		$.ajax(params)
	}
	this['get-employee-doc'] = function(params){
		params.type = 'GET'
		params.url = '/api-employee-doc/?format=json'
		$.ajax(params)
	}
	// Документ сотрудника - редактирование и удаление
	this['set-employee-doc'] = function(params){
		params.type = 'POST'
		params.url = '/api-employee-doc/?format=json'
		$.ajax(params)
	}
	// Документ сотрудника - удаление
	this['delete-employee-doc'] = function(params){
		params.type = 'DELETE'
		params.url = '/api-employee-doc/?format=json'
		params.headers = {
			'X-CSRFToken': csrf_token,
		},
		$.ajax(params)
	}

	// Квоты - список вот
	this['quotas-list'] = function(params){
		params.type = 'GET'
		params.url = '/api-quotas-list/?format=json'
		params.cache = false
		$.ajax(params)
	}
	// Квоты - список зон магазина и промоутеров (TODO - разделить на 2 запроса)
	this['get-quota-areas-promos'] = function(params){
		params.type = 'GET'
		params.url = '/api-get-quota-areas-promos/?format=json'
		params.cache = false
		$.ajax(params)
	}
	// Квоты - создание или редактирование квоты
	this['set-quota'] = function(params){
		params.type = 'POST'
		params.url = '/api-quota/?format=json'
		$.ajax(params)
	}
	// Квоты - удаление одной или нескольких квот
	this['delete-quota'] = function(params){
		params.type = 'DELETE'
		params.url = '/api-quota/'
		params.headers = {
			'X-CSRFToken': csrf_token,
		},
		$.ajax(params)
	}
	// Квоты ограничения - ограничения квот
	this['quotas-volume-list'] = function(params){
		params.type = 'GET'
		params.url = '/api-quotas-volume-list/?format=json'
		params.cache = false
		$.ajax(params)
	}
	// Квоты ограничения - создание или редактирование ограничения
	this['set-quota-volume'] = function(params){
		params.type = 'POST'
		params.url = '/api-quota-volume/?format=json'
		$.ajax(params)
	}
	// Квоты ограничения - удаление одного или нескольких ограничений
	this['delete-quota-volume'] = function(params){
		params.type = 'DELETE'
		params.url = '/api-quota-volume/'
		params.headers = {
			'X-CSRFToken': csrf_token,
		},
		$.ajax(params)
	}

	// TODO - разобраться, что это
	this['get-headquaters-organizations'] = function(params){
		params.type = 'GET'
		params.url = '/api-get-headquaters-organizations/?format=json'
		params.cache = false
		$.ajax(params)
	}
	this['get-claims'] = function(params){
		params.type = 'GET'
		params.url = '/api-get-claims/?format=json'
		params.cache = false
		$.ajax(params)
	}

	this['update-request'] = function(params){
		params.type = 'POST'
		params.url = '/update-request/'
		params.cache = false
		$.ajax(params)
	}
	this['shifts-workload'] = function(params){
		params.type = 'GET'
		params.url = '/api-shifts-workload/'
		params.contentType = "application/json; charset=utf-8"
		params.cache = false
		$.ajax(params)
	}
	this['shift-employee'] = function(params){
		params.url = '/api-shift-employee/?format=json'
		$.ajax(params)
	}
	this['check-selected-orgunit'] = function(params){
		params.type = 'GET'
		params.cache = false
		$.ajax(params)
	}
	this['get-docs-archive'] = function(params){
		params.url = '/api-get-docs-archive/'
		params.type = 'GET'
		params.cache = false
		$.ajax(params)
	}
}

var blobXHR = function(params, onOk, onErr){
	var params = params || {}
	var xhr = new XMLHttpRequest();
	var dataString = ''
	var file = params.file || {}
	if(params.data){
		dataString = '?'+joinGetParams(params.data)
	}
	if(params.responseType){
		xhr.responseType = params.responseType
	}
	xhr.open(params.type || 'GET', params.url + dataString, true)
	xhr.responseType = 'blob' // ие просит задавать респонс тайп после открытия запроса
	xhr.send(params.formData || null);
	blockUILoading()
	xhr.onload = function (e) {
		unBlockUILoading()
		var s = xhr.status
		// ok
		try{
			if (s >= 200 && s <= 204) {

				var fileName = file.name || xhr.getResponseHeader('content-disposition').split('filename="')[1].replace('"', '')
				var mimeType = xhr.getResponseHeader('content-type')
				if(navigator.msSaveOrOpenBlob) {
					// ИЕ10+ и Edge (в последнем должен работать a[download], но не работает)
					navigator.msSaveOrOpenBlob(xhr.response, fileName)
				} else if(/Version\/[\d\.]+.*Safari/.test(navigator.userAgent)) {
					// Safari
					location.href = 'data:' + mimeType + ';charset=utf-8,' + encodeURIComponent(data) //URL.createObjectURL(blob)
				} else {
					// FF, Chrome, Opera
					var blob = xhr.response
					var blobURL = URL.createObjectURL(blob)
	
					var a = document.createElement('a')
					a.href = blobURL
					a.target = '_blank'
					a.setAttribute('download', fileName)
					document.body.appendChild(a)
					a.click()
	
					setTimeout(function() {
						a.remove()
						URL.revokeObjectURL(blobURL)
					}, 100)
				}
				onOk ? onOk() : pass
			} else{
				// err
				unBlockUILoading()
				var reader = new FileReader()
				reader.addEventListener('loadend', function(e){
					var message = parseErrorFromServer(JSON.parse(e.srcElement.result))
					onErr ? onErr(message) : alert(message)
				})
				reader.readAsText(xhr.response)
			}
		}catch(e){
			console.error(e)
			unBlockUILoading()
		}
		
	}
}
joinGetParams = function(params){
	var arr = []
	for (var name in params) {
		var value = params[name]
		if (typeof value == "object") value = JSON.stringify(value)
		arr.push(name +'='+ encodeURIComponent(value))
	}
	return arr.join('&')
}