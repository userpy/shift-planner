page_main_widget.components.push(new function(){
	this.init = function(){
		Vue.component('sa-filters-dd', {
			name: 'sa-filters-dd',
			props: ['on-ok', 'on-cancel', 'raw-rows-data', 
							'on-org-filter-change', 'on-area-filter-change', 
							'org-filter-values', 'area-filter-values', 'settings'],
			template: '\
			<div class="sa-dropdown" :style="{top: cssTop, left: cssLeft}" ref="ddBody">\
				<div class="sse-row head-row">\
					<b>Настройка фильтрации</b>\
					<div class="btn m-btn--pill btn-secondary btn-sm" @click="onCancel"><i class="fa fa-times"></i></div>\
				</div>\
				<div class="sse-row " v-if="settings.filters.organization">\
					<vue-jq-select\
						:options="organizations"\
						:selected-options="orgFilterValues"\
						:on-change="onOrgFilterChange"\
						:select-params="orgSelectParams"\
						:elem-params="{isMultiple: true}"\
					></vue-jq-select>\
				</div>\
				<div class="sse-row " v-if="settings.filters.area">\
					<vue-jq-select\
						:options="areas"\
						:selected-options="areaFilterValues"\
						:on-change="onAreaFilterChange"\
						:select-params="areaSelectParams"\
						:elem-params="selectorElParams"\
					></vue-jq-select>\
				</div>\
			</div>\
			',
			data: function(){return{
				cssTop: 0,
				cssLeft: 0,
				selectorParams: {closeOnSelect: false},
				selectorElParams: {isMultiple: true},
			}},
			mounted: function(){
				var ddBody = this.$refs.ddBody
				var targetEl = ae$('.sa-filters-expand-btn')
				var pos = calcPosForDropDown(targetEl.getBoundingClientRect(), ddBody.getBoundingClientRect())
				this.cssTop = pos.top +'px'
				this.cssLeft = pos.left +'px'
			},
			computed: {
				orgSelectParams: function(){
					return Object.assign({}, this.selectorParams, {placeholder: this.settings.filters.organization.placeholder})
				},
				areaSelectParams: function(){
					return Object.assign({}, this.selectorParams, {placeholder: this.settings.filters.area.placeholder})
				},
				cleanRows: function(){
					return this.rawRowsData.map(function(block){return block.rows}).reduce(function(p, c){return p.concat(c)},[])
				},
				organizations: function(){
					return this.cleanRows.map(function(r){
						var nr = {
							text: r.organization.name,
							id: r.organization.id,
						}
						return nr}).uniqByKey('id')
				},
				areas: function(){
					return this.cleanRows.map(function(r){
						var nr = {
							text: r.area.name,
							id: r.area.id,
						}
						return nr}).uniqByKey('id')
				},
			},
		})
	}
}())