$(document).ready(function(){

	$('.view_btn').click(function(e){
		var tab = "#" + $(this).attr('data-viewbutton') + "_view_page";
		switchPage(tab)
	});
	var switchPage = function(tab){
		$('.active_page').removeClass('active_page').addClass('hidden_page');
		$(tab).removeClass('hidden_page').addClass('active_page');
	}

	var tab = $("#view_mode").attr('data-currentview');
	if ($.inArray(tab, ['details', 'window', 'list']) > 0){
    	switchPage("#" + tab + "_view_page");
	}

});