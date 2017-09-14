$(document).ready(function(){

	var form_valid = function(){
		var valid = true;
		$('input, .dropdown_input').each(function(){
			if ($(this).hasClass('invalid')){
				valid = false;
			}
		});
		return (valid);
	}

	var validateField = function(that){
		$(that).removeClass('invalid').addClass('valid');
		$('#title_rule').removeClass('invalid').addClass('valid');
		$('#genre_rule').removeClass('invalid').addClass('valid');

		var field_name = $(that).attr('name');
		var field_value = $(that).val();

		switch(field_name){
			case 'title':
				if ((field_value.length < 1) || (field_value.length >= 500)){
					$(that).removeClass('valid').addClass('invalid');
					$('#title_rule').removeClass('valid').addClass('invalid');
				}
				break;
			case 'genre_tags':
				if ((field_value.length < 0) || (field_value.length >= 500)){
					$(that).removeClass('valid').addClass('invalid');
					$('#genre_rule').removeClass('valid').addClass('invalid');
				}
				break;
		}
	}

	$('input, .dropdown_input').focusout(function(){
		validateField(this);
	});

	$('input').keyup(function(event){
		validateField(this);
	});

});