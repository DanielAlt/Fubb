$(document).ready(function(){

	// Reset Layout To Default
	var doLayout = function(){
		var x = $(window).width();
		var y = $(window).height();
		var sidebar_width = $(".content_side_bar").width();
		var tabbar_width = $("#tab_bar").width();
		var footer_height = $("#footer").height();
		var content_height = $('#content_page').height();
		$("#top_bar").width(x);
		$('#static_top').width(x-tabbar_width-30);
		$("#backlight_overlay").height(y).width(x);
		$('#loading_screen').width(x-60);
		if (content_height < (y-footer_height)){
			$('#content_page').css('min-height', (y-footer_height));
		}
	}
	doLayout();	
	$(window).resize(doLayout);

	// Loading Bar
	Pace.on("done", function(){
	    $("#loading_screen").fadeOut(1000);
	});

	// HOVER MENU
	$('.hover_menu > li').click(function(e){
		var url = $(this).children().children().attr('href');
		window.location.href = url;
	});

	// BACK TO TOP BUTTON
	$(window).scroll(function(e){
		if ($(this).scrollTop() >= 200){
			$('#back_to_top').fadeIn(1000);
		} else {
			$('#back_to_top').fadeOut(1000);
		}
	});
});