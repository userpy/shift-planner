var claims = new function(){
	var claims = this
	this.vm = null
	this.tabs = []
	this.init = function(){
		claims.initComponents()
		var data = getInitialData()
		var vm = new Vue({
			el: '.claims-nest',
			template: '#claims_template',
			data: data,
			methods:{
				onTabClick: onTabClick,
			},
			computed:{
				widgetBody: function(){
					return claims.vm.$refs["widget-body"]
				}
			}
		})
		this.vm = vm
	}
	this.initComponents = function(){
		Vue.component('messages', {
			name: 'messages',
			props:['messages'],
			template: '#messages_template',
			methods:{
				handleClick: function(e){var el = e.target.findElemByClass('message'); if(el) el.classList.remove('short')}
			}
		})
		Vue.component('pagination', {
			name: 'pagination',
			props:['pages', 'curr-page', 'onclick'],
			template: '#pagination_template',
		})
		this.tabs.forEach(function(tab){tab.initComponents()})
	}
	this.showNoPermissionPlaceholder = function(){
		$$('.custom-loading-screen').classList.add('hidden')
		LoadingScreen.showFor(document.body, {
			message: 'Недостаточно прав доступа для просмотра содержимого',
			messageColor: '#4a5266',
			backgroundColor: 'white',
			heightUntil: 'allScreen'
		})
	}
	getInitialData = function(){
		return{
			tabs: claims.tabs,
			selectedTab: claims.tabs[1],
			shouldTabBeReloaded: false,
			disabledMessage: null,
			isLoading: false,
			widgetParams: getParams(),
		}
	}
	getParams = function(){}
	onTabClick = function(tab){
		var vm = this
		if(tab.code == this.selectedTab.code && tab.forceRefreshOnReOpen){
			this.selectedTab = tab
			this.shouldTabBeReloaded = true
		} else{
			this.selectedTab = tab
		}
		Vue.nextTick(function(){vm.shouldTabBeReloaded = false})
	}
	this.showProgressPp = function(){
		UI.showPopup({
			title: 'Отправка',
			body: '<div class="nest" style="width: 240px;"></div>',
			onSubmit: function(){return false},
			onAbort: function(){return false}
		})
		var pp = $('.big-popup-wrap')
		pp.$('#pp_close').classList.add('hidden')
		var pgEl = pp.$('.nest')
		InitCustomProgressbar(pgEl)
	}
	this.updateProgressPp = function(done, total){
		var percents = done / total * 100
		var pp = $('.big-popup-wrap')
		var pgEl = pp.$('.nest')
		pgEl.setPercents(percents, 'отправлено '+done, total)
	}
	this.closeProgressPp = function(){
		var pp = $('.big-popup-wrap')
		if(!pp) return
		pp.remove()
	}
	this.getTabByCode = function(code, currentNode){
		var i, currentChild, result
		var currentNode = currentNode || {childs: claims.tabs}
		if (code == currentNode.code) {
			return currentNode
		} else {
			for (i = 0; i < currentNode.childs.length; i += 1) {
				currentChild = currentNode.childs[i]
				result = claims.getTabByCode(code, currentChild)
				if (result !== false) {
					return result
				}
			}
			return false
		}
	}
	this.claimsTab = function(rawTab){
		var tab = this
		tab.childs = []
		tab.isVisible = function(){
			return true
		}
		tab.getCompName = function(){
			return 'claims-tab-'+tab.code
		}
		for(var k in rawTab){
			tab[k] = rawTab[k]
		}
		tab.initComponents = function(){
			tab.childs.forEach(function(c){c.initComponents()})
			rawTab.initComponents.bind(tab)()
		}
	}
	this.loadClaimsAndFilter = function(key, page, onOk){
		xhr({
			url: '/api-get-claims/',
			data:{
				'format': 'json',
				'orgunit_code': getOrganization().code,
				'headquater_code': getHeadquater().code,
				'period_start': getPeriodStart().code,
				'period_end' :getPeriodEnd().code,
				'pagination[page]': page,
				'status_code': key
			},
			type: 'GET'
		}, function(resp){
			var data = JSON.parse(resp.responseText)
			var claims = data.data.map(function(c){
				var maxSybmls = 300
				var tooLong = c.text.length > maxSybmls
				c.shorTtext = c.text.slice(0, maxSybmls)
				if(tooLong) c.shorTtext+= '…'
				return c
			})
			onOk({
				claims: claims,
				page: data.meta.page,
				pages: data.meta.pages,
				total: data.meta.total,
			})
		})
	}
	this.loadClaimMessages = function(claimId, onOk){
		xhr({
			url: '/api-get-claim-messages/',
			data:{
				'format': 'json',
				'claim_id': claimId,
				'pagination[page]': 1,
				'pagination[perpage]': 1000,
			},
			type: 'GET'
		}, function(resp){
			var resp = JSON.parse(resp.responseText)
			onOk({
				messages: resp.data,
			})
		})
	}
	this.loadDataForCreation = function(onOk){
		xhr({
			url: '/api-create-claim/',
			data:{
				'format': 'json',
				'orgunit_code': getOrganization().code,
				'headquater_code': getHeadquater().code,
			},
			type: 'GET'
		}, function(resp){
			var resp = JSON.parse(resp.responseText)
			var agencies = []
			var optsForAgencySelect = []
			resp.agency_list.forEach(function(gr){
				var agsInGroup = gr.children.map(textToName)
				optsForAgencySelect.push({name: gr.text, titleLine: true})
				optsForAgencySelect = optsForAgencySelect.concat(agsInGroup.map(function(a){a.level = 1; return a}))
				agencies = agencies.concat(agsInGroup)
			})
			onOk({
				claimTypes: resp.claim_types.map(textToName),
				optsForAgencySelect: optsForAgencySelect,
				agencies: agencies,
				orgunit: resp.orgunit,
				guid: resp.guid,
			})
		})
	}
	this.createClaim = function(data, onOk, onErr){
		var files = data.files
		var formData = new FormData()
		formData.append('organization_id', data.organization_id)
		formData.append('agency_id', data.agency_id)
		formData.append('claim_type_id', data.claim_type_id)
		formData.append('text', data.text)
		formData.append('user_name', data.user_name)
        formData.append('email', data.email)
		formData.append('guid', data.guid)
		xhr({
			url: '/api-create-claim/',
			data:{
				'format': 'json',
			},
			type: 'POST',
			formData: formData
		}, function(resp){
			var resp = JSON.parse(resp.responseText)
			var claim_id = resp.id
			sendFilesInBase64(files, function(f){
				claims.addFileToClaim(f, claim_id, onOk, onErr)
			})	
			onOk()
		}, onErr)
	}
	this.commentClaim = function(data, onOk, onErr){
		var files = data.files
		var formData = new FormData()
		formData.append('claim_id', data.claim_id)
		formData.append('text', data.text)
		formData.append('party', 'client')
		formData.append('user_name', data.user_name)
		xhr({
			url: '/api-create-claim-message/',
			data:{
				'format': 'json',
			},
			type: 'POST',
			formData: formData,
		}, function(resp){
			var resp = JSON.parse(resp.responseText)
			var message_id = resp.id
			sendFilesInBase64(files, function(f){
				claims.addFileToComment(f, message_id, onOk, onErr)
			})
			onOk()
		}, onErr)
	}
	this.closeClaim = function(data, onOk, onErr){
		var formData = new FormData()
		formData.append('claim_id', data.claim_id)
		xhr({
			url: '/api-close-claim/',
			data:{
				'format': 'json',
			},
			type: 'POST',
			formData: formData,
		}, onOk, onErr)
	}
	this.reOpenClaim = function(data, onOk, onErr){
		var formData = new FormData()
		formData.append('claim_id', data.claim_id)
		xhr({
			url: '/api-reopen-claim/',
			data:{
				'format': 'json',
			},
			type: 'POST',
			formData: formData,
		}, onOk, onErr)
	}
    this.setClaimAction = function(data, onOk, onErr){
        var formData = new FormData()
        formData.append('claim_id', data.claim_id)
        formData.append('action', data.action)
		formData.append('user_name', getUsername().code)
        xhr({
            url: '/api-set-claim-action/',
            data:{
                'format': 'json',
            },
            type: 'POST',
            formData: formData,
        }, onOk, onErr)
    }
	this.addFileToClaim = function(file, claim_id, onOk, onErr){
		var formData = new FormData()
		formData.append('claim_id', claim_id)
		formData.append('filename', file.name)
		formData.append('size', file.size)
		formData.append('mime', file.mime)
		formData.append('file', file.base64)
		xhr({
			url: '/api-create-claim-attachment/',
			data:{
				'format': 'json',
			},
			type: 'POST',
			formData: formData,
		}, onOk, onErr)
	}
	this.addFileToComment = function(file, message_id, onOk, onErr){
		var formData = new FormData()
		formData.append('message_id', message_id)
		formData.append('filename', file.name)
		formData.append('size', file.size)
		formData.append('mime', file.mime)
		formData.append('file', file.base64)
		xhr({
			url: '/api-create-claim-attachment/',
			data:{
				'format': 'json',
			},
			type: 'POST',
			formData: formData,
		}, onOk, onErr)
	}
	this.loadDocsForHr = function(onOk){
		xhr({
			url: '/api-get-headquater-documents/',
			data:{
				'format': 'json',
				'headquater_code': getHeadquater().code,
			},
			type: 'GET'
		}, function(resp){
			var resp = JSON.parse(resp.responseText)
			onOk(resp)
		})
	}
	function textToName(o){o.name = o.text; return o}
}
document.body.classList.remove('loading-page')

function sendFilesInBase64(rawFiles, sendFunc){
	var readed = []
	for(var i=0; i<rawFiles.length; i++){
		var rawFile = rawFiles[i]
		var file = {
			name: rawFile.name,
			size: rawFile.size,
			mime: rawFile.type,
			base64: null,
		}
		readed.push(file)
		var reader = new FileReader()
		reader.onload = function(e) { this.base64 = e.target.result.split('base64,', 2)[1]; afterRead() }.bind(file)
		reader.readAsDataURL(rawFile)
	}
	function afterRead(){
		var isAllReady = readed.every(function(f){return f.base64})
		if(readed.length != rawFiles.length || !isAllReady) return
		readed.forEach(sendFunc)
	}
}
