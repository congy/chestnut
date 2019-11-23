const JSON_MODEL = {
    0: {
        'table': ['tracker'],
        'type': 'BasicArray',
        'value': {
            'fields': ['id', 'name', 'is_in_chlog', 'position', 'is_in_roadmap', 'default_status_id'],
            'nested': [{
                'table': ['tracker', 'projects'],
                'type': 'BasicArray',
                'association': {
                    'leftTable': 'project',
                    'rightFkField': 'tracker_id',
                    'assocType': 'many_to_many',
                    'leftFkField': 'project_id',
                    'rightTable': 'tracker',
                    'table': 'projects_trackers'
                },
                'value': {
                    'fields': [
                        'id', 'status', 'lft', 'rgt', 'name', 'description', 'homepage', 'is_public', 'parent_id',
                        'created_on', 'updated_on', 'inherit_members', 'default_version_id', 'default_assigned_to_id'
                    ],
                    'nested': [{
                        'keys': [],
                        'value': {
                            'fields': ['id'],
                            'nested': []
                        },
                        'table': ['projects', 'enabled_modules'],
                        'type': 'Index',
                        'id': 0,
                        'condition': "name == 'issue_tracking'"
                    }]
                }
            },
            {
                'table': ['tracker', 'issues'],
                'type': 'BasicArray',
                'association': {
                    'assocType': 'one_to_many',
                    'leftTable': 'tracker',
                    'rightFkField': 'tracker_id',
                    'rightTable': 'issue',
                    'leftFkField': 'issues_id'
                },
                'value': {
                    'fields': [
                        'id', 'subject', 'description', 'due_date', 'assigned_to_id', 'created_on', 'updated_on',
                        'start_date', 'done_ratio', 'estimated_hours', 'parent_id', 'root_id', 'lft', 'rgt',
                        'is_private', 'closed_on', 'author_id', 'priority_id', 'project_id', 'tracker_id', 'status_id'
                    ],
                    'nested': [{
                        'table': ['issues', 'status'],
                        'type': 'BasicArray',
                        'association': {
                            'assocType': 'one_to_many',
                            'leftTable': 'issue_status',
                            'rightFkField': 'status_id',
                            'rightTable': 'issue',
                            'leftFkField': 'issues_id'
                        },
                        'value': {
                            'fields': ['id', 'is_closed'],
                            'nested': []
                        }
                    }]
                }
            }]
        }
    }
};
