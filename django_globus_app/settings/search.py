from django_globus_app import fields


def get_rfm(search_result):
    if search_result[0].get("remote_file_manifest"):
        return [search_result[0]["remote_file_manifest"]]
    else:
        return []


SEARCH_INDEXES = {
    "my-search-index": {
        "uuid": "4dcf50b9-14e7-4994-be36-6c6b11a73cd2",
        "name": "My Search Index",
        "fields": [
            ("dc", fields.dc),
            ("title", fields.title),
            ("formatted_search_results", fields.formatted_search_results),
            ("formatted_files", fields.formatted_files),
        ],
        "facets": [
            {
                "name": "Publisher",
                "field_name": "dc.publisher",
                "size": 10,
                "type": "terms",
            },
            {
                "name": "Type",
                "field_name": "dc.subjects.subject",
                "size": 10,
                "type": "terms",
            },
            {"name": "Type", "field_name": "dc.formats", "size": 10, "type": "terms"},
            {
                "name": "File Size (Bytes)",
                "type": "numeric_histogram",
                "field_name": "files.length",
                "size": 10,
                "histogram_range": {"low": 5000, "high": 10000},
            },
            {
                "name": "Dates",
                "field_name": "dc.dates.date",
                "type": "date_histogram",
                "date_interval": "hour",
            },
        ],
    },
    "perfdata": {
        "name": "Performance Data",
        "uuid": "5e83718e-add0-4f06-a00d-577dc78359bc",
        "fields": [
            "perfdata",
            ("remote_file_manifest", get_rfm),
            (
                "globus_http_endpoint",
                lambda x: "b4eab318-fc86-11e7-a5a9-0a448319c2f8.petrel.host",
            ),
            ("globus_http_scope", lambda x: "petrel_https_server"),
            (
                "globus_http_path",
                lambda x: x[0]["remote_file_manifest"]["url"].split(":")[2],
            ),
        ],
        "facets": [
            {
                "name": "Subject",
                "field_name": "perfdata.subjects.value",
                "size": 10,
                "type": "terms",
            },
            {
                "name": "Publication Year",
                "field_name": "perfdata.publication_year.value",
            },
            {
                "name": "File Size (Bytes)",
                "type": "numeric_histogram",
                "field_name": "remote_file_manifest.length",
                "size": 10,
                "histogram_range": {"low": 15000, "high": 30000},
            },
            {
                "name": "Dates",
                "field_name": "perfdata.dates.value",
                "type": "date_histogram",
                "date_interval": "month",
            },
        ],
        "filter_match": "match-all",
        "template_override_dir": "perfdata",
        "test_index": True,
    },
}
