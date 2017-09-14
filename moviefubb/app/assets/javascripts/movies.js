$(document).ready(function(){

	$('.poster_img').each(function(){
		if (
			($(this).attr('src') === '') ||
			!(this.hasAttribute('src'))
		){
			$(this).attr('src', '/static/images/movie_posters/default_poster.png');
		}
	});

	$('.edit_opt').click(function(event){
		edittab = "#editslab_"  + $(this).attr('data-mid');

		clearDialogEdit();		
		$(edittab).removeClass('invisible').addClass('popup_dlg');

		var offset_x = ($(window).width() - $('.popup_dlg').width())/2
		var offset_y = ($(window).height() - $('.popup_dlg').height())/2;
		$('.popup_dlg').css({'left': offset_x, 'top': offset_y, 'z-index': 16});

		$('.cancel_btn').bind('click', function(){
			clearDialogEdit();		
		});
		$('#backlight_overlay').bind('click', function(e){
			clearDialogEdit();		
		});

		$('#backlight_overlay').fadeIn();
		$(edittab).fadeIn();
	});

	var clearDialogEdit = function(){
		$('.cancel_btn').unbind('click')
		$('.confirm_btn').unbind('click')
		$("#backlight_overlay").fadeOut();
		$('.popup_dlg').fadeOut(1000, function(){
			$(this).removeClass('.popup_dlg').addClass('invisible');
		});
	}

	var grabFilm = function(that){
		return ({
			"title": $(that).attr('data-title'),
			"year": $(that).attr('data-year'),
			"rated": $(that).attr('data-rated'),
			"imdb_rating": $(that).attr('data-imdbRating'),
			"imdb_votes": $(that).attr('data-imdbVotes'),
			"runtime": $(that).attr('data-runtime'),
			"director": $(that).attr('data-director'),
			"writer": $(that).attr('data-writer'),
			"actors": $(that).attr('data-actors'),
			"country": $(that).attr('data-country'),
			'awards': $(that).attr('data-awards'),
			"language": $(that).attr('data-language'), 
			"embed": $(that).attr('data-embed'), 
			"poster": $(that).attr('data-poster'),
			"imdb_id": $(that).attr('data-imdb'),
			"plot": $(that).html()
		})
	}

	$('#downloadCollection_btn').click(function(e){
		// $(this)

		var popup_box = (
			"<div id='download_menu_dlg' class='popup_dlg'>" +
				"<div class='popup_title'>Download Your Collection</div><br />" +
				"<table><tbody><tr><td>Select a Filetype</td><td><select id='dl_filetype' class='dropdown_input'>" +
				"<option value='xml'>XML</option></select></td></tr>" + 
				"</tr></tbody></table><br /><br />" + 
				"<a id='dl_link' href='' download=''></a><br/>" +
				"<input type='button' class='confirm_btn' id='fdownload_btn' value='Generate File' />"  + 
				"<input class='cancel_btn' type='button' download='' id='cancel_delete_btn' value='Cancel' /></div>"
		);
		$('body').append(popup_box);
		var offset_x = ($(window).width() - $('.popup_dlg').width())/2
		var offset_y = ($(window).height() - $('.popup_dlg').height())/2;

		$('.popup_dlg').css({'left': offset_x, 'top': offset_y});

		$('.cancel_btn').bind('click', function(){
			clearDialog('#download_menu_dlg');
		});

		$("#fdownload_btn").bind('click', function(){

			var film_list = [];
			var file_type = $("#dl_filetype").val();
			
			$('.movie_data').each(function(){
				film_list.push(grabFilm(this));
			});
			switch(file_type){
				case "xml":
					var xml = '<?xml version="1.0" encoding="utf-8"?>\n<collection>\n'
					for (var i=0; i < film_list.length; i++){
						xml += "\t<movie>\n" ;
						xml += '\t\t<title>' + film_list[i].title + "</title>\n";
						xml += '\t\t<year>' + film_list[i].year + "</year>\n";
						xml += '\t\t<rated>' + film_list[i].rated + "</rated>\n";
						xml += '\t\t<imdbRating>' + film_list[i].imdb_rating + "</imdbRating>\n";
						xml += '\t\t<imdbVotes>' + film_list[i].imdb_votes + "</imdbVotes>\n";
						xml += '\t\t<runtime>' + film_list[i].runtime + "</runtime>\n";
						xml += '\t\t<director>' + film_list[i].director + "</director>\n";
						xml += '\t\t<writer>' + film_list[i].writer + "</writer>\n";
						xml += '\t\t<actors>' + film_list[i].actors + "</actors>\n";
						xml += '\t\t<country>' + film_list[i].country + "</country>\n";
						xml += '\t\t<awards>' + film_list[i].awards + "</awards>\n";
						xml += '\t\t<language>' + film_list[i].language + "</language>\n";
						xml += '\t\t<embed>' + film_list[i].embed + "</embed>\n";
						xml += '\t\t<poster>' + film_list[i].poster + "</poster>\n";
						xml += '\t\t<imdbId>' + film_list[i].imdbId + "</imdbId>\n";
						xml += '\t\t<plot>' + film_list[i].plot + "</plot>\n";
						xml += "\t</movie>\n";
					}
					xml += "</collection>";

				    $("#dl_link").attr('download', 'collection.xml');
					// $("#dl_link").attr('href',  encodeURIComponent('data:Application/octet-stream,' + xml));
					$('#dl_link').html('Click Here to Download XML');
					break;
			}
		});

		$('#backlight_overlay').bind('click', function(e){
			clearDialog('#download_menu_dlg');		
		});

		$('#backlight_overlay').fadeIn();
		$('#download_menu_dlg').fadeIn();
	});

	$('#share_btn').click(function(e){
		var page_url = $(this).attr('data-embedUrl');
		var popup_box = (
			"<div id='share_menu_dlg' class='popup_dlg'>" +
				"<div class='popup_title'>Share this Collection</div><br />" +
				"<table><tbody><tr><td>" +
				"Embed</td><td><input class='text_input' type='text' value='"  +
					'<iframe src="' + page_url + '"' + ' width="500" height="400"></iframe>' + "' /></td></tr>" +
				"<tr><td>" +
				"URL</td><td><input type='text' class='text_input' value='" + page_url +  "' /></td></tr></tbody></table><br />" + 
			"<span>Please make sure to update your privacy settings, such that your collection is visible to anyone</span><br /><br />"+
			"<input class='cancel_btn' type='button' id='cancel_delete_btn' value='Cancel' /></div>"
		);
		$('body').append(popup_box);
		var offset_x = ($(window).width() - $('.popup_dlg').width())/2
		var offset_y = ($(window).height() - $('.popup_dlg').height())/2;

		$('.popup_dlg').css({'left': offset_x, 'top': offset_y});

		$('.cancel_btn').bind('click', function(){
			clearDialog("#share_menu_dlg");
		});

		$('#backlight_overlay').bind('click', function(e){
			clearDialog("#share_menu_dlg");		
		});
		$('#backlight_overlay').fadeIn();
		$("#share_menu_dlg").fadeIn();
	});

	$('.delete_btn').click(function(e){
		var movie_title = $(this).attr('data-mtitle');
		var delete_url = $(this).attr('data-deleteUrl');
		var popup_box = (
			"<div id='delete_movie_menu' class='popup_dlg'><div class='popup_title'>Confirm Destructive Action</div><br />" +
			"<span>Are you sure you want to permanently delete <b>" + movie_title + "</b>?</span><br /><br />" +
			"<input class='confirm_btn' type='button' id='confirm_delete_btn' value='Delete' />" +
			"<input class='cancel_btn' type='button' id='cancel_delete_btn' value='Cancel' /></div>"
		);
		$('body').append(popup_box);
		var offset_x = ($(window).width() - $('.popup_dlg').width())/2
		var offset_y = ($(window).height() - $('.popup_dlg').height())/2;

		$('.popup_dlg').css({'left': offset_x, 'top': offset_y});

		$('.cancel_btn').bind('click', function(){
			clearDialog("#delete_movie_menu");
		});
		$('.confirm_btn').bind('click', function(){
			deleteEntry(delete_url);
		});
		$('#backlight_overlay').bind('click', function(e){
			clearDialog("#delete_movie_menu");		
		});

		$('#backlight_overlay').fadeIn();
		$("#delete_movie_menu").fadeIn();
	});

	var clearDialog = function(dlgid){
		$('.cancel_btn').unbind('click');
		$('.confirm_btn').unbind('click');
		$("#backlight_overlay").unbind('click').fadeOut();
		$(dlgid).fadeOut(function(){
			$(this).remove();
		});
	}

	var deleteEntry = function(delete_url){
		window.location.href = delete_url;
	}

});