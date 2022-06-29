from ndr_core_api.views import AdvancedSearchView


class MyAdvancedSearchView(AdvancedSearchView):
    template_name = 'main/advanced_search.html'
    endpoint = "chapters"

    def transform_result(self, hit):
        pass
        # hit["transcription"] = "Dummy Text"
