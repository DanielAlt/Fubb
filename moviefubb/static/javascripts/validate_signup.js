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

	var validateForm = function(that){
		var field_name = $(that).attr('name');
		var field_value = $(that).val();

		$(that).removeClass('invalid').addClass('valid');
		switch (field_name){

			case 'username':
				if (field_value.length <= 0){
					$(that).removeClass('valid').addClass('invalid');
				}
				if (field_value.length > 200){
					$(that).removeClass('valid').addClass('invalid');
				}
				break;

			case 'email':
				if (field_value.length <= 0){
					$(that).removeClass('valid').addClass('invalid');
				}
				if (validateEmail(field_value)==false){
					$(that).removeClass('valid').addClass('invalid');	
				}
				break;

			case 'password':
				if (field_value.length <=8){
					$(that).removeClass('valid').addClass('invalid');	
				}
				break;

			case 'password_confirm':
				if (field_value !== $('#psswd').val()){
					$(that).removeClass('valid').addClass('invalid');	
				}
				break;

			case 'terms_accepted':
				if (field_value == false){
					$(that).removeClass('valid').addClass('invalid');	
				}
				break;
		}
		if (form_valid()){
			$('.submit_btn').removeAttr('disabled');
		}
	}

	$('input').focusout(function(){
		validateForm(this);
	});

	$('input').keyup(function(event){
		validateForm(this);
	});

});