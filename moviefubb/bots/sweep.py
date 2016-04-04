import imdb_bot, omdb_bot, magnet_bot, trailer_bot, poster_bot, os

def botSweep(**kwargs):
    omdb_dict, imdb_id, embed = (None, None, None)
    keyword_args = dict(title= None, imdbID= None, embed= None)
    _here = os.path.join(os.getcwd(), 'moviefubb')
    print "Initializing Bot Sweep Varirables."

    for arg in kwargs.keys():
        if (arg in keyword_args.keys()):
            keyword_args.update({arg: kwargs[arg]})
    print "Configuring Bot Settings."


    """ Movie Lookup Based on Title"""

    if (keyword_args['title'] is not None):

        print "\n\nInitializing Info Lookup using Title Provided"
        omdb_dict = omdb_bot.LookupHandler(title=keyword_args['title']).run()

        try:
            imdb_id = omdb_dict['imdbID']
            print "Found Info"
            print "------------------- Movie Info------------------------"
            for k in omdb_dict.keys():
                print "\t %s.........................%s" % (k, omdb_dict[k])
            print "------------------- Movie Info------------------------"


        except KeyError:
            print "Did Not Find IMDB ID trying Secondary Lookup"
            imdb_id = imdb_bot.LookupHandler(keyword_args['title']).run()
            if imdb_id is not None:
                omdb_dict = omdb_bot.LookupHandler(imdbID=imdb_id).run()
                print "------------------- Movie Info------------------------"
                for k in omdb_dict.keys():
                    print "\t %s.........................%s" % (k, omdb_dict[k])
                print "------------------- Movie Info------------------------"
            else:
                omdb_dict = {
                    'Title': keyword_args['title'],
                    'Year': 0000,
                    'Rated': 'N/A',
                    'Runtime': 'N/A',
                    'Director': 'N/A',
                    'Writer': 'N/A',
                    'Actors': 'N/A',
                    'Plot': 'N/A',
                    'Country': 'N/A',
                    'Awards': 'N/A',
                    'imdbRating': 'N/A',
                    'imdbVotes': 'N/A',
                    'Language': 'N/A',
                }


    """ Movie Lookup Based on IMDB ID"""
    if (keyword_args['imdbID'] is not None):
        print "Initializing Info Lookup Based on IMDB ID"
        imdb_id = keyword_args['imdbID']
        omdb_dict = omdb_bot.LookupHandler(imdbID=imdb_id).run()

    """ Movie Trailer Lookup """
    if ((keyword_args['embed'] is None) and (omdb_dict is not None)):
        print 'Initializing Trailer Lookup'
        try:
            embed = trailer_bot.LookupHandler(omdb_dict['Title']).run()
        except KeyError:
            embed = None

    """ When the lookup is successful """
    if ((imdb_id is not None) and (omdb_dict is not None)):

        poster = ''

        if not (omdb_dict['Poster'] == 'N/A'):
    
            """ Saving Poster To Filesystem """
            print "Initializing Poster Bot"
            filename = os.path.join(_here, 'uploads', omdb_dict["imdbID"] + '.jpg')
    
            if not os.path.exists(filename):
                poster = poster_bot.LookupHandler(omdb_dict['Poster']).run()            
                # Might insert Try Except Here
                with open(filename, 'w') as f:
                    f.write(poster)
                    f.close()

            poster = '/uploads/' + imdb_id + ".jpg"
        
        magnet = "Magnet Bot is Disabled"
        #magnet = magnet_bot.LookupHandler(title).run()

        return ({
            'title': omdb_dict['Title'],
            'Year': omdb_dict['Year'],
            'Rated': omdb_dict['Rated'],
            'Runtime': omdb_dict['Runtime'],
            'Director': omdb_dict['Director'],
            'Writer': omdb_dict['Writer'],
            'Actors': omdb_dict['Actors'],
            'Plot': omdb_dict['Plot'],
            'Country': omdb_dict['Country'],
            'Awards': omdb_dict['Awards'],
            'imdbRating': omdb_dict['imdbRating'],
            'imdbVotes': omdb_dict['imdbVotes'],
            'Language': omdb_dict['Language'],
            'poster': poster,
            "imdbID": imdb_id,
            'magnet': magnet,
            'embed': embed
        })

    else:
        return (None)