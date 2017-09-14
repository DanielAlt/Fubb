

""" Helper Functions """
def getCurrentUser(request):
    email = request.authenticated_userid
    return (DBSession.query(User).filter_by(email=email).first())

def parse_genres(genre_string):
    genre_list = []

    if (genre_string):

        while (len(genre_string) > 0):
            hashtag_index = genre_string.find('#')

            if (hashtag_index is not -1):
                genre_string = genre_string[hashtag_index+1:]
                hashtag_index = genre_string.find('#')
        
                if (hashtag_index is not -1):
                    genre_list.append('#' + genre_string[:hashtag_index])
                    genre_string = genre_string[hashtag_index:]
                else:
                    genre_list.append('#' + genre_string)
                    genre_string = '' 
            else:
                genre_string = ''

    return (genre_list)

def parseIndexArgs(kargs):
    kargs = kargs[kargs.find('?')+1:]
    kargs = kargs.split('&')
    args = {
        'query': None,
        'orderby': None,
        'order': None,
        'page' : 0, 
        'results': 100,
        'view': 'details'
    }
    for k in kargs:
        k = k.split("=")
        if k[0] in args.keys():
            if not (k[1] == ""):
                args.update({k[0]:k[1]})
    return (args)


def paginate(to_paginate, args):
    pagination_args = args
    try:
        pagination_args['page'] = int(pagination_args['page'])
        pagination_args['results'] = int(pagination_args['results'])    
    except ValueError:
        return False

    to_paginate_size = len(to_paginate)
    number_of_pages = (to_paginate_size/int(pagination_args['results']))
    page_list = [x for x in range(0,number_of_pages+1)]
    lower_bound = pagination_args['page']-2
    upper_bound = pagination_args['page']+3
    upper_bal = number_of_pages-5
    lower_bal = 5

    if ((lower_bound > 0) and (upper_bound <= number_of_pages)):
        page_list = [0] + page_list[lower_bound : upper_bound] + [number_of_pages-1]

    elif ((upper_bal >=0) and (upper_bound >= number_of_pages)):
        page_list = [0] + page_list[upper_bal : number_of_pages]

    elif ((lower_bound <= 0) and (lower_bal <= number_of_pages)):
        page_list = page_list[0:lower_bal] + [number_of_pages-1]

    if ((to_paginate_size - (pagination_args['page']*pagination_args['results'])) > 0):
        to_paginate = to_paginate[pagination_args['page']*pagination_args['results']:(pagination_args['page']*pagination_args['results'])+pagination_args['results']]
    else:
        to_paginate = to_paginate[pagination_args['page']*pagination_args['results']:]

    return dict(
        page_content = to_paginate,
        number_of_pages = number_of_pages,
        current_page = pagination_args['page'],
        next_page = int(pagination_args['page'])+1,
        prev_page = int(pagination_args['page'])-1,
        results= int(pagination_args['results']),
        page_list = page_list
    )

def getRandomTrailer():
    all_embeds = []
    all_movies = DBSession.query(Movie).order_by('embed').all()
    for movie in all_movies:
        if not movie.embed in all_embeds:
            all_embeds.append(movie)
    
    if not (len(all_embeds) == 0):    
        max_embeds = len(all_embeds)
        embed = all_embeds[random.randrange(0,max_embeds)].embed
        return (embed)
    else:
        return "dKrVegVI0Us"
