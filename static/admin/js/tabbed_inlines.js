(function($) {
	'use strict';
	$(document).ready(function() {
		activateCurrentTab();

		$('ul.tabs__caption').on('click', 'li:not(.active)', function() {
			var index = $(this).index();
			$(this).addClass('active').siblings().removeClass('active')
			$('fieldset.module').each(function(i){
				$(this).toggleClass('active', i == index);
			});
			saveCurrentTab();
		});
	});

	function getPageKey() {
		var m = location.pathname.match(/\/admin\/.*?\/.*?\//)
		return m && m[0]
	}

	function saveCurrentTab() {
		var key = getPageKey()
		if (key === null) return
		localStorage['active-tab-on:'+key] = $('ul.tabs__caption li.active').text();
	}

	function activateCurrentTab() {
		var key = getPageKey()
		var name = key && localStorage['active-tab-on:'+key]
		var index = name ? $('ul.tabs__caption li:contains('+name+')').filter(function(){ return this.textContent==name }).index() : 0
		$('ul.tabs__caption li').eq(index).addClass('active');
		$('fieldset.module').eq(index).addClass('active');
	}
})(django.jQuery);