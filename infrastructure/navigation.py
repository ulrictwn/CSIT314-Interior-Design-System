def navigation():
    groups = [dict(title='Workspace', links=[dict(label='Dashboard', endpoint='dashboard', arguments={})])]
    for label, singular, plural in [('User Profiles', 'user_profile', 'user_profiles'),
                                    ('User Accounts', 'user_account', 'user_accounts')]:
        groups.append(dict(title=label, links=[
            dict(label='Create '+label, endpoint='create_'+singular, arguments={}),
            dict(label='Update '+label, endpoint=plural, arguments={'mode': 'update'}),
            dict(label='Suspend '+label, endpoint=plural, arguments={'mode': 'suspend'}),
            dict(label='Search '+label, endpoint='search_'+plural, arguments={}),
        ]))
    return groups
