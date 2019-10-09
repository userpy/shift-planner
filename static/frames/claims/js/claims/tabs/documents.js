claims.tabs.push(new claims.claimsTab({
	name: 'Шаблоны документов',
	code: 'docs',
	initComponents: function(){
		var tab = this
		Vue.component(this.getCompName(), {
			name: this.getCompName(),
			props:[],
			template: '#'+ this.getCompName() +'_template',
			data: function(){return{
				isMounted: false,
				isLoading: false,
				docs: [],
			}},
			mounted: function(){
				this.isMounted = true
				tab.loadAndGenerate(this)
			},
			computed:{
				colBody: function(){
					return this.$refs["col-body"]
				}
			},
		})
	},
	loadAndGenerate: function(comp){
		comp.isLoading = true
		claims.loadDocsForHr(onOk)
		function onOk(docs){
			comp.isLoading = false
			comp.docs = docs
		}
	},
}))