# coding=utf-8
import re
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from flask import Flask, jsonify, request


# *The* app object
app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = 'https://api.github.com/users/{username}/gists'.format(
            username=username)
    response = requests.get(gists_url)
    # BONUS: What failures could happen?
    # BONUS: Paging? How does this work for users with tons of gists? If truncated key is true then the file is too large and some part of the content is returned.
    #                If the top level trunated key is true then 300 file will be returned. In order to get all the files you have copy the gist via "git_pull_url"

    return response.json()


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()
    # BONUS: Validate the arguments?
    username = post_data['username']
    valid = re.match('^[\w-]+$', username)
    if valid is None:
        print("not passed")
    pattern = post_data['pattern']

    result = {}
    gists = gists_for_user(username)
    # BONUS: Handle invalid users?
    pattern_check = False
    matches = []
    status_check = 'failure'
    for gist in gists:
        pattern_check = False
        gists_url = 'https://api.github.com/gists/{gist_id}'.format(gist_id=gist['id'])
        response = requests.get(gists_url)
        response = response.json()

        for key, value in response['files'].iteritems():
            prog = re.compile(pattern)
            found = prog.search(value['content'])
            if(found):
                pattern_check = True
                status_check = 'success'
                break
        if(pattern_check):
            matches.append('https://gist.github.com/' + username + '/' + gist['id'])
        # REQUIRED: Fetch each gist and check for the pattern
        # BONUS: What about huge gists?
        # BONUS: Can we cache results in a datastore/db?
        pass

    result['status'] = status_check
    result['username'] = username
    result['pattern'] = pattern
    result['matches'] = matches

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
