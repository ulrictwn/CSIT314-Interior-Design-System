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


def dashboard_endpoint(account):
    """Choose the dashboard associated with the saved profile name."""
    return {'interior designer':'designer_dashboard', 'customer':'customer_dashboard',
            'platform manager':'platform_manager_dashboard', 'platform management':'platform_manager_dashboard'}.get(
                account.profile.name.casefold(),'dashboard')
