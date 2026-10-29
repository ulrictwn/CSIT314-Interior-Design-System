def navigation(actor):
    if actor is None:
        return []
    groups = [dict(title='Workspace', links=[dict(label='Dashboard', endpoint='dashboard', arguments={})])]
    for label, prefix, singular, plural in [('User Profiles', 'profile', 'user_profile', 'user_profiles'),
                                           ('User Accounts', 'account', 'user_account', 'user_accounts')]:
        links = []
        for title, endpoint, arguments, permission in [
            ('Create '+label, 'create_'+singular, {}, prefix+'.create'),
            ('Update '+label, plural, {'mode':'update'}, prefix+'.update'),
            ('Suspend '+label, plural, {'mode':'suspend'}, prefix+'.suspend'),
            ('Search '+label, 'search_'+plural, {}, prefix+'.search')]:
            if actor.has_permission(permission):
                links.append(dict(label=title, endpoint=endpoint, arguments=arguments))
        if links:
            groups.append(dict(title=label, links=links))
    return groups
