claims.tabs.push(new claims.claimsTab({
	name: 'Создать новую',
	code: 'create',
	initComponents: function(){
		var tab = this
		Vue.component(this.getCompName(), {
			name: this.getCompName(),
			props:[],
			template: '#'+ this.getCompName() +'_template',
			data: function(){return{
				isLoading: false,
				claimTypes: [],
				selectedClaimType: null,
				agencies: [],
				orgunit: null,
				guid: null,
				optsForAgencySelect: [],
				selectedAgency: null,
				claimComment: '',
				files: [],
				reportStatus:{},
				okCalledCount: 0
			}},
			mounted: function(){
				tab.loadAndGenerate(this)
			},
			computed:{
				colBody: function(){
					return this.$refs["col-body"]
				}
			},
			methods: {
				onClaimTypeChange: function(e){this.selectedClaimType = e.target.selectedOptions[0]},
				onAgencyChange: function(e){this.selectedAgency = e.target.selectedOptions[0]},
				onFilesChange: function(e){var files =e.target.files; this.files = files.filter(function(f){return f.size}); tab.checkFilesSize(this)},
				onCreateClick: function(e){tab.submit(e, this, tab)},
				onClearClick: function(e){tab.clearForm(this)}
			}
		})
	},
	clearForm: function(comp){
		comp.claimComment = ''
		comp.reportStatus = {}
		comp.colBody.$('.files-input').value = ''
		comp.files = []
	},
	checkFilesSize: function(comp){
		var files = comp.files
		comp.reportStatus = {}
		new Array().forEach.call(files, function(f){
			if(f.size < maxFileSize) return
			comp.reportStatus = {type: 'error', message: 'Максимальный размер загружаемых файлов составляет  '+ maxFileSizeMB +' Мб'}
			comp.colBody.$('.files-input').classList.add('validation-error')
		})
	},
	isValid: function(comp){
		if(!comp.selectedClaimType) return invalid(comp.colBody.$('.claim-type-select'))
		if(!comp.selectedAgency) return invalid(comp.colBody.$('.agencies-select'))
		if(!comp.claimComment) return invalid(comp.colBody.$('.comment-area'))
		if(!comp.files.length) return invalid(comp.colBody.$('.files-input'))
		if(new Array().some.call(comp.files, function(f){return f.size > maxFileSize})) return invalid(comp.colBody.$('.files-input'))
		return true
		function invalid(el){
			el.classList.add('validation-error')
			return false
		}
	},
	submit: function(e, comp, tab){
		if(!tab.isValid(comp)) return
		claims.createClaim({
			organization_id: comp.orgunit.id,
			agency_id: comp.selectedAgency.id,
			claim_type_id: comp.selectedClaimType.id,
			text: comp.claimComment,
			guid: comp.guid,
			user_name: getUsername().code,
			email: getEmail().code,
			files: comp.files
		}, function(){
			tab.handleProgress(comp)
			tab.clearForm(comp)
		}, function(){
			claims.closeProgressPp()
			comp.reportStatus = {type:'error', message: 'Возникла ошибка, попробуйте позже'}
			setTimeout(function(){comp.reportStatus = {}}, 2000)
		})
	},
	handleProgress: function(comp){
		//ожадиается, что будет вызвана для при отправке сообщения и каждого файла
		if(!$('.big-popup-wrap')) claims.showProgressPp()
		var total = 1 + comp.files.length
		comp.okCalledCount = comp.okCalledCount +1
		if(comp.okCalledCount >=total ){
			comp.okCalledCount = 0
			claims.closeProgressPp()
			claims.vm.selectedTab = claims.tabs[1]
		} else {
			claims.updateProgressPp(comp.okCalledCount, total)
		}
	},
	loadAndGenerate: function(comp){
		comp.isLoading = true
		claims.loadDataForCreation(function(d){
			comp.agencies = d.agencies
			comp.optsForAgencySelect = d.optsForAgencySelect
			comp.claimTypes = d.claimTypes
			comp.orgunit = d.orgunit
			comp.guid = d.guid
			comp.isLoading = false
		})
	},
}))
