from urllib.parse import urlparse

# get domain name (returns "example.com" from "name.example.com")
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''

# get sub-domain name (returns "name.example.com" from "https://name.example.com/file1/file2")
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''