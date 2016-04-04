$(document).ready(function(){

	var switchTab = function(tab){
		$('.tabpage').each(function(){
			$(this).removeClass('tabpage_active').addClass('tabpage_hidden');
		});
		$(tab).removeClass('tabpage_hidden').addClass('tabpage_active');
	}
	$('.stats_tabbar_btn').click(function(e){
		var tab = '#tabpage_' + $(this).attr('data-tab');
		switchTab(tab);
	});

	// Functions for Downloading Images
	$('#download_genre_stats').click(function(event){
		$(this).attr('href', document.getElementById('genres_screen').toDataURL());
	    $(this).attr('download', 'genre_stats.png');
	});

	$('#download_format_stats').click(function(event){
		$(this).attr('href', document.getElementById('formats_screen').toDataURL());
	    $(this).attr('download', 'format_stats.png');
	});

	$('#download_year_stats').click(function(event){
		$(this).attr('href', document.getElementById('years_screen').toDataURL());
	    $(this).attr('download', 'year_stats.png');
	});

	// Function to Draw a Single Graph
	var drawGraph = function(pie_type){
		var total_films = $('#collection_size').html();
		var color_options = [
			'rgb(255,0,0)',
			'rgb(0,255,0)',
			'rgb(0,0,255)',
			'rgb(255,100,0)',
			'rgb(255,100,100)',
			'rgb(100,255,100)',
			'rgb(100,255,255)',
			'rgb(50,50,50)'
		];

		// Initialize Genre Canvas Viewport	
		c = document.getElementById(pie_type + '_screen');
		ctx = c.getContext('2d');
		port_width = $('#genres_screen').width();
		port_height = $('#genres_screen').height();
		port_min = Math.min(port_width, port_height);
		$('#'+ pie_type +'_screen').attr('width', port_width).attr('height', port_height);

		// Create Key Value Object Containing Genres and Percentages
		var genre_dict = {};
		var genre_keys = [];
		$('.' + pie_type + '_pair').each(function(){
			var key = $(this).children().html();
			var value = $(this).children().next().html();
			value = (value/total_films);
			genre_keys.push(key);
			genre_dict[key] = value;
		});

		// Draw to The Canvas
		ctx.fillStyle = 'rgb(0,0,0)';
		ctx.fillRect(0,0,port_width, port_height);

		bg_img = new Image();
		bg_img.src = '/static/images/wallpapers/watermark.png';
		ctx.drawImage(bg_img, port_width-200, port_height-165);

		ctx.strokeStyle = 'rgb(255,255,255)';
		ctx.beginPath();
		ctx.arc(port_width/3, port_height/2, (port_min/3) + 2, 0, 2*Math.PI);
		ctx.stroke();

		var current_angle = 0;
		var current_legend_y = 50;
		var current_legend_x = 1.5*(port_width/3) + 25;
		
		for (var i=0; i < genre_keys.length; i++){
			var key = genre_keys[i];
			var value = genre_dict[key];

			var init_pos_x = port_width/3;
			var init_pos_y = port_height/2;
			var first_pos_x = init_pos_x + ( Math.cos( current_angle*(Math.PI/180) ) * (port_min/3) );
			var first_pos_y = init_pos_y + ( Math.sin(current_angle*(Math.PI/180)) * (port_min/3) );

			var new_angle = current_angle + (value*360);

			var second_pos_x = init_pos_x + ( Math.cos(new_angle*(Math.PI/180)) * (port_min/3) );
			var second_pos_y = init_pos_y + ( Math.sin(new_angle*(Math.PI/180)) * (port_min/3) );
		
			// PIE WEDGE
			ctx.strokeStyle = 'rgb(255,255,255)';
			ctx.fillStyle = color_options[i];
			ctx.beginPath();			
			ctx.moveTo(init_pos_x, init_pos_y);
			ctx.lineTo(first_pos_x, first_pos_y);
			ctx.arc(init_pos_x, init_pos_y, (port_min/3), current_angle*(Math.PI/180), new_angle*(Math.PI/180));
			ctx.lineTo(second_pos_x, second_pos_y);
			ctx.stroke();
			ctx.fill();
			current_angle = new_angle;

			// LEGEND
			ctx.fillRect(current_legend_x, current_legend_y, 20, 20);
			ctx.font = '12px bd_cartoon';
			ctx.fillText(key, current_legend_x+25, current_legend_y+15);
			current_legend_y += 25;
		}

	}

	var drawGraphs = function(){
		drawGraph('genres');
		drawGraph('formats');
		drawGraph('years');	
	}
	
	$(window).resize(drawGraphs());

});