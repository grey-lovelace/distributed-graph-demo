"""Prepares the Hive schema registry for the demo.

The script runs once each time the stack starts. It does the steps that a person
would otherwise do by hand in the Hive web app:

1. It signs in as the demo user. It creates the user first if the user does not exist.
2. It creates the "conference" organization if it does not exist.
3. It creates the "conference-platform" project if it does not exist.
   The project type is FEDERATION. Hive creates the production, staging and development targets.
4. It creates an access token that can publish schemas, check schemas and report usage.
5. It creates a CDN access token. The router uses it to download the supergraph.

It writes the tokens to /hive-tokens/hive.env. The publish containers and the router read that file.
The script uses only the Python standard library.
"""

import json
import urllib.request
from datetime import datetime, timezone
from http.cookies import SimpleCookie

HIVE_URL = "http://server:3001"

EMAIL = "demo@conference.local"
PASSWORD = "Conference-demo-2026!"

ORGANIZATION = "conference"
PROJECT = "conference-platform"
TARGET = "production"

OUTPUT_FILE = "/hive-tokens/hive.env"

# Hive puts the session in a cookie named sAccessToken when the user signs in.
# The cookie is marked Secure, so Python's cookie jar would not send it over plain HTTP.
# The script stores the cookie here and sends it with every request instead.
session_cookie = ""


def post(path, body):
    global session_cookie
    request = urllib.request.Request(
        HIVE_URL + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "cookie": session_cookie},
    )
    with urllib.request.urlopen(request) as response:
        for header in response.headers.get_all("set-cookie") or []:
            cookie = SimpleCookie(header)
            if "sAccessToken" in cookie:
                session_cookie = f"sAccessToken={cookie['sAccessToken'].value}"
        return json.load(response)


def graphql(query, variables=None):
    result = post("/graphql", {"query": query, "variables": variables or {}})
    if result.get("errors"):
        raise RuntimeError(result["errors"])
    return result["data"]


def sign_in():
    form = {"formFields": [{"id": "email", "value": EMAIL}, {"id": "password", "value": PASSWORD}]}
    if post("/auth-api/signin", form)["status"] == "OK":
        print(f"Signed in as {EMAIL}")
        return
    result = post("/auth-api/signup", form)
    if result["status"] != "OK":
        raise RuntimeError(f"Could not create the demo user: {result}")
    print(f"Created the user {EMAIL}")


def ensure_organization():
    # Hive returns a permission error for an organization that does not exist,
    # so the script looks for the slug in the user's own organizations instead.
    data = graphql("{ organizations { nodes { slug } } }")
    if any(organization["slug"] == ORGANIZATION for organization in data["organizations"]["nodes"]):
        return
    result = graphql(
        "mutation ($slug: String!) { createOrganization(input: { slug: $slug }) { error { message } } }",
        {"slug": ORGANIZATION},
    )["createOrganization"]
    if result["error"]:
        raise RuntimeError(result["error"]["message"])
    print(f"Created the organization {ORGANIZATION}")


def ensure_project():
    data = graphql(
        """query ($organization: String!, $project: String!) {
          organization(reference: { bySelector: { organizationSlug: $organization } }) {
            projectBySlug(projectSlug: $project) { id }
          }
        }""",
        {"organization": ORGANIZATION, "project": PROJECT},
    )
    if data["organization"]["projectBySlug"]:
        return
    result = graphql(
        """mutation ($organization: String!, $project: String!) {
          createProject(input: {
            organization: { bySelector: { organizationSlug: $organization } }
            slug: $project
            type: FEDERATION
          }) { error { message } }
        }""",
        {"organization": ORGANIZATION, "project": PROJECT},
    )["createProject"]
    if result["error"]:
        raise RuntimeError(result["error"]["message"])
    print(f"Created the Federation project {PROJECT}")


def get_target_id():
    data = graphql(
        """query ($organization: String!, $project: String!, $target: String!) {
          target(reference: { bySelector: {
            organizationSlug: $organization, projectSlug: $project, targetSlug: $target
          } }) { id }
        }""",
        {"organization": ORGANIZATION, "project": PROJECT, "target": TARGET},
    )
    return data["target"]["id"]


def create_access_token():
    """Creates a token for the Hive CLI and for the router's usage reports."""
    # A token title can only contain letters, numbers, spaces, "_" and "-".
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H-%M-%S")
    result = graphql(
        """mutation ($organization: String!, $title: String!) {
          createOrganizationAccessToken(input: {
            organization: { bySelector: { organizationSlug: $organization } }
            title: $title
            permissions: ["project:describe", "schemaCheck:create", "schemaVersion:publish", "usage:report"]
            resources: { mode: ALL }
          }) { ok { privateAccessKey } error { message details { title } } }
        }""",
        {"organization": ORGANIZATION, "title": f"demo token {created_at}"},
    )["createOrganizationAccessToken"]
    if result["error"]:
        raise RuntimeError(result["error"])
    return result["ok"]["privateAccessKey"]


def create_cdn_access_token():
    """Creates a token that lets the router download the supergraph."""
    result = graphql(
        """mutation ($organization: String!, $project: String!, $target: String!) {
          createCdnAccessToken(input: {
            target: { bySelector: { organizationSlug: $organization, projectSlug: $project, targetSlug: $target } }
            alias: "router"
          }) { ok { secretAccessToken } error { message } }
        }""",
        {"organization": ORGANIZATION, "project": PROJECT, "target": TARGET},
    )["createCdnAccessToken"]
    if result["error"]:
        raise RuntimeError(result["error"]["message"])
    return result["ok"]["secretAccessToken"]


def main():
    sign_in()
    ensure_organization()
    ensure_project()
    target_id = get_target_id()

    # The router, the Hive CLI and the Hive router plugin all read these variables.
    settings = {
        "HIVE_REGISTRY_ENDPOINT": f"{HIVE_URL}/graphql",
        "HIVE_TARGET_ID": f"{ORGANIZATION}/{PROJECT}/{TARGET}",
        "HIVE_TOKEN": create_access_token(),
        "HIVE_ENDPOINT": "http://usage:3006",
        "HIVE_CDN_ENDPOINT": f"{HIVE_URL}/artifacts/v1/{target_id}",
        "HIVE_CDN_KEY": create_cdn_access_token(),
    }
    with open(OUTPUT_FILE, "w") as file:
        for name, value in settings.items():
            file.write(f"export {name}='{value}'\n")
    print(f"Wrote the Hive tokens to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
