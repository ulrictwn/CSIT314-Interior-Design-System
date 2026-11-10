PROJECT_FIELDS = ['projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description']


def project_values(project):
    """Prepare the project fields used by HTML and JSON displays."""
    return dict(projectId=project.project_id, accountId=project.account_id,
        projectName=project.project_name, categoryId=project.category_id,
        propertyType=project.property_type, area=project.area,
        renovationCost=project.renovation_cost, description=project.description,
        status=project.project_status)
