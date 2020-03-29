from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from entries.models import CompendiumEntry
from search.views.mixins import BasicSearchMixin


class SearchView(View):
    """
    Displays all of the compendium entries that appear as the result of a query.
    """

    default_pagination = 10

    def get(self, request):
        entries = CompendiumEntry.objects.all()

        # Paginate (don't show all of the results on a single page)
        paginator = Paginator(entries, self.default_pagination)
        page_obj = paginator.get_page(request.GET.get("page"))
        page_number = page_obj.number

        context = {
            "page_obj": page_obj,
        }
        return render(request, "entry_list.html", context)
