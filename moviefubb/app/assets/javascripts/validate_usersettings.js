$(document).ready(function(){

	function validateEmail(email) {
    	var re = /^(\S)*@(\w)*\.\w{2,}$/; 
	    return re.test(email);
	}

	var form_valid = function(){
		var valid = true;
		$('input').each(function(){
			if ($(this).hasClass('invalid')){
				valid = false;
			}
		});
		return (valid);
	}

	var colorize = function(that, valid){
		if ($(that).attr('type') != 'submit'){
			if (valid){
				$(that).removeClass('invalid').addClass('valid');								
			} else{
				$(that).removeClass('valid').addClass('invalid');
			}
		}
	}

	var validateForm = function(that){
		var field_name = $(that).attr('name');
		var field_value = $(that).val();

		switch (field_name){
			case 'username':
				if (field_value.length <= 2){
					colorize(that, false)
				} else if (field_value.length > 200){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;

			case 'email':
				if (field_value.length <= 0){
					colorize(that, false);
				} else if (validateEmail(field_value)==false){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;

			case 'password':
				if (field_value.length <=8){
					colorize(that, false);
				} else {
					colorize(that, true);
				}
				break;

			case 'password_confirm':
				if (field_value !== $('#psswd').val()){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;

			case 'terms_accepted':
				if (field_value == false){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;

			case 'fav_film':
				if (field_value.length > 100){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;

			case 'fav_show':
				if (field_value.length > 100){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;

			case 'fav_genre':
				if (field_value.length > 100){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;

			case 'about_me':
				if (field_value.length > 1000){
					colorize(that, false);	
				} else {
					colorize(that, true);
				}
				break;
		}
	}

	$('input, textarea').focusout(function(){
		validateForm(this);
	});

	$('input, textarea').keyup(function(event){
		validateForm(this);
	});

});