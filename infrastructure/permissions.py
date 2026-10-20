"""Permission values stored by profiles. Only stories 1–12 are implemented here."""

PERMISSION_OPTIONS = {
    'profile.create': 'Create user profiles',
    'profile.view': 'View user profiles',
    'profile.update': 'Update user profiles',
    'profile.suspend': 'Suspend user profiles',
    'profile.search': 'Search user profiles',
    'account.create': 'Create user accounts',
    'account.view': 'View user accounts',
    'account.update': 'Update user accounts',
    'account.suspend': 'Suspend user accounts',
    'account.search': 'Search user accounts',
    'company.create': 'Create own company information',
    'company.view': 'View own company information',
    'company.update': 'Update own company information',
    'company.delete': 'Delete own company information',
    'company.search': 'Search own company information',
    'project.create': 'Create own current and past projects',
    'project.view': 'View own current and past projects',
    'project.update': 'Update own current and past projects',
    'project.delete': 'Delete own current and past projects',
    'project.search': 'Search own current and past projects',
    'project.browse': 'Search and view published design projects',
    'shortlist.save': 'Save projects to own shortlist',
    'shortlist.view': 'View own shortlisted projects',
    'shortlist.search': 'Search own shortlist',
    'interest.views': 'View own project view counts',
    'interest.shortlists': 'View own project shortlist counts',
    'category.create': 'Create project categories',
    'category.view': 'View project categories',
    'category.update': 'Update project categories',
    'category.delete': 'Delete project categories',
    'category.search': 'Search project categories',
    'report.daily': 'Generate daily platform reports',
    'report.weekly': 'Generate weekly platform reports',
    'report.monthly': 'Generate monthly platform reports',
}

ADMIN_PERMISSIONS = {code for code in PERMISSION_OPTIONS if code.startswith(('profile.', 'account.'))}
DEFAULT_PROFILES = {
    'User Admin': sorted(ADMIN_PERMISSIONS),
    'Customer': ['project.browse', 'shortlist.save', 'shortlist.view', 'shortlist.search'],
    'Interior Designer': [code for code in PERMISSION_OPTIONS if code.startswith(('company.', 'interest.'))
                         or code.startswith('project.') and code != 'project.browse'],
    'Platform Management': [code for code in PERMISSION_OPTIONS if code.startswith(('category.', 'report.'))],
}
