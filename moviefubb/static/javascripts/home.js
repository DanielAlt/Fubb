$(document).ready(function(){
	
	$('.poster_img').each(function(){
		if ($(this).attr('src') === ''){
			$(this).attr('src', '/static/images/movie_posters/default_poster.png')
		}
	});
	
	$("body").on("contextmenu", "img", function(e) {
	  return false;
	});
	$('#logo').on('dragstart', function(event) { event.preventDefault(); });
});