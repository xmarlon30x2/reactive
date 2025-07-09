from reactive import component, use_navigation


@component
def TodoNotFound():
    _, params, *_ = use_navigation()

    id = params.get('id', 'unknow')

    return [
        'Todo not found',
        f'Todo ID: {id}',
    ]
