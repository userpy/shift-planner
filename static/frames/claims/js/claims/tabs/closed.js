claims.tabs.push(new claims.claimsTab({
	name: 'Закрытые',
	code: 'closed',
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
				onBackClick: function(e){this.currPage = 1; this.detailed = null; tab.loadAndGenerate(this)},
				loadMoreRows: function(page){this.currPage = this.currPage+1; tab.loadAndGenerate(this)},
				onOpenButClick: function(e){tab.openClaim(this, tab)},
			}
		})
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
		claims.loadClaimsAndFilter('closed', comp.currPage, onOk)
		function onOk(params){
			comp.isLoading = false
			comp.claims = comp.claims.concat(params.claims)
			comp.pages = params.pages
			comp.currPage = params.page
		}
	},
	openClaim: function(comp, tab){
		if(!confirm('Открыть снова?')) return
		claims.reOpenClaim({
			claim_id: comp.detailed.id,
		}, function(){
			comp.detailed = null
			tab.loadAndGenerate(comp)
		}, function(){
			alert('Возникла ошибка, попробуйте позже')
		})
	},
}))