from django.db.models import BooleanField, Count, Exists, OuterRef, Value


def with_star_summary(queryset, user):
    """Return a request-scoped summary without loading star-giver User objects."""
    is_starred = Value(False, output_field=BooleanField())
    if user.is_authenticated:
        relation = queryset.model._meta.get_field('starred_by')
        membership = relation.remote_field.through.objects.filter(**{
            f'{relation.m2m_field_name()}_id': OuterRef('pk'),
            f'{relation.m2m_reverse_field_name()}_id': user.pk,
        })
        is_starred = Exists(membership)

    # Filter "mine" using the Exists annotation, so Count still includes all stars.
    return queryset.annotate(
        _api_star_count=Count('starred_by', distinct=True),
        _api_is_starred=is_starred,
    )
