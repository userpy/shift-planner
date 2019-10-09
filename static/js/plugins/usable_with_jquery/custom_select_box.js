//	custom select .custom-select-box
function InitCustomSelect(el, paramsArray, superParams){
	//option can be: hidden, titleLine, disabled
	//iconical - значит вместо заголовка - иконка
	//multiSelect - значит можно выбрать несколько опций
	//width-100prsnts - по ширине инпута, width-auto - по ширине самой длинной опции
	//labelsWithIcons - опции с иконками
	//withAdditionInfo - серая приписочка к каждой опции
	//searchable - поиск
	//width-fixed, {width: n} - фикс ширина, в пикселях
	//togglable-selector-icon - опции могут менять иконку селекту
	//withLevels - отступы у опций
	// cleanDesign - воздушные опции
	// highlight-if-not-full - иконка красится когда выбраны не все опции
	if(el.classList.contains('custom-select-box')) return
	el.paramsArray = paramsArray || []
	el.superParams = superParams || {}
	el.classList.add('custom-select-box')
	el.setAttribute('tabindex', 0)
	el.expand = expand
	el.close = close

	var label = createEl('div')
	label.classList.add('csb-label')
	el.appendChild(label)
	if(~el.paramsArray.indexOf('searchable')){
		label.innerHTML = ''+
			'<div class="select-options"></div>'+
			'<input class="select-search">'
		label.ae$('input').addEventListener('keydown', onSearchInputKeydown)
		label.ae$('input').addEventListener('keyup', onSearchInputKeyUp)
	}

	var optionsWrap = createEl('div')
	optionsWrap.classList.add('csb-options-wrap')
	if( el.superParams.cleanDesign ){
		optionsWrap.classList.add('clean-design')
	}
	el.appendChild(optionsWrap)
	el.paramsArray.forEach(function(param){
		el.classList.add(param)
	})
	el.options = []
	el.selectedOptions = []
	el.addOptions = function(arrayOfObj, silent){
		arrayOfObj.forEach(function(item){
			el.addOption(item, silent)
		})
	}
	el.hideOption = function(obj){
		if(!obj.value) obj.value = obj.name
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var value = encodeURI(obj.value)
		var line = dd.ae$('.csb-option[data-value="'+value+'"]')
		if(line) line.style.display = 'none'
	}
	el.showOption = function(obj){
		if(!obj.value) obj.value = obj.name
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var value = encodeURI(obj.value)
		var line = dd.ae$('.csb-option[data-value="'+value+'"]')
		if(line) line.style.display = ''
	}
	el.addOption = function(obj, silent){
		if(!obj.value) obj.value = obj.name
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var optionsWrap = dd.ae$('.csb-options-wrap')
		var option = createEl('div')
		option.classList.add('csb-option')
		optionsWrap.appendChild(option)
		if(~el.paramsArray.indexOf('labelsWithIcons')){
			option.innerHTML = '<i class="fa '+ obj.labelIcon+'"></i>' + obj.name
		} else{
			option.textContent = obj.name
		}

		// if (obj.safe === true) {
		// 	option.innerHTML += obj.name
		// }
		// else {
		// 	option.textContent += obj.name
		// }

		if(~el.paramsArray.indexOf('withAdditionInfo')){
			option.innerHTML += (obj.additionInfo ? '<div class="addition-info">'+ obj.additionInfo +'</div>' : '')
		}
		if(el.superParams.withLevels){
			option.classList.add('level-'+ (obj.level || 0) )
		}
		
		if(obj.hidden) option.style.display = 'none'
		var oks = Object.keys(obj)
		for(var i = 0; i< oks.length; i++){
			option.dataset[oks[i]] = encodeURI(obj[oks[i]])
		}
		if( obj.icon ) option.className += ' ' + obj.icon
		el.options.push(obj)
		if(el.selectedOptions.length == 0 && !silent){
			el.selectOption(obj)
		}
		return option
	}
	el.wipeOptions = function(silent){
		for(var i=(el.options.length-1); i>=0; i--){
			if (!!el.options[i]) {
				el.removeOption(el.options[i], silent, {isNoRerender: true})
			}
		}
		onChange()
		updateSelectLabel()
	}
	el.removeOption = function(obj, silent, p){
		var p = p || {}
		var isNoRerender = p.isNoRerender
		if(!obj.value) obj.value = obj.name
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var value = encodeURI(obj.value)
		var line = dd.ae$('.csb-option[data-value="'+value+'"]')
		if(line) line.remove()

		el.selectedOptions.forEach(function(opt, i){
			if(opt.value == obj.value) el.selectedOptions.remove(el.selectedOptions[i])
		})
		el.options.forEach(function(opt, i){
			if(opt.value == obj.value) el.options.remove(el.options[i])
		})
		if(!silent) el.throwEvent('change', {}, true)
		if(!isNoRerender){
			onChange()
			updateSelectLabel()
		}
	}
	el.deSelectOption = function(obj, silent){
		if(!obj.value) obj.value = obj.name
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var value = encodeURI(obj.value)
		var line = dd.ae$('[data-value="'+value+'"]')
		var alreadyDeSelected = true
		el.selectedOptions.forEach(function(selOpt){
			if(selOpt.value == obj.value) alreadyDeSelected = false
		})
		if( alreadyDeSelected ) return
		//группа радиокнопок
		if(line.dataset.groupType == 'radio'){
			//если это единственная активная радиокнопка, то ее нельзя деселектить
			var group = decodeURI( line.dataset.group )
			var opts = el.selectedOptions
			var anyOtherSelected = false
			opts.forEach(function(opt){
				if( opt.group == group &&
						opt.value != obj.value
					) anyOtherSelected = true
			})
			if( !anyOtherSelected ) return
		}
		el.selectedOptions.forEach(removeOpt)
		if(line.dataset.groupType == encodeURI('all-or-not') ){
			obj.group = decodeURI( line.dataset.group )
			obj.groupRole = decodeURI( line.dataset.groupRole )
			if(!silent)updateAllOrNoGroup(obj, 'deSelect')
		}

		if(!silent) el.throwEvent('change', {}, true)
		onChange()

		function removeOpt(opt, i){
			if(opt.value == obj.value) el.selectedOptions.remove(el.selectedOptions[i])
		}
		updateSelectLabel()
	}
	el.selectOptions = function(arrayOfObj, silent){
		arrayOfObj.forEach(function(obj){ el.selectOption(obj, silent) })
	}
	el.deSelectOptions = function(arrayOfObj, silent){
		arrayOfObj.forEach(function(obj){ el.deSelectOption(obj, silent) })
	}
	el.selectOption = function(obj, silent){
		if(!obj.value) obj.value = obj.name
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var line
		var value = encodeURI( obj.value )
		line = dd.ae$('.csb-option[data-value="'+ value +'"]')
		var alreadySelected = false
		el.selectedOptions.forEach(function(selOpt){
			if(selOpt.value == obj.value) alreadySelected = true
		})
		if( alreadySelected ) return
		if( line ){
			//мультиселект
			if(~el.paramsArray.indexOf('multiSelect')){
				var flag = true
				el.selectedOptions.forEach(function(opt){
					if(opt.value == obj.value) flag = false
				})
				if(flag){
					var opts = el.options
					opts.forEach(function(opt){
						if(opt.value == obj.value) {el.selectedOptions.push(opt); return}
					})
				}
			} else { //обычный селект
				el.selectedOptions = []
				var opts = el.options
				opts.forEach(function(opt){
					if(opt.value == obj.value) {el.selectedOptions.push(opt); return}
				})
			}
			//группа радиокнопок
			if(line.dataset.groupType == 'radio'){
				var group = decodeURI( line.dataset.group )
				var opts = el.options
				opts.forEach(function(opt){
					if( opt.group == group &&
							opt.value != obj.value
						) el.deSelectOption(opt, silent)
				})
			}
			if( decodeURI( line.dataset.groupType ) == 'all-or-not'){
				obj.group = decodeURI( line.dataset.group )
				obj.groupRole = decodeURI( line.dataset.groupRole )
				if(!silent)updateAllOrNoGroup(obj, 'select')
			}
		}
		if(!silent) {
			el.throwEvent('change', {}, true)
		} else {
			if(!~el.paramsArray.indexOf('multiSelect')){
				el.ae$ae$('.csb-option').classList.remove('selected')
			}
			line.classList.add('selected')
		}
		updateSelectLabel()
		onChange()
	}
	function updateAllOrNoGroup(obj, mode){
		var options = el.options
		var selectedOptions = el.selectedOptions
		options = options.filter(function(opt){return opt.group == obj.group ? opt : false})
		selectedOptions = selectedOptions.filter(function(opt){return opt.group == obj.group ? opt : false})
		var isAllSelected = false
		var allOption
		options.forEach(function(opt){ if(opt.groupRole == 'toggleAll') allOption = opt})
		selectedOptions.forEach(function(opt){ if(opt.groupRole == 'toggleAll') isAllSelected = true})
		if(mode == 'select'){
			if(options.length == selectedOptions.length + 1){
				if( !isAllSelected ){
					el.selectOption(allOption, true)
				}
			}
			if(obj.groupRole == 'toggleAll') el.selectOptions(options, true)
		}else{
			el.deSelectOption(allOption, true)
			if(obj.groupRole == 'toggleAll') el.deSelectOptions(options, true)
		}
	}
	function removeAllLevels(){
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var lines
		lines = dd.ae$ae$('.csb-option')
		lines.classList.remove('level-0')
		lines.classList.remove('level-1')
		lines.classList.remove('level-2')
		lines.classList.remove('level-3')
		lines.classList.remove('level-4')
		lines.classList.remove('level-5')
	}
	function restoreAllLevels(){
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		var lines
		lines = dd.ae$ae$('.csb-option')
		lines.forEach(function(line){
			var level = decodeURI( line.dataset.level )
			line.classList.add('level-'+ level)
		})
	}
	function onSearchInputKeydown(e){
		var input = this
		var value = input.value
		if(value == '' && e.keyCode==8 && el.selectedOptions.length > 0){
			var optionToDeselect = el.selectedOptions[el.selectedOptions.length-1]
			el.deSelectOption(optionToDeselect)
			// input.click()//переоткрыть попап
			el.close()
			el.expand()
		}
	}
	function onSearchInputKeyUp(e){
		if(e.keyCode == 9){//tab
			close()
			expand()
		}
		var input = this
		if(e.keyCode == 13){//enter
			doSearchOnKeyUp(input)
		}
	}
	function doSearchOnKeyUp(input){
		var value = input.value.toLowerCase()
		var words = value.split(' ')
		var dd = ae$('.csb-dd')
		if(!dd) {
			input.value = ''
			input.blur()
			return
		}
		if(input.value == ''){
			restoreAllLevels()
			dd.ae$ae$('.csb-option').classList.remove('hidden')
			return
		}
		removeAllLevels() 
		el.options.forEach(function(option){
			var allWordsInOption = true
			words.forEach(function(word){
				if( !~option.name.toLowerCase().indexOf(word) ) allWordsInOption = false
			})
			var value = encodeURI( option.value )
			var line = dd.ae$ae$('.csb-option[data-value="'+ value +'"]')
			line.classList.toggle('hidden', !allWordsInOption )
		})
	}
	function updateSelectLabel(){
		var label = el.ae$('.csb-label')
		if(!~el.paramsArray.indexOf('iconical')) {
			if(~el.paramsArray.indexOf('searchable')){
				updateInSearchable()
			} else {
				updateInRegular()
			}
		} else {
			if(el.superParams['togglable-selector-icon']){
				var opt = el.selectedOptions[0]
				if(opt['selectorIcon']) label.className = 'csb-label fa '+ opt['selectorIcon']
			}
			if(el.superParams['highlight-if-not-full']){
				label.classList.toggle('not-full', el.selectedOptions.length != el.options.length)
			}
		}
		function updateInSearchable(){
			var label = el.ae$('.csb-label')
			var optionsWrap = label.ae$('.select-options')
			var searchInput = label.ae$('.select-search')
			searchInput.value = ''
			optionsWrap.textContent = ''
			el.selectedOptions.forEach(function(item){
				var optEl = createEl('div')
				optEl.classList.add('option')
				optEl.textContent = item.name
				optEl.dataset.name = item.name
				if(item.value) optEl.dataset.value = item.value
				optionsWrap.appendChild(optEl)
			})
			if(el.selectedOptions.length == 0){
				optionsWrap.classList.add('hidden')
				searchInput.setAttribute('placeholder', 'Не выбрано')
			} else {
				optionsWrap.classList.remove('hidden')
				searchInput.removeAttribute('placeholder')
			}
			searchInput.style.width = label.offsetWidth - optionsWrap.offsetWidth + 'px'
		}
		function updateInRegular(){
			var names = []
			el.selectedOptions.forEach(function(item){
				names.push(item.name)
			})
			label.textContent = names.join(', ')
		}
	}

	var ua = navigator.userAgent
	var ev = (ua.match(/iPad/i)) ? "touchstart" : "click"
	addEventListener(ev, onClickElseWhere)
	//el.addEventListener('focus', onFocus)
	//el.addEventListener('blur', onBlur)
	function onChange(e){
		var dd = ae$('.csb-dd')
		if( !dd || dd.parentSelector != el ) dd = el
		dd.ae$ae$('[data-name]').classList.remove('selected')
		el.selectedOptions.forEach(function(opt){
			var line
			var value = encodeURI( opt.value )
			line = dd.ae$('.csb-option[data-value="'+ value +'"]')
			if(line) line.classList.add('selected')
		})
	}
	function onClickElseWhere(e){
		var target = e.target.findElemByClass('csb-dd')
		//клик в попапчик
		if(target && target.parentSelector == el){
			var target = e.target
			if(el.classList.contains('disabled')) return
			target = target.findElemByClass('csb-option')
			if(target){
				if(target.classList.contains('disabled') ||
					target.dataset.disabled == 'true' ||
					target.dataset.titleLine == 'true') return

				if( !~el.paramsArray.indexOf('multiSelect') ){
					if(target.dataset.value){
						el.selectOption({
							'value': decodeURI( target.dataset.value ),  
							'name': decodeURI( target.dataset.name )
						})
					}else{
						el.selectOption({'name': decodeURI( target.dataset.name) })
					}
					close()
				} else {
					if(target.classList.contains('selected')){
						if(target.dataset.value){
							el.deSelectOption({'value': decodeURI( target.dataset.value )})
						}else{
							el.deSelectOption({'name': decodeURI( target.dataset.name )})
						}
					} else {
						if(target.dataset.value){
							el.selectOption({'value': decodeURI( target.dataset.value )})
						}else{
							el.selectOption({'name': decodeURI( target.dataset.name )})
						}
					}
				}
			}
			return
		}
		//клик мимо попапчика
		target = e.target.findElemByClass('custom-select-box') || false
		if(!target){
			close()
		} else if(target.classList.contains('active')){
			close()
		} else if(target == el){
			if(el.classList.contains('disabled')) return
			el.classList.contains('active') ?  close() : expand()
		} else {
			close()
		}
	}
	function onFocus(e){
		if(el.classList.contains('disabled')) return
		expand()
	}
	function onBlur(e){
		setTimeout(close, 100)
	}

	function expand(){
		el.classList.add('active')
		var elOptionsWrap = el.ae$('.csb-options-wrap')
		var dd = createEl('div')
		dd.classList.add('csb-dd', 'action-select-box')
		dd.parentSelector = el
		document.body.appendChild(dd)
		el.paramsArray.forEach(function(param){
			dd.classList.add(param)
		})
		elOptionsWrap.style.opacity = '0'
		elOptionsWrap.style.position = 'fixed'
		dd.appendChild(elOptionsWrap)
		dd.ae$ae$('.csb-option').classList.remove('hidden')//скрыты бывают после поиска
		var isPageZoomedIn = UI.utils.getScrollbarSize().width > 17
		var zoomFixWidth = isPageZoomedIn ? UI.utils.getScrollbarSize().width : 0
		if( ~el.paramsArray.indexOf('width-100prsnts') ){
			elOptionsWrap.style.width = el.offsetWidth + zoomFixWidth + 'px'
		}
		if( ~el.paramsArray.indexOf('width-auto') ){
			elOptionsWrap.classList.add('auto-width-try')
			var width = 0
			elOptionsWrap.ae$ae$('.csb-option').forEach(function(op){
				var ow = op.offsetWidth
				if(width < ow) width = ow
			})
			elOptionsWrap.classList.remove('auto-width-try')
			elOptionsWrap.style.width = width + 30 + UI.utils.getScrollbarSize().width + zoomFixWidth + 'px'
		}
		if( ~el.paramsArray.indexOf('width-fixed') ){
			elOptionsWrap.style.width = el.superParams.width + zoomFixWidth + 'px'
		}

		var elCoords = el.getBoundingClientRect()
		var elOptionsWrapOffsetHeight = elOptionsWrap.offsetHeight
		var coords = UI.utils.calcPosForDropDown(elCoords, elOptionsWrap.offsetWidth, elOptionsWrapOffsetHeight, 5)
		elOptionsWrap.style.left = coords.x + 'px'
		elOptionsWrap.style.top = coords.y + 'px'
		elOptionsWrap.style.opacity = '1'

		if(isPageZoomedIn) elOptionsWrap.style.height = elOptionsWrapOffsetHeight + 4+'px'

		var selectedOption = el.selectedOptions[0]
		if(selectedOption && !~el.paramsArray.indexOf('multiSelect')){
			var name =  encodeURI( selectedOption.name )
			var line = dd.ae$('.csb-option[data-name="'+ name +'"]')
			line.scrollIntoView()
		}
		if(~el.paramsArray.indexOf('searchable')){
			el.ae$('.select-search').focus()
		}
	}
	function close(){
		var dd = ae$('.csb-dd')
		if(!dd) return
		restoreAllLevels()
		if(dd.parentSelector != el) return
		el.appendChild(dd.ae$('.csb-options-wrap'))
		dd.remove()
		el.classList.remove('active')
		var label = el.ae$('.csb-label')
		var searchInput = label.ae$('.select-search')
		if(searchInput) searchInput.value = ''
	}
}
//	END custom select
