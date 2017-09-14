$(document).ready(function(){

	// Darwing the Filmstrip
	var filmstrip_array = new Array();

	$('.film_strip').each(function(){
		strip_name = "film_" + $(this).attr('data-film');
		filmstrip_array.push(strip_name);
	});
	
	var drawStrips = function(){
		for (var i=0; i < (filmstrip_array.length); i++){
			var c = document.getElementById(filmstrip_array[i]);
			var ctx = c.getContext("2d");
			var canvas_width = $('#slide_pane').width();
			var canvas_height = $('#slide_pane').height();
			// var message = $("#" + filmstrip_array[i])
			
			$("#" + filmstrip_array[i]).height(canvas_height);

			ctx.fillStyle = "rgb(0,0,0)";
			ctx.fillRect(0,0,canvas_width,canvas_height);
			var square = 10;
			for (var x=0; x<canvas_width; x+=(square+5)){
				ctx.fillStyle = 'rgb(255,255,255)';
				ctx.fillRect(x, 5, square, square);
				ctx.fillRect(x, (canvas_height/2)-square-5, square, square);
			}
			ctx.fillRect(5, square*2, (2*canvas_width)/3, (canvas_height/2) - (square*4));
		}
	}

	drawStrips();
	$(window).resize(drawStrips());

	// Function for Changing Slides in Slideshow
	var slideshow_array = new Array();
	var current_slide = 0;

	$('.slide').each(function(){
		var slidename = $(this).attr('data-slide');
		slideshow_array.push(slidename);
	});

	var switchSlides = function(direction=false){
		// $('.current_slide').removeClass('current_slide').addClass('hidden_slide');
		$('.current_slide').removeClass('current_slide').animate({width:'toggle'},350, function(){
			switch(direction){
				case "left":
					current_slide --;
					break;
				case 'right':
					current_slide ++;
					break;
				default:
					current_slide ++;
					break;
			}

			if (current_slide > (slideshow_array.length-1)){
				current_slide = 0;
			}
			if (current_slide < 0){
				current_slide = slideshow_array.length-1;
			}
			var slide_id = "#slide_" + slideshow_array[current_slide];
			$(slide_id).addClass('current_slide').animate({width:'toggle'},350);
			// $(slide_id).removeClass('hidden_slide').addClass('current_slide');
		});
	}

	$('.slideshow_handle').click(function(e){
		var direction = $(this).attr('data-direction');
		switchSlides(direction);
	});

	setInterval(switchSlides, 30000);

});