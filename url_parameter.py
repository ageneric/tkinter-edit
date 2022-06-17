"""Decodes and prints all url query parameters."""
from urllib import parse

def url_parameter(text_data):
    query = parse.parse_qs(parse.urlparse(text_data).query)
    for value in query.values():
        print(parse.unquote(value[0]))
