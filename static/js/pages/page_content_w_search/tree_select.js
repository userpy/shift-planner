var orgSelect
document.addEventListener('DOMContentLoaded', function() {
	orgSelect = new function(){
		var thisSelect = this
		var nodeData = {}
		this.selectedUnit = null
		this.refresh = function(){ treeElem.jstree(true).refresh() }
		var storageKey = 'group_orgTree_tree_'+ request_page_party
		var storageKeyState = 'group_orgTree_state_'+ request_page_party
		var treeElem
		var ddElem
		var navItemControl
		var navItemLabel
		var data
		init()
		function getData(){
			data = JSON.parse(localStorage.getItem(storageKey))
			if(data) return initTree()
			var params = {
				type: 'GET',
				url: '/api-get-selector-data/',
				data:{
					format: 'json',
					party: request_page_party,
					'_': new Date().getTime(),
				},
				success: function(r){
					data = r
					localStorage.setItem(storageKey, JSON.stringify(r))
					initTree()
				},
				error: function(r){console.log(r)},
			}
			$.ajax(params)
		}
		function init(){
			treeElem = $('#org_tree')
			ddElem = $('#org_dropdown')
			navItemControl = $('#top_org_select_control')
			navItemLabel = $('#top_org_select_label')
			getData()
			initSearchBlock(treeElem)
			//чтобы не закрывалась меню при клике на дерево
			$('#org_dropdown').click(function(e){
				e.stopPropagation()
			})
		}
		function initTree(){
			var applyItem = function(nodeData, silent){
				// выбрать оргунит
				this.selectedUnit = new function Unit(){
					this.id = nodeData.id.split('_')[0]
					this.code = nodeData.id
					this.name = nodeData.text
					this.isHeadquater = ~nodeData.id.split('_').indexOf('headquater')
				}
				if(!silent) {
					navItemControl.trigger('change', this.selectedUnit)
					$('body').trigger('orgunits:change', this.selectedUnit)
				}
				navItemLabel[0].textContent = this.selectedUnit.name
				document.body.click()
			}.bind(thisSelect)
			// чтобы выбирал первую доступную ноду
			// у агенств и промо нужно выбирать первый хедквотер,
			// у клиента грузить первый хедквотер и выбирать что в него вложено
			treeElem.on('loaded.jstree', function(e, instance) {
				if(localStorage.getItem(storageKeyState)) {
					var prevSelected = JSON.parse(localStorage.getItem(storageKeyState)).state.core.selected[0]
					if(prevSelected && data.some(function(d){return d.id == prevSelected})) return
				}
				var tree = instance.instance
				// если страница клиента, то выбрать первую организацию, иначе открыть список
				if(request_page_party == 'client'){
					tree.select_node(tree.get_json()[0])
				} else {
					tree.open_node(tree.get_json()[0])
					tree.select_node(tree.get_json()[0].children[0])
				}
			});
			//клик на ноду
			var isInitialNodeSelect = true
			treeElem.on('select_node.jstree', function(event, node){
				nodeData = node.node
				if(isInitialNodeSelect){//выбрать оргюнит после инициализации дерева
					isInitialNodeSelect = false
					applyItem(nodeData, true)
					//проверить что юнит рабочий
					if(!data.some(function(item){
						return item.id == nodeData.id
					})){
						// сбросить дерево, если выбранный юнит недоступен
						// такое может быть, если дерево устарело
						localStorage.setItem(storageKeyState, '') // нужно для выбора дефолтной опции
						thisSelect.refresh()
					}
					setTimeout(function(){$('body').trigger('orgunits:loaded')}, 100)//иначе ие не видит объект дерева
				} else{
					applyItem(nodeData)
				}
			})
			treeElem.jstree({
				dnd: {
					"is_draggable": function (node) {
							return false;  // flip switch here.
					}
				},
				core: {
					themes: {
						responsive: !1
					},
					check_callback: !0,
					data: data,
				},
				types: {
					default: {
						icon: 'fa fa-folder m--font-brand'
					},
					file: {
						icon: 'fa fa-file m--font-brand'
					}
				},
				state: {
					key: storageKeyState
				},
				plugins: ['dnd', 'state', 'types', 'conditionalselect']
			})
			// чтобы растягивался по ширине
			treeElem.css({
				'width': 'auto',
				'height': 'auto',
				'overflow': 'auto',
				'display': 'inline-block',
				'max-height': '500px'
			})
			ddElem.css({'transition': 'width 0.1s ease-in'})
			treeElem.on('open_node.jstree', resizeTreeWrap)
			treeElem.on('close_node.jstree', resizeTreeWrap)
			treeElem.on('open_all.jstree', resizeTreeWrap)
			treeElem.on('close_all.jstree', resizeTreeWrap)
			navItemControl.on('click', function(){requestAnimationFrame(resizeTreeWrap)})
			// чтобы растягивался по ширине
		}
		function resizeTreeWrap(){
			var treeWidth = treeElem[0].getBoundingClientRect().width
			ddElem.css('width', Math.max(treeWidth + 60, 270) +'px')
			ae$('.tree-search').style.width = Math.max(treeWidth-24, 187) +'px'
		}
		function initSearchBlock(treeElem){
			var inputEl = ae$('.tree-search')
			var treeElem = treeElem
			var resultsElem = ae$('.tree-search-results')
			resultsElem.style.display = 'none'
			function onkeyup(e){
				if(e.keyCode != 13) return
				e.preventDefault()
				var search = e.target.value.toLowerCase()
				if(search.length < 3) return
				var opts = treeElem.jstree().get_json(null,{flat:true})
				opts = opts.filter(function(o){
					return ~o.text.toLowerCase().indexOf(search)
				}).map(function(o){
					let path = o.parent != '#'?opts.filter(function(fo){
						return fo.id == o.parent
					})[0].text : ''
					return '<div class="button" data-text="'+o.text+'">'+o.text+(path ? '<span class="path">'+path+'</path>' : '')+'</div>'
				}).join('')
				if(opts.length)
					resultsElem.innerHTML = opts
					else
					resultsElem.innerHTML = '<span class="no-results">Ничего не найдено</span>'
				resultsElem.style.display = 'block'
				treeElem.hide()
			}
			var clearElem = ae$('.tree-search-block .clear-search')
			clearElem.addEventListener('click', clear)
			function clear(){
				resultsElem.innerHTML = ''
				resultsElem.style.display = 'none'
				treeElem.show()
				inputEl.value = ''
				resizeTreeWrap()
			}
			
			ae$('.tree-search-results').addEventListener('click', function(e){
				let butt = e.target.findElemByClass('button')
				if(!butt) return
				var opts = treeElem.jstree().get_json(null,{flat:true})
				var op = opts.filter(function(o){
					return o.text == butt.dataset.text
				})[0]
				treeElem.jstree().deselect_all()
				treeElem.jstree().select_node(op)
				clear()
				document.body.click()
			})
			inputEl.addEventListener('keyup', onkeyup)
			// костыль для ие. Без него фокус в инпут на появляющемся элементе не ставится, пока 
			// не будет нажата кастомная кнопка очистки инпута, или контрол+в, или пкм
			var ftimer
			inputEl.addEventListener('focus', function(){
				if(ftimer) return
				var input = this
				var v = this.value
				input.value = v + '   '
				input.blur()
				ftimer = setTimeout(function(){
					input.focus()
					input.value = v
					clearTimeout(ftimer)
					setTimeout(function(){
						ftimer = null
					},200)
				},100)
			})
		}
	}()
});
