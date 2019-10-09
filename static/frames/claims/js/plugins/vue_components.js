UI.vueComponents = {
	init: function(){
		this.compInits.forEach(function(ci) {
			ci()
		})
		//filters
		Vue.filter('fullDate', function(time){
			return new Date(time).dmy() +' '+ new Date(time).hm()
		})
		Vue.filter('timeDeltaHM', function(time){
			return Date.delta.hm(time)
		})
	},
	compInits: [
		//select box
		function(){
			function selectOptions(select, selectedOptions, params){
				if( !selectedOptions || (selectedOptions && selectedOptions instanceof Array && !selectedOptions.length) ) {
					if( select.options.length && select.options[0].value == 'not-set') select.selectOption(select.options[0], true)
					return
				}
				if( typeof selectedOptions == 'Array')
					selectedOptions.map(function(o){ o.id && !o.value ? o.value = o.id : o })
					else
					selectedOptions.id && !selectedOptions.value ? selectedOptions.value = selectedOptions.id : false
				if( ~params.old.indexOf('multiselect') )
					select.selectOptions(selectedOptions, true)
					else
					select.selectOption(selectedOptions, true)
			}
			function getParams(comp){
				var params = comp.params || {}
				if( !params.old ) params.old = []
				if( !params.new ) params.new = {}
				if( !params.classes ) params.classes = []
				return params
			}
			Vue.component('vue-select-box', {
				name: 'vue-select-box',
				props: ['options', 'selected-options', 'params'],
				template: '#vp_selectbox',
				watch: {
					options: {
						handler: function(){
							var params = getParams(this)
							var select = this.$refs['selector-body']
							var opts = this.options || []
							opts.map(function(o){o.id && !o.value ? o.value = o.id : o})
							select.wipeOptions(true)
							select.addOptions(opts, true)
							selectOptions(select, this.selectedOptions, params)
						},
						deep: true
					},
					selectedOptions: {
						handler: function(){
							var params = getParams(this)
							var select = this.$refs['selector-body']
							selectOptions(select, this.selectedOptions, params)
						},
						deep: true
					},
					params:{
						handler: function(){
							// todo сделать адекватно
							var params = getParams(this)
							var select = this.$refs['selector-body']
							select.classList.toggle('disabled', ~params.old.indexOf('disabled'))
						},
						deep: true
					}
				},
				mounted: function () {
					var select = this.$refs['selector-body']
					var params = getParams(this)
					var opts = this.options || []
					opts.map(function(o){o.id && !o.value ? o.value = o.id : o})
					InitCustomSelect(select, params.old, params.new)
					select.addOptions(opts, true)
					selectOptions(select, this.selectedOptions, params)
					params.classes.forEach(function(c){select.classList.add(c)})
				}
			})
		},
		// date-select
		function(){
			function getParams(comp){
				var params = comp.params || {}
				if( !params.forInput ) params.forInput = {}
				if( !params.classes ) params.classes = []
				return params
			}
			Vue.component('vue-date-select', {
				name: 'vue-date-select',
				props: ['date', 'params', 'disabled'],
				template: '#vp_dateselect',
				watch: {
					params: {
						handler: function(){
							var params = getParams(this)
							var select = this.$refs['selector-body']
							select.setParams(params.forInput)
						},
						deep: true
					},
					date: {
						handler: function(){
							var select = this.$refs['selector-body']
							select.setDate(this.date, true)
						},
						deep: true
					},
					disabled: {
						handler: function(){
							var select = this.$refs['selector-body']
							select.disabled = this.disabled ? true : false
						},
						deep: true
					},
				},
				mounted: function () {
					var select = this.$refs['selector-body']
					var params = getParams(this)
					UI.DateInputWithDropdown(this.date, select, params.forInput)
					select.disabled = this.disabled ? true : false
					params.classes.forEach(function(c){select.classList.add(c)})
				}
			})
		},
		//date-interval-select
		function(){
			Vue.component('vue-date-interval-select', {
				name: 'vue-date-interval-select',
				props: ['date-from', 'date-to', 'params-from', 'params-to', 'disabled-from', 'disabled-to'],
				template: '\
<div class="date-range-wrap" ref="el-body">\
	<vue-date-select\
		:date="dateFrom"\
		:params="paramsFrom"\
		:disabled="disabledFrom"\
		v-on:change.native="onFromChange"\
	></vue-date-select>\
	<div class="separator">—</div>\
	<vue-date-select\
		:date="dateTo"\
		:params="paramsTo"\
		:disabled="disabledTo"\
		v-on:change.native="onToChange"\
	></vue-date-select>\
</div>',
				methods:{
					onFromChange: function(e){
						var date = e.target.getDate().getTime()
						this.$refs["el-body"].throwEvent('from-change', {date: date})
					},
					onToChange: function(e){
						var date = e.target.getDate().getTime()
						this.$refs["el-body"].throwEvent('to-change', {date: date})
					},
				},
				watch:{
					dateFrom: function(){
						if(this.dateFrom > this.dateTo)
							ViolationWarnings.showFor(this.$refs["el-body"].$('.date-input-with-dropdown'), {message: L10n.labels.valids.endBeforeStart})
					},
					dateTo: function(){
						if(this.dateFrom > this.dateTo) 
						ViolationWarnings.showFor(this.$refs["el-body"].$('.date-input-with-dropdown'), {message: L10n.labels.valids.endBeforeStart})
					},
				}
			})
		},
		// time-select
		function(){
			function getParams(comp){
				var params = comp.params || {}
				if( !params.forInput ) params.forInput = {}
				if( !params.classes ) params.classes = []
				return params
			}
			Vue.component('vue-time-select', {
				name: 'vue-time-select',
				props: ['time', 'params'],
				template: '#vp_timeselect',
				watch: {
					params: {
						handler: function(){
							//todo
							return
							var params = getParams(this)
							var select = this.$refs['selector-body']
							select.setParams(params.forInput)
						},
						deep: true
					},
					time: {
						handler: function(){
							var select = this.$refs['selector-body']
							select.setTime(this.time, true)
						},
						deep: true
					},
				},
				mounted: function () {
					var select = this.$refs['selector-body']
					var params = getParams(this)
					UI.TimeInputWithDropdown(this.time, select, params.forInput)
					params.classes.forEach(function(c){select.classList.add(c)})
					if(params.toolTip) new Tooltipable(select, params.toolTip, params.toolTipDelay || 500)
				}
			})
		},
		// mobilable table
		function(){
			Vue.component('vue-mobilable-table', {
				name: 'vue-mobilable-table',
				props: ['rows', 'params'],
				template: '#vp_mobilableTable',
				mounted: function () {
					MobilableTable.updateSizes(this.$refs['table-elem'])
				},
				updated: function () {
					var tableEl = this.$refs['table-elem']
					this.$nextTick(function () {
						MobilableTable.updateSizes(tableEl)
					})
				},
			})
		},
		// checkbox
		function(){
			Vue.component('vue-checkbox', {
				name: 'vue-checkbox',
				props: ['title', 'is-checked'],
				template: '\
<div class="vue-checkbox">\
	<i class="fa fa-square-o not-checked" v-if="!isChecked"></i>\
	<i class="fa fa-check-square-o checked" v-if="isChecked"></i>\
	<span v-if="title" v-text="title"></span>\
</div>'
			})
		},
		//loading screen
		function(){
			Vue.component('vue-loading-screen', {
				name: 'vue-loading-screen',
				props: ['target', 'message', 'type', 'heightUntil', 'messageColor', 'backgroundColor'],
				template: '<div class="vue-loading-screen" ref="el-body"></div>',
				data: function(){
					return{
						messageColor_local: this.messageColor || this.type == 'text' ? '#4a5266' : '',
						backgroundColor_local: this.backgroundColor || this.type == 'text' ? 'white' : '',
					}
				},
				mounted: function(){
					LoadingScreen.showFor(this.target, {
						message: this.message,
						messageColor: this.messageColor_local,
						backgroundColor: this.backgroundColor_local,
						heightUntil:  this.heightUntil
					})
				},
				destroyed: function(){
					LoadingScreen.hideFor(this.target)
				},
			})
		}
	]
}