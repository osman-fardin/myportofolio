from django.shortcuts import render

from .models import Experience


def show_main(request):
    context = {
        'name': 'Muhammad Osman Fardin',
        'npm': '2506541723',
        'study_program': 'S1 Ilmu Komputer',
        'bio': (
            'CS student at Universitas Indonesia exploring the cloudy side '
            'of security, while helping guide new programmers through '
            'Programming Foundations 1. Equal parts builder, debugger, and '
            '“wait, let’s trace the code one more time” person.'
        ),
    }

    return render(request, 'index.html', context)


def show_experience(request):
    experiences = Experience.objects.order_by('-started_at')

    context = {
        'experiences': experiences,
    }

    return render(request, 'experience.html', context)
