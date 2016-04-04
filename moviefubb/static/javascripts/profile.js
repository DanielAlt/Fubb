$(document).ready(function(){

	var doLayout = function(){
		$(".scroll_page").css('min-height', $(window).height());	
	}
	doLayout()
	$(window).resize(doLayout);

	$('#warning_icon').click(function(e){
		var offset_x = ($(window).width() - $('.warning_popup').width())/2
		var offset_y = ($(window).height() - $('.warning_popup').height())/2;
		$('.warning_popup').css({'left': offset_x, 'top': offset_y});

		$('.cancel_btn').bind('click', function(){
			clearDialog() 
		});

		$('.confirm_btn').bind('click', function(){
			resendEmail($(this).attr('data-user'));
		});

		$('#backlight_overlay').fadeIn();
		$('.warning_popup').fadeIn();
	});

	$('#backlight_overlay').click(function(event){
		clearDialog();
	})

	var clearDialog = function(){
		$('.cancel_btn').unbind('click');
		$('.confirm_btn').unbind('click');
		$("#backlight_overlay").fadeOut();
		$('.warning_popup').fadeOut();
	}

	var resendEmail = function(user_id){
		window.location.href = '/accounts/' + user_id + "/confirm/resend";
	}

});