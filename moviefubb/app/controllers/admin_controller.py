@view_config(
    route_name='admin_analytics',
    renderer='templates/admin/analytics.pt',
    permission='admin'
)

def admin_analytics(request):
    current_user = getCurrentUser(request)

    pages = DBSession.query(Page).order_by('page_url').all()
    page_args = parseIndexArgs(request.url)
    pagination = paginate(pages, page_args)

    total_hits = 0
    fav_agent_nums = {}
    for page in pages:
        total_hits += len(page.myhits)
        for hit in page.myhits:
            if hit.user_agent in fav_agent_nums.keys():
                fav_agent_nums[hit.user_agent] += 1
            else:
                fav_agent_nums.update({hit.user_agent: 1})

    fav_agent = ['', 0]
    for agent in fav_agent_nums.keys():
        if (fav_agent_nums[agent] >= fav_agent[1]):
            fav_agent = [agent, fav_agent_nums[agent]]

    return dict(
        request=request,
        total_hits=total_hits,
        fav_agent=fav_agent,
        pagination=pagination,
        page_args=page_args,
        pages= pagination["page_content"],
        datetime=datetime.datetime.today(),
        logged_in=request.authenticated_userid,
        current_user=current_user,
    )    