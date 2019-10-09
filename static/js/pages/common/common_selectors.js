var initCommonSelectors = new function(){
	checkSelectOptions = function(rawOpts, oldValue, selectName){
		var opts = []
		rawOpts.forEach(function(o){
			if(o.children) {
				opts = opts.concat(o.children)
			} else {
				opts.push(o)
			}
		})
		var ids = opts.map(function(opt){return ''+opt.id})
		if(oldValue instanceof Array){
			if(
				ids.filter(function(id){
					return ~oldValue.indexOf(id)
				}).length == oldValue.length
			) return
		}
		if(~ids.indexOf(oldValue)) return
		if(!oldValue) return
		//старое выбранное значение больше не может быть выбрано и будет сброшено. Надо предупредить юзера
		ViolationWarnings.showFor(null,{
			message: 'Старые фильтры таблицы были сброшены',
			type: 'warning'
		})
	}
	function setSelectedOpt(el, params){
		el.val(params.defaultOpt)
		el.trigger('change');
	}
	this.statusSelect = function(el, params){
		el.select2({
			placeholder: 'Статус...',
			data: params.options,
		})
		setSelectedOpt(el, params)
	}
	this.shiftsSelect = function(el, params){
		el.select2({
			placeholder: 'Смены...',
			data: params.options,
		})
		setSelectedOpt(el, params)
	}
	this.monthDatePicker = function(el, params){
		el.datepicker({
			language: 'ru',
			clearBtn: true,
			format: 'MM yyyy',
			autoclose: true,
			startView: 1,
			minViewMode: 1,
			maxViewMode: 2
		})
		el.datepicker( "setDate", params.defDate);
	}
	this.orgSelect = function(el, params){ //вызывается несоклько раз для пересоздания опций
		if(el.empty) el.empty()
		el.select2({
			placeholder: "Магазин...",
			allowClear: true,
			data: params.options,
		});
		setSelectedOpt(el, params)
	}
	this.setOrUpdateOrgSelect = function(organizations, filter){
		var current_value = filter.getValue()
		this.orgSelect($('#organization_select'),
			{
				options: organizations,
				defaultOpt: current_value
			}
		)
	}
	this.agencySelect = function(el, params){ //вызывается несоклько раз для пересоздания опций
		if(el.empty) el.empty()
		el.select2({
			placeholder: "Агентство...",
			allowClear: true,
			data: params.options,
		});
		setSelectedOpt(el, params)
	}
	this.setOrUpdateAgencySelect = function(agencies, filter){
		var current_value = filter.getValue()
		this.agencySelect($('#agency_select'),
			{
				options: agencies,
				defaultOpt: current_value
			}
		)
	}

	this.agencySelect = function(el, params){ //вызывается несоклько раз для пересоздания опций
		if(el.empty) el.empty()
		el.select2({
			placeholder: "Агентство...",
			allowClear: true,
			data: params.options,
		});
		setSelectedOpt(el, params)
	}
	this.setOrUpdateAgencySelect = function(agencies, filter){
		var current_value = filter.getValue()
		this.agencySelect($('#agency_select'),
			{
				options: agencies,
				defaultOpt: current_value
			}
		)
	}

	this.areaSelect = function(el, params){ //вызывается несоклько раз для пересоздания опций
		if(el.empty) el.empty()
		el.select2({
			placeholder: "Зона магазина...",
			allowClear: true,
			data: params.options,
		});
		setSelectedOpt(el, params)
	}
	this.setOrUpdateAreaSelect = function(areas, filter){
		var current_value = filter.getValue()
		this.areaSelect($('#area_select'),
			{
				options: areas,
				defaultOpt: current_value
			}
		)
	}

	
	this.promoSelect = function(el, params){ //вызывается несоклько раз для пересоздания опций
		if(el.empty) el.empty()
		el.select2({
			placeholder: "Вендор...",
			allowClear: true,
			data: params.options,
		});
		setSelectedOpt(el, params)
	}
	this.setOrUpdatePromoSelect = function(promos, filter){
		var current_value = filter.getValue()
		this.promoSelect($('#promo_select'),
			{
				options: promos,
				defaultOpt: current_value
			}
		)
	}

	this.violationSelect = function(el, params){ //вызывается несоклько раз для пересоздания опций
		if(el.empty) el.empty()
		el.select2({
			placeholder: "Нарушение...",
			allowClear: true,
			data: params.options,
			multiple: true,
		});
		setSelectedOpt(el, params)
	}
	this.setOrUpdateViolationSelect = function(violations, filter){
		var value = filter.getValueAsFixedArrStr()
		var current_value = value ? JSON.parse(value) : value
		if(simpleEqual(this.violationSelect.prevValues, violations)) return
		this.violationSelect.prevValues = violations
		checkSelectOptions(violations, current_value)
		this.violationSelect($('#violation_select'),
			{
				options: violations,
				defaultOpt: current_value
			}
		)
	}
}

function FilterState(filters){
	// упрощает получение и установку дефолтных значений
	// принимает массив фильтров
	// {name - по которому обращаться, storage - ключ для хранения в локалстороже, default - стартовое значение}
	var self = this
	filters.forEach(function(f){
		self[f.name] = new function(){
			var value = localStorage.getItem(f.storage) || f.default
			this.getValue = function(){return value}
			this.getValueAsDate = function(){
				var formattedDate = $('#'+f.name).data('datepicker').getFormattedDate('yyyy-mm-')
				if(formattedDate) formattedDate += '01'
				return formattedDate
			}
			this.getValueAsFixedArrStr = function(){
				if(!value) return ''
				if(value instanceof Array){
					val = value.map(function(v){return ''+v})
					return val.length ? JSON.stringify(val) : ''
				} else {
					return JSON.stringify( [value] )
				}
			}
			this.upd = function(newValue){
				//устанавливает переданное значение в локалстораж, селект и значение фильтра
				if(newValue === null) newValue = ''
				var oldValue = value
				if(JSON.stringify(newValue) == JSON.stringify(oldValue)) return
				localStorage.setItem(f.storage, newValue)
				value = newValue
				setValue($('#'+f.name), newValue, f.type)
			}
		}
	})

	this.clear = function(){
		filters.forEach(function(f){
			//сбрасывает фильтры страницы на дефолтное значение
			self[f.name].upd(f.default)
		})
	}
	function setValue(el, newValue, type){
		if(type == 'date_select'){
			el.datepicker( "setDate", newValue);
		} else {
			el.val(newValue)
			el.trigger('change')
		}
	}
}