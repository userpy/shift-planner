claims.tabs.push(new claims.claimsTab({
	name: 'На рассмотрении',
	code: 'wait',
	iconLeft: 'fa-refresh',
	forceRefreshOnReOpen: true,
	initComponents: function(){
		var tab = this
		Vue.component(this.getCompName(), {
			name: this.getCompName(),
			props:['shouldTabBeReloaded'],
			template: '#'+ this.getCompName() +'_template',
			data: function(){return{
				isMounted: false,
				isLoading: false,
				claims: [],
				detailed: null,
				messages: [],
				pages: 1,
				currPage: 1,
				comment: null,
				files:[],
				reportStatus: {},
				okCalledCount: 0
			}},
			watch:{
				shouldTabBeReloaded: function(){
					if( !tab.forceRefreshOnReOpen || !this.shouldTabBeReloaded) return
					this.isMounted = true
					tab.loadAndGenerate(this)
				}
			},
			mounted: function(){
				this.isMounted = true
				tab.loadAndGenerate(this)
			},
			computed:{
				colBody: function(){
					return this.$refs["col-body"]
				}
			},
			methods: {
				onRowClick: function(claim){this.detailed = claim; tab.loadMessagesAndGenerate(claim.id, this)},
				onFilesChange: function(e){var files =e.target.files; this.files = files.filter(function(f){return f.size}); tab.checkFilesSize(this)},
				onBackClick: function(e){this.currPage = 1; this.detailed = null; tab.loadAndGenerate(this); tab.clearForm(this)},
				onCreateClick: function(e){tab.submitComment(this, tab)},
				onCloseButClick: function(e){tab.closeClaim(this, tab)},
				loadMoreRows: function(page){this.currPage = this.currPage+1; tab.loadAndGenerate(this)}
			}
		})
	},
	clearForm: function(comp){
		comp.comment = ''
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
		if(!comp.comment) return invalid(comp.colBody.$('textarea'))
		if(new Array().some.call(comp.files, function(f){return f.size > maxFileSize})) return invalid(comp.colBody.$('.files-input'))
		return true
		function invalid(el){
			el.classList.add('validation-error')
			return false
		}
	},
	submitComment: function(comp, tab){
		if(!tab.isValid(comp)) return
		claims.commentClaim({
			claim_id: comp.detailed.id,
			text: comp.comment,
			user_name: getUsername().code,
			files: comp.files,
		}, function(){
			tab.handleProgress(comp, tab)
			tab.clearForm(comp)
		}, function(){
			claims.closeProgressPp()
			comp.reportStatus = {type:'error', message: 'Возникла ошибка, попробуйте позже'}
			setTimeout(function(){comp.reportStatus = {}}, 2000)
		})
	},
	handleProgress: function(comp, tab){
		//ожадиается, что будет вызвана для при отправке сообщения и каждого файла
		if(!$('.big-popup-wrap')) claims.showProgressPp()
		var total = 1 + comp.files.length
		comp.okCalledCount = comp.okCalledCount +1
		if(comp.okCalledCount >=total ){
			comp.okCalledCount = 0
			claims.closeProgressPp()
			comp.comment = null
			tab.loadMessagesAndGenerate(comp.detailed.id, comp)
			comp.colBody.$('.files-input').value = ''
		} else {
			claims.updateProgressPp(comp.okCalledCount, total)
		}
	},
	loadMessagesAndGenerate: function(cId, comp){
		comp.isLoading = true
		claims.loadClaimMessages(cId, function(data){
			comp.messages = data.messages
			comp.isLoading = false
		})
	},
	loadAndGenerate: function(comp){
		//do req
		comp.detailed = null
		comp.messages = []
		comp.isLoading = true
		if(comp.currPage == 1) comp.claims = []
		claims.loadClaimsAndFilter('wait', comp.currPage, onOk)
		function onOk(params){
			comp.isLoading = false
			comp.claims = comp.claims.concat(params.claims)
			comp.pages = params.pages
			comp.currPage = params.page
		}
	},
}))