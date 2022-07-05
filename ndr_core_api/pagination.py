
def get_page_list(request, current_page, number_of_pages):
    page_list = []

    if current_page <= 5 and number_of_pages >= 10:
        page_range = [str(x) for x in [*range(1, 8)]]
        page_list = page_range + ['...', str(number_of_pages)]
    else:
        if current_page + 4 == number_of_pages and number_of_pages > 5:
            page_range = [str(x) for x in [*range(current_page-2, number_of_pages+1)]]
            page_list = ['1', '...'] + page_range

        else:
            if number_of_pages < 10 and current_page < 10:
                for number in range(number_of_pages):
                    page_list.append(str(number+1))

            else:
                if number_of_pages - 3 <= current_page:
                    page_list = ['1', '...']
                    page_range = [str(x) for x in [*range(number_of_pages - 6, number_of_pages + 1)]]
                    page_list.extend(page_range)

                else:
                    page_range = [str(x) for x in [*range(current_page-2, current_page+3)]]
                    page_list = ['1', '...'] + page_range + ['...', str(number_of_pages)]

    enriched_page_list = list()
    url = request.path + "?"

    for get_param in request.GET:
        if get_param != 'page':
            url += get_param + "=" + request.GET.get(get_param, "") + "&"

    for page in page_list:
        enriched_page_list.append({'page': page, 'url': url + "page=" + page})

    return enriched_page_list

