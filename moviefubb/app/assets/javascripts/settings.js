$(document).ready(function(){
	
	var doLayout = function(){
	}
	doLayout()
	$(window).resize(doLayout);

	var switchTab = function(tab){
		$('.tabpage').each(function(){
			$(this).removeClass('tabpage_active').addClass('tabpage_hidden');
		});
		$(tab).removeClass('tabpage_hidden').addClass('tabpage_active');
	}
	$('.settings_tabbar_btn').click(function(e){
		var tab = '#tabpage_' + $(this).attr('data-tab');
		switchTab(tab);
		$('#notification_message').slideUp();
	});

	if ($.trim($('#notification_message').html()).length > 0){
		$('#notification_message').css('display', 'inline-block');
	}

	var toDisplay = '#tabpage_' + $('#last_form').attr('data-form');
	switchTab(toDisplay);

});