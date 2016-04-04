$(document).ready(function(){

	var switchTab = function(tab){
		$('.tabpage').each(function(){
			$(this).removeClass('tabpage_active').addClass('tabpage_hidden');
		});
		$(tab).removeClass('tabpage_hidden').addClass('tabpage_active');
	}
	$('.help_tabbar_btn').click(function(e){
		var tab = '#tabpage_' + $(this).attr('data-tab');
		switchTab(tab);
	});

});